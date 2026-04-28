import json
import os
import shutil
import mimetypes
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


# ─────────────────────────────────────────────
# 基本設定
# ─────────────────────────────────────────────
LLAMA_URL   = "http://localhost:8080/v1"
LLAMA_MODEL = "gemma-4-E4B-it-GGUF:Q8_0"
PORT        = 8001

ROOT_DIR    = "/opt/Shrimp-LMM-Agent-Rag/Agent_Server"
WORKSPACE   = f"{ROOT_DIR}/knowledge-base"

RAW_DIR     = f"{WORKSPACE}/raw"

AGENT_DIR   = ".deepagents/AGENTS.md"
SKILLS_DIR  = ".deepagents/skills/"


# raw 子資料夾（自動分類）
UPLOAD_MAP = {
    "pdf":        f"{RAW_DIR}/articles",
    "image":      f"{RAW_DIR}/images",
    "video":      f"{RAW_DIR}/videos",
    "audio":      f"{RAW_DIR}/audio",
    "excel":      f"{RAW_DIR}/datasets",
    "csv":        f"{RAW_DIR}/datasets",
    "doc":        f"{RAW_DIR}/documents",
    "code":       f"{RAW_DIR}/notes",
    "text":       f"{RAW_DIR}/notes",
    "unknown":    f"{RAW_DIR}/clippings",
}


# 建立資料夾
for path in UPLOAD_MAP.values():
    os.makedirs(path, exist_ok=True)


# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────
llm = ChatOpenAI(
    base_url=LLAMA_URL,
    api_key="not-needed",
    model=LLAMA_MODEL,
    temperature=0.0,
    max_tokens=64000,
    streaming=True,
)


# ─────────────────────────────────────────────
# 工具
# ─────────────────────────────────────────────
@tool
def read_pdf_text(file_path: str) -> str:
    """
    讀取 PDF 純文字內容。
    """

    path = f"{ROOT_DIR}/{file_path}"

    try:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()

        if not text.strip():
            return "PDF 無法提取文字，可能是掃描檔"

        return text[:15000]

    except Exception as e:
        return str(e)


# ─────────────────────────────────────────────
# 檔案分類器
# ─────────────────────────────────────────────
def classify_file(filename: str) -> str:
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return "pdf"

    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        return "image"

    elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
        return "video"

    elif ext in [".mp3", ".wav", ".m4a"]:
        return "audio"

    elif ext in [".xlsx", ".xls"]:
        return "excel"

    elif ext == ".csv":
        return "csv"

    elif ext in [".doc", ".docx", ".ppt", ".pptx"]:
        return "doc"

    elif ext in [".py", ".js", ".ts", ".java", ".cpp", ".php", ".html", ".css"]:
        return "code"

    elif ext in [".txt", ".md", ".json", ".yaml", ".yml"]:
        return "text"

    return "unknown"


def save_upload_file(upload: UploadFile) -> str:
    file_type = classify_file(upload.filename)
    target_dir = UPLOAD_MAP[file_type]

    dest = Path(target_dir) / upload.filename

    with dest.open("wb") as out:
        shutil.copyfileobj(upload.file, out)

    relative_path = str(dest).replace(ROOT_DIR + "/", "")
    return relative_path


# ─────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────
checkpointer = MemorySaver()

backend = FilesystemBackend(
    root_dir=ROOT_DIR,
    virtual_mode=True
)

agent = create_deep_agent(
    model=llm,
    backend=backend,
    system_prompt="""
你是一位專業智慧蝦隻養殖 AI 助手。

規則：
1. 使用者上傳的檔案已自動分類到 raw/ 對應資料夾
2. 如果是 PDF，可使用 read_pdf_text
3. 根據使用者語言回答（預設繁體中文）
4. 協助分析蝦病、水質、養殖、研究資料
""",
    skills=[f"./{SKILLS_DIR}"],
    memory=[f"./{AGENT_DIR}"],
    tools=[read_pdf_text],
    interrupt_on={
        "write_file": {
            "allowed_decisions": ["approve", "edit", "reject"]
        }
    },
    checkpointer=checkpointer,
)


# ─────────────────────────────────────────────
# FastAPI
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Shrimp Agent Server 啟動")
    yield
    print("🛑 Server 關閉")


app = FastAPI(title="Shrimp DeepAgent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# SSE
# ─────────────────────────────────────────────
def sse_token(text: str = "", status: str = None):
    """
    支援同時發送內容與狀態
    """
    payload = {
        "choices": [{"delta": {"content": text}}]
    }
    if status:
        payload["status"] = status  # 前端會檢查這個欄位
        
    return {
        "data": json.dumps(payload, ensure_ascii=False)
    }


async def stream_agent(input_data, config):
    async for event in agent.astream_events(
        input_data,
        config=config,
        version="v2"
    ):
        kind = event["event"]
        # 獲取事件名稱，例如：read_pdf_text, ChatOpenAI, 或 node 名稱
        name = event.get("name", "Unknown")

        # 1. 捕捉工具執行
        if kind == "on_tool_start":
            # 直接顯示原始工具名稱
            yield sse_token(status=f"Executing tool: {name}...")

        # 2. 捕捉模型思考與處理
        elif kind == "on_chat_model_start":
            yield sse_token(status=f"Model starting: {name}...")

        # 3. 捕捉模型吐字
        elif kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content:
                # 這裡 status 保持顯示模型正在回應，並帶上原始模型名稱
                yield sse_token(text=chunk.content, status=f"Streaming from {name}...")

        # 4. (選配) 捕捉節點切換 - 如果您想看 LangGraph 的節點跳轉
        elif kind == "on_chain_start":
            yield sse_token(status=f"Entering: {name}")

# ─────────────────────────────────────────────
# Chat API
# ─────────────────────────────────────────────
@app.post("/chat")
async def chat(
    text: str = Form(""),
    thread_id: str = Form("default"),
    files: list[UploadFile] = File(default=[])
):
    config = {"configurable": {"thread_id": thread_id}}

    uploaded_paths = []

    for f in files:
        path = save_upload_file(f)
        uploaded_paths.append(path)

    prompt = text

    if uploaded_paths:
        prompt += "\n\n已上傳檔案：\n" + "\n".join(uploaded_paths)

    async def event_gen():
        async for item in stream_agent(
            {"messages": [{"role": "user", "content": prompt}]},
            config
        ):
            yield item

        yield {"data": "[DONE]"}

    return EventSourceResponse(event_gen())


# ─────────────────────────────────────────────
# Status
# ─────────────────────────────────────────────
@app.get("/status")
def status():
    return {
        "workspace": WORKSPACE,
        "raw_dir": RAW_DIR,
        "llama": LLAMA_URL
    }


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent:app", host="0.0.0.0", port=PORT, reload=True)