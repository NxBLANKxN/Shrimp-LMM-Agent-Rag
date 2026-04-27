import json
import os
import shutil
import subprocess
import fitz
from pathlib import Path
from contextlib import asynccontextmanager

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
LLAMA_URL   = os.getenv("OPENAI_BASE_URL",   "http://localhost:8080/v1")
LLAMA_MODEL = os.getenv("MODEL_NAME", "local-model")
PORT        = int(os.getenv("PORT", 8001))
# 物理路徑對齊
WORKSPACE   = os.getenv("WORKSPACE","/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base")
UPLOADS_DIR = f"{WORKSPACE}/raw/clippings"
ROOT_DIR   = "/opt/Shrimp-LMM-Agent-Rag/Agent_Server"
AGENT_DIR   = ".deepagents/AGENTS.md"
SKILLS_DIR  = ".deepagents/skills/"
KNOWLEDGE_BASE_AGENT_DIR = "knowledge-base/AGENTS.md"

print(f"./{AGENT_DIR}")

# 確保目錄存在
for d in [WORKSPACE, UPLOADS_DIR, SKILLS_DIR]:
    Path(d).mkdir(parents=True, exist_ok=True)

# ─── llama.cpp → LangChain ChatOpenAI ─────────────────────
llm = ChatOpenAI(
    base_url=LLAMA_URL,
    api_key="not-needed",
    model=LLAMA_MODEL,
    temperature=0.0,
    max_tokens=64000,
    streaming=True,
)

# ─── 工具定義 ──────────────────────────────────────────────
@tool
def read_pdf_text(file_path: str) -> str:
    """
    讀取指定路徑的 PDF 檔案並提取純文字內容。
    適用於學術文獻 (articles/) 與研究報告的深度分析。
    """
    path = Path(file_path)
    # 如果是相對路徑，則補上 AGENT_DIR
    if not path.is_absolute():
        path = Path(AGENT_DIR) / file_path

    if not path.exists():
        return f"錯誤：找不到檔案 {file_path}"
    
    try:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        
        if not text.strip():
            return "警告：該 PDF 可能為掃描檔或無可提取文字。"
            
        return f"--- PDF 內容開始 ---\n{text}\n--- PDF 內容結束 ---"
    except Exception as e:
        return f"讀取 PDF 時發生錯誤：{str(e)}"


# ─── 初始化 Agent 核心 ──────────────────────────────────────
checkpointer = MemorySaver()
# 修正警告：顯式指定 virtual_mode
backend = FilesystemBackend(root_dir=f"{ROOT_DIR}",virtual_mode=True)
agent = create_deep_agent(
    model=llm,
    backend=backend,
    skills=[f"./{SKILLS_DIR}"],
    memory=[f"./{AGENT_DIR}"],
    tools=[read_pdf_text ],
    interrupt_on={
        "write_file":    {"allowed_decisions": ["approve", "edit", "reject"]},
        "read_pdf_text": False,
        "read_file":     False,
        "ls":            False,
        "glob":          False,
        "bunx @tobilu/qmd": False, # QMD 索引自動化
    },
    checkpointer=checkpointer,
)

# ─── FastAPI 生命週期與服務 ──────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 替代原本的 @app.on_event("startup")
    print(f"\n🚀 Shrimp Agent Server 啟動中")
    print(f"   - Workspace: {WORKSPACE}\n   - Agent Dir: {AGENT_DIR}")
    yield
    # Shutdown: 可以在此處清理資源
    print("\n🛑 Shrimp Agent Server 已關閉")

app = FastAPI(title="Deep Agent API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── SSE 工具與路由 (保持原邏輯) ──────────────────────────────
def sse_token(text: str) -> dict:
    return {"data": json.dumps({"choices": [{"delta": {"content": text}}]}, ensure_ascii=False)}

def sse_interrupt(thread_id: str, calls: list) -> dict:
    return {"data": json.dumps({"interrupt": True, "thread_id": thread_id, "calls": calls}, ensure_ascii=False)}

async def stream_agent(input_data, config: dict):
    thread_id = config["configurable"]["thread_id"]
    async for event in agent.astream_events(input_data, config=config, version="v2"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content: yield sse_token(chunk.content)
        elif kind == "on_tool_start":
            yield sse_token(f"\n\n> ⚙️ 執行工具 `{event['name']}`\n")
        elif kind == "on_interrupt":
            iv = event["data"]["value"]
            calls = [{"name": a["name"], "args": a.get("args", {}), "allowed_decisions": ["approve", "reject"]} for a in iv.get("action_requests", [])]
            yield sse_interrupt(thread_id, calls)
            return

@app.post("/chat")
async def chat(text: str = Form(""), thread_id: str = Form("default"), files: list[UploadFile] = File(default=[])):
    config = {"configurable": {"thread_id": thread_id}}
    for f in files:
        dest = Path(UPLOADS_DIR) / f.filename
        with dest.open("wb") as out: shutil.copyfileobj(f.file, out)
    
    prompt = text + (f"\n\n已上傳檔案：{', '.join([f.filename for f in files])}" if files else "")
    async def event_gen():
        async for item in stream_agent({"messages": [{"role": "user", "content": prompt}]}, config): yield item
        yield {"data": "[DONE]"}
    return EventSourceResponse(event_gen())

@app.post("/approve")
async def approve(thread_id: str = Form(...), decision: str = Form("approve")):
    config = {"configurable": {"thread_id": thread_id}}
    dec_type = "approve" if decision == "approve" else "reject"
    async def event_gen():
        async for item in stream_agent(Command(resume={"decisions": [{"type": dec_type}]}), config): yield item
        yield {"data": "[DONE]"}
    return EventSourceResponse(event_gen())

@app.get("/status")
def status():
    return {"workspace": WORKSPACE, "agent_dir": AGENT_DIR, "llama_url": LLAMA_URL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent:app", host="0.0.0.0", port=PORT, reload=True)