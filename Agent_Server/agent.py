"""
Deep Agent + FastAPI + llama.cpp
配合前端格式：
  - POST /chat   multipart/form-data (text, thread_id, files)
  - POST /approve multipart/form-data (thread_id)
  SSE 格式：data: {"choices":[{"delta":{"content":"..."}}]}
            data: {"interrupt": true, "calls": [...]}
            data: [DONE]
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

# ─── 設定區 ────────────────────────────────────────────────
LLAMA_URL   = os.getenv("LLAMA_URL",   "http://localhost:8080/v1")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "local-model")
PORT        = int(os.getenv("PORT", 8001))
WORKSPACE   = os.getenv("WORKSPACE",   "/opt/Shrimp-LMM-Agent-Rag/data")
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "/opt/Shrimp-LMM-Agent-Rag/data/uploads")
Path(WORKSPACE).mkdir(parents=True, exist_ok=True)
Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)

# deepagents 專案根目錄（存放 AGENTS.md 和 .deepagents/skills/）
AGENT_DIR   = os.getenv("AGENT_DIR", "/opt/Shrimp-LMM-Agent-Rag/Agent_Server")
# Skills 目錄（包含 shrimp-behavior-analysis 等子目錄）
SKILLS_DIR  = os.getenv("SKILLS_DIR", f"{AGENT_DIR}/.deepagents/skills")
# ──────────────────────────────────────────────────────────

# ─── llama.cpp → LangChain ChatOpenAI ─────────────────────
llm = ChatOpenAI(
    base_url=LLAMA_URL,
    api_key="not-needed",
    model=LLAMA_MODEL,
    temperature=0.7,
    max_tokens=4096,
    streaming=True,
)

# ─── 工具 ──────────────────────────────────────────────────
@tool
def run_shell(command: str) -> str:
    """在 workspace 目錄內執行 shell 指令"""
    BLOCKED = ["rm -rf /", "mkfs", ":(){ :|:& };:"]
    if any(b in command for b in BLOCKED):
        return "錯誤：指令被安全規則封鎖"
    try:
        result = subprocess.run(
            command, shell=True, cwd=WORKSPACE,
            capture_output=True, text=True, timeout=15
        )
        return result.stdout or result.stderr or "(無輸出)"
    except subprocess.TimeoutExpired:
        return "錯誤：指令逾時 (15s)"

@tool
def delete_upload(filename: str) -> str:
    """處理完畢後，刪除 uploads 暫存區內的指定檔案"""
    if ".." in filename or "/" in filename:
        return "錯誤：不允許使用路徑分隔符，請只傳檔名"
    target = Path(UPLOADS_DIR) / filename
    if not target.exists():
        return f"錯誤：找不到檔案 {filename}"
    target.unlink()
    return f"已刪除暫存檔案：{filename}"

# ─── Checkpointer ─────────────────────────────────────────
checkpointer = MemorySaver()

# ─── Backend ───────────────────────────────────────────────
# FilesystemBackend 只用來載入 AGENTS.md 和 skills
# 實際的資料存取（WORKSPACE / UPLOADS_DIR）由自訂工具直接操作實體路徑
backend = FilesystemBackend(root_dir=AGENT_DIR)

# ─── Deep Agent ────────────────────────────────────────────
agent = create_deep_agent(
    model=llm,
    backend=backend,
    skills=[SKILLS_DIR],  # 實體路徑，FilesystemBackend 直接讀磁碟
    tools=[run_shell, delete_upload],
    system_prompt=(
        "你是一個蝦子研究專用的 AI 助理。\n"
        f"專案資料目錄（可讀寫）：{WORKSPACE}\n"
        f"媒體上傳暫存區（處理完請用 delete_upload 刪除）：{UPLOADS_DIR}\n"
        f"Agent 設定目錄：{AGENT_DIR}\n"
        "使用 run_shell 或內建工具操作檔案時，請使用上述完整實體路徑。\n"
        "執行任何修改檔案或執行指令前，請先說明你要做什麼。"
    ),
    interrupt_on={
        "run_shell":     {"allowed_decisions": ["approve", "edit", "reject"]},
        "write_file":    {"allowed_decisions": ["approve", "edit", "reject"]},
        "edit_file":     {"allowed_decisions": ["approve", "reject"]},
        "delete_upload": {"allowed_decisions": ["approve", "reject"]},
        "read_file":     False,
        "ls":            False,
        "glob":          False,
        "grep":          False,
    },
    # permissions 由工具層 (run_shell / delete_upload) 負責路徑安全，
    # FilesystemBackend 的虛擬 FS 只供 AGENTS.md / skills 使用
    checkpointer=checkpointer,
)

# ─── FastAPI ───────────────────────────────────────────────
app = FastAPI(title="Deep Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── SSE 格式工具函式 ──────────────────────────────────────
def sse_token(text: str) -> dict:
    """前端解析的格式：data.choices[0].delta.content"""
    return {
        "data": json.dumps(
            {"choices": [{"delta": {"content": text}}]},
            ensure_ascii=False
        )
    }

def sse_interrupt(thread_id: str, calls: list) -> dict:
    """前端偵測 data.interrupt == true"""
    return {
        "data": json.dumps(
            {"interrupt": True, "thread_id": thread_id, "calls": calls},
            ensure_ascii=False
        )
    }

def sse_done() -> dict:
    return {"data": "[DONE]"}


# ─── 共用串流邏輯 ──────────────────────────────────────────
async def stream_agent(input_data, config: dict):
    thread_id = config["configurable"]["thread_id"]

    async for event in agent.astream_events(input_data, config=config, version="v2"):
        kind = event["event"]

        # LLM 輸出 token → 前端格式
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content:
                yield sse_token(chunk.content)

        # 工具開始執行：送一行說明文字給使用者看
        elif kind == "on_tool_start":
            name  = event["name"]
            input_ = event["data"].get("input", {})
            hint  = f"\n\n> ⚙️ 正在執行工具 **{name}**"
            if input_:
                hint += f"：`{json.dumps(input_, ensure_ascii=False)}`"
            yield sse_token(hint + "\n")

        # 工具執行完畢
        elif kind == "on_tool_end":
            name   = event["name"]
            output = str(event["data"].get("output", ""))
            yield sse_token(f"\n> ✅ `{name}` 完成：{output[:200]}\n\n")

        # 中斷點（需要人工確認）
        elif kind == "on_interrupt":
            iv = event["data"]["value"]
            action_requests = iv.get("action_requests", [])
            review_configs  = iv.get("review_configs", [])
            cfg_map = {c["action_name"]: c for c in review_configs}
            calls = [
                {
                    "name":              a["name"],
                    "args":              a.get("args", {}),
                    "allowed_decisions": cfg_map.get(a["name"], {}).get(
                        "allowed_decisions", ["approve", "reject"]
                    ),
                }
                for a in action_requests
            ]
            yield sse_interrupt(thread_id, calls)
            return  # 停止 stream，等待 /approve


# ─── POST /chat ────────────────────────────────────────────
# 接收：multipart/form-data
#   text:      使用者訊息
#   thread_id: 對話 thread（固定即可保留記憶）
#   files:     圖片/影片（會存到 UPLOADS_DIR）
@app.post("/chat")
async def chat(
    text:      str        = Form(""),
    thread_id: str        = Form("default_thread"),
    files:     list[UploadFile] = File(default=[]),
):
    config = {"configurable": {"thread_id": thread_id}}

    # 儲存上傳的檔案到 UPLOADS_DIR
    saved_files: list[str] = []
    for f in files:
        dest = Path(UPLOADS_DIR) / f.filename
        with dest.open("wb") as out:
            shutil.copyfileobj(f.file, out)
        saved_files.append(f.filename)

    # 組合使用者訊息
    user_content = text or ""
    if saved_files:
        file_list = ", ".join(f"`{n}`" for n in saved_files)
        user_content += f"\n\n已上傳檔案：{file_list}（位於 {UPLOADS_DIR}）"

    messages = [{"role": "user", "content": user_content}]

    async def event_gen():
        try:
            async for item in stream_agent({"messages": messages}, config):
                yield item
        except Exception as e:
            yield sse_token(f"\n\n❌ 發生錯誤：{e}")
        yield sse_done()

    return EventSourceResponse(event_gen())


# ─── POST /approve ─────────────────────────────────────────
# 前端按「核准執行」後呼叫
# 接收：multipart/form-data
#   thread_id: 同一個 thread
#   decision:  "approve"（預設）或 "reject"
@app.post("/approve")
async def approve(
    thread_id: str = Form(...),
    decision:  str = Form("approve"),
):
    config = {"configurable": {"thread_id": thread_id}}
    dec_type = "approve" if decision == "approve" else "reject"

    async def event_gen():
        try:
            async for item in stream_agent(
                Command(resume={"decisions": [{"type": dec_type}]}),
                config
            ):
                yield item
        except Exception as e:
            yield sse_token(f"\n\n❌ 發生錯誤：{e}")
        yield sse_done()

    return EventSourceResponse(event_gen())


# ─── GET /status ───────────────────────────────────────────
@app.get("/status")
def status():
    return {
        "llama_url":   LLAMA_URL,
        "llama_model": LLAMA_MODEL,
        "workspace":   WORKSPACE,
        "uploads_dir": UPLOADS_DIR,
        "agent_dir":   AGENT_DIR,
        "skills_dir":  SKILLS_DIR,
    }


@app.on_event("startup")
async def startup():
    print(f"\n🤖 Deep Agent")
    print(f"   Port      : {PORT}")
    print(f"   llama.cpp : {LLAMA_URL}  ({LLAMA_MODEL})")
    print(f"   Workspace : {WORKSPACE}")
    print(f"   Uploads   : {UPLOADS_DIR}")
    print(f"   Agent Dir : {AGENT_DIR}")
    print(f"   Skills    : {SKILLS_DIR}")
    print(f"\n   POST /chat    — 發送訊息 (multipart SSE)")
    print(f"   POST /approve — 核准/拒絕工具執行 (multipart SSE)")
    print(f"   GET  /status  — 狀態\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent:app", host="127.0.0.1", port=PORT, reload=True)