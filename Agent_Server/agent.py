import os
import sys
import shutil
import json
import asyncio
import importlib.util
from typing import List
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
SKILLS_PATH = os.path.join(os.path.dirname(__file__), ".deepagents/skills/")
sys.path.append(SKILLS_PATH)

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage


load_dotenv()

def load_skill_tool(skill_dir: str, script_name: str, tool_name: str):
    """解決 Python 無法直接 import 帶連字號 (-) 路徑的問題"""
    module_path = os.path.join(SKILLS_PATH, skill_dir, "scripts", f"{script_name}.py")
    spec = importlib.util.spec_from_file_location(script_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, tool_name)


# 載入追蹤工具 (目錄：shrimp-tracking)
yolo_tracker = load_skill_tool("shrimp-tracking", "shrimp_analysis", "yolo_tracker")
shrimp_image_detector = load_skill_tool("shrimp-tracking", "shrimp_analysis", "shrimp_image_detector")

# 載入搜索工具 (目錄：shrimp-search)
list_files_in_directory = load_skill_tool("shrimp-search", "search_tools", "list_files_in_directory")
app = FastAPI()

shrimp_behavior_expert_report = load_skill_tool(
    "shrimp-behavior-analysis", 
    "behavior_expert_lmm", 
    "analyze_behavior_with_lmm"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. 初始化對接 llama.cpp (8080)
llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key="sk-no-key",
    model=os.getenv("MODEL_NAME"),
    streaming=True # 必須開啟
)

agent = create_deep_agent(
    model=llm,
    backend=FilesystemBackend(root_dir=".", virtual_mode=False),
    system_prompt="你是一個養殖自動化助手，當用戶詢問蝦池狀況時，請調用分析工具。",
    checkpointer=MemorySaver(),
    skills=["./.deepagents/skills/"],
    memory=["./.deepagents/AGENTS.md"],
    tools=[yolo_tracker, shrimp_image_detector, list_files_in_directory,shrimp_behavior_expert_report],
)

# 2. 串流生成器 (符合 OpenAI SSE 格式)
async def openai_stream_generator(prompt, thread_id):
    active_tools = set()  # 用於追蹤當前啟動的工具，避免重複輸出訊息

    async for event in agent.astream_events(
        {"messages": [HumanMessage(content=prompt)]},
        config={"configurable": {"thread_id": thread_id}},
        version="v2",
    ):
        kind = event["event"]
        
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                data = {"choices": [{"delta": {"content": content}, "index": 0}]}
                yield f"data: {json.dumps(data)}\n\n"
        
        elif kind == "on_tool_start":
            tool_name = event['name']
            if tool_name not in active_tools:
                active_tools.add(tool_name)
                # 使用引用區塊 (>) 與粗體，讓介面產生層次感
                msg = f"\n\n> ⚙️ **系統調用**: `{tool_name}` ... 執行分析中\n\n"
                data = {"choices": [{"delta": {"content": msg}, "index": 0}]}
                yield f"data: {json.dumps(data)}\n\n"
        
        # 工具結束時清理狀態（選配）
        elif kind == "on_tool_end":
            tool_name = event['name']
            if tool_name in active_tools:
                active_tools.remove(tool_name)

    yield "data: [DONE]\n\n"

@app.post("/chat")
async def chat_with_agent(
    text: str = Form(...),
    thread_id: str = Form(...),
    files: List[UploadFile] = File(None)
):
    prompt_context = text
    
    if files:
        file_names = []
        for file in files:
            path = os.path.join(UPLOAD_DIR, file.filename)
            with open(path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_names.append(file.filename)
        # 提供絕對路徑暗示，讓 Agent 自主尋找
        prompt_context += f"\n\n[系統提示：已上傳檔案 {file_names} 至 /data/uploads/]"

    return StreamingResponse(
        openai_stream_generator(prompt_context, thread_id),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)