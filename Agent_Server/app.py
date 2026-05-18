# ─────────────────────────────────────────────
# app.py — FastAPI 應用、路由與 SSE 串流
# ─────────────────────────────────────────────
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from config import WORKSPACE, RAW_DIR, LLAMA_URL
from file_handler import save_upload_file
from deep_agent import agent


# ─────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Shrimp Agent Server 啟動")
    yield
    print("🛑 Server 關閉")


# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────
app = FastAPI(title="Shrimp DeepAgent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# SSE 工具函式
# ─────────────────────────────────────────────
def sse_token(text: str = "", status: str = None) -> dict:
    """組裝 SSE payload，同時支援文字內容與狀態欄位。"""
    payload = {"choices": [{"delta": {"content": text}}]}
    if status:
        payload["status"] = status
    return {"data": json.dumps(payload, ensure_ascii=False)}


async def stream_agent(input_data, config):
    """將 DeepAgent 事件轉換為 SSE token 串流。"""
    async for event in agent.astream_events(input_data, config=config, version="v2"):
        kind = event["event"]
        name = event.get("name", "Unknown")

        if kind == "on_tool_start":
            yield sse_token(status=f"Executing tool: {name}...")

        elif kind == "on_chat_model_start":
            yield sse_token(status=f"Model starting: {name}...")

        elif kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            content = chunk.content
            if isinstance(content, str) and content:
                yield sse_token(text=content, status=f"Streaming from {name}...")
            elif isinstance(content, list):
                combined = "".join(
                    part.get("text", "") for part in content if isinstance(part, dict)
                )
                if combined:
                    yield sse_token(text=combined, status=f"Streaming from {name}...")

        elif kind == "on_chain_start":
            yield sse_token(status=f"Entering: {name}")


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.post("/chat")
async def chat(
    text: str = Form(""),
    thread_id: str = Form("default"),
    files: list[UploadFile] = File(default=[]),
):
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}

    uploaded_paths = [save_upload_file(f) for f in files]

    prompt = text
    if uploaded_paths:
        prompt += "\n\n[系統自動事件] 使用者剛剛上傳了以下檔案：\n" + "\n".join(uploaded_paths)
        if not text.strip():
            prompt += "\n(使用者並未輸入文字，請自動呼叫 WikiManager 對上述檔案執行 INGEST 攝入操作。)"
        else:
            prompt += "\n(請在處理使用者的文字需求時，同時考慮是否需要呼叫 WikiManager 攝入這些檔案。)"

    async def event_gen():
        async for item in stream_agent(
            {"messages": [{"role": "user", "content": prompt}]},
            config,
        ):
            yield item
        yield {"data": "[DONE]"}

    return EventSourceResponse(event_gen())


@app.get("/status")
def status():
    return {
        "workspace": WORKSPACE,
        "raw_dir":   RAW_DIR,
        "llama":     LLAMA_URL,
    }
