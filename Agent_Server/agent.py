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

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


from deepagents import create_deep_agent
from deepagents.middleware.subagents import SubAgent
from deepagents.backends.filesystem import FilesystemBackend

# llm-wiki 工具集（透過 sys.path 插入，避免 relative import 問題）
import sys
sys.path.append(str(Path(__file__).parent / ".deepagents" / "tools"))
try:
    from wiki_tools import read_wiki_file, list_wiki_files, write_wiki_file, append_log, search_wiki, run_lint, list_unprocessed_raw_files
    from qmd_tools import qmd_query, qmd_status, qmd_reindex
except ImportError as e:
    print(f"Warning: Failed to import wiki/qmd tools: {e}")
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
KNOWLEDGE_BASE = ".deepagents/knowledge-base/AGENTS.md"
SKILLS_DIR  = ".deepagents/skills/"


# raw 子資料夾（自動分類）
UPLOAD_MAP = {
    "pdf":        f"{RAW_DIR}/pdfs",
    "image":      f"{RAW_DIR}/images",
    "video":      f"{RAW_DIR}/clippings",
    "audio":      f"{RAW_DIR}/clippings",
    "excel":      f"{RAW_DIR}/notes",
    "csv":        f"{RAW_DIR}/notes",
    "doc":        f"{RAW_DIR}/articles",
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

"""
llm = ChatOpenAI(
    base_url=LLAMA_URL,
    api_key="not-needed",
    model=LLAMA_MODEL,
    max_tokens=200000,
)
"""

llm = ChatGoogleGenerativeAI(
    api_key="AIzaSyC7du_mD-m7FSPF8nEGZrj0eevyT0cUJKY",
    model="gemma-4-31b-it",
    max_tokens=200000,
)


# ─────────────────────────────────────────────
# 工具
# ─────────────────────────────────────────────
@tool
def read_pdf_text(file_path: str) -> str:
    """
    讀取 PDF 純文字內容。可以傳入相對路徑或只有檔名，系統會自動在 raw/ 內尋找。
    """
    
    # 嘗試幾種可能的位置
    possible_paths = [
        Path(ROOT_DIR) / file_path,
        Path(ROOT_DIR) / "knowledge-base" / "raw" / file_path,
    ]
    
    target_path = None
    for p in possible_paths:
        if p.exists() and p.is_file():
            target_path = p
            break
            
    # 如果還是找不到，嘗試用檔名全域搜尋 knowledge-base/raw
    if not target_path:
        raw_root = Path(ROOT_DIR) / "knowledge-base" / "raw"
        basename = Path(file_path).name
        for p in raw_root.rglob("*.pdf"):
            if p.name == basename:
                target_path = p
                break

    if not target_path or not target_path.exists():
        return f"❌ 無法讀取 PDF：找不到檔案 '{file_path}'"

    try:
        text = ""
        with fitz.open(str(target_path)) as doc:
            for page in doc:
                text += page.get_text()

        if not text.strip():
            return "PDF 無法提取文字，可能是掃描檔"

        return text

    except Exception as e:
        return f"❌ 讀取 PDF 發生錯誤：{str(e)}"

@tool
def overwrite_file(file_path: str, content: str) -> str:
    """
    完全覆蓋現有檔案的內容。此工具用於替換檔案的全部內容，而非僅僅編輯特定字串。
    當目標是更新知識庫中檔案的完整內容時，應使用此工具。
    
    Args:
        file_path (str): 需要被覆蓋的檔案的絕對路徑。必須是絕對路徑。
        content (str): 用來替換現有檔案的完整新文本內容。
        
    Returns:
        str: 執行操作結果訊息（成功或失敗）。
    """
    path = f"{ROOT_DIR}/{file_path}"
    try:
        # 使用 'w' 模式進行寫入，這會完全覆蓋檔案的現有內容
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功：檔案 '{file_path}' 的內容已完全覆蓋並更新。"
    except FileNotFoundError:
        return f"錯誤：找不到檔案 '{file_path}'。請確認路徑是否正確。"
    except Exception as e:
        return f"執行 overwrite_file 發生未知錯誤：{str(e)}"


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
# Subagents
# ─────────────────────────────────────────────





# ─────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────
checkpointer = MemorySaver()

backend = FilesystemBackend(
    root_dir=ROOT_DIR,
    virtual_mode=True
)

"""
# 讀取 Wiki 行為契約 (單一真實來源)
try:
    with open(f"{WORKSPACE}/CLAUDE.md", "r", encoding="utf-8") as f:
        wiki_rules = f.read()
except FileNotFoundError:
    wiki_rules = ""

system_prompt_text = f
你是一個專門負責管理 LLM Wiki 知識庫的 AI 管理員（WikiManager）。
你的唯一職責是精準地執行知識庫的增刪改查操作。請嚴格遵守以下操作規範：

{wiki_rules}
"""

# ─────────────────────────────────────────────
# Subagents
# ─────────────────────────────────────────────
"""
wiki_manager: SubAgent = {
    "name": "WikiManager",
    "description": "負責管理 LLM Wiki 知識庫，包含文獻攝入 (INGEST)、精準查詢 (QUERY)、綜合整理 (REFLECT) 與健康檢查 (LINT)。當你需要將新的專業知識、檔案內容寫入知識庫，或者需要查閱歷史文獻與概念時，請將詳細的指令交給此代理執行。",
    "system_prompt": system_prompt_text,
    "model": llm,
    "tools": [
        read_wiki_file,
        list_wiki_files,
        list_unprocessed_raw_files,
        write_wiki_file,
        append_log,
        search_wiki,
        run_lint,
        qmd_query,
        qmd_status,
        qmd_reindex,
    ]
}
"""
agent = create_deep_agent(
    model=llm,
    backend=backend,
    system_prompt="""
你是一位專業智慧蝦隻養殖 AI 助手。
【高度自動化守則】：
1. **自動建檔 (Auto-INGEST)**：當系統提示使用者上傳了新檔案（如 pdf, doc 等），請你「主動」且「立即」將檔案路徑傳給 WikiManager，命令它執行完整的 INGEST 攝入流程，不要只是單純總結內容。
2. **自動查庫 (Auto-QUERY)**：當使用者詢問任何專業或事實性問題時，請你「主動」呼叫 WikiManager 進行 QUERY 操作，以便根據我們自己的知識庫來回答，避免幻覺。
3. **自動批次同步 (Auto-Sync)**：當使用者要求「掃描未處理的檔案」、「整理知識庫」或想要處理所有檔案時，請主動呼叫 WikiManager 使用 `list_unprocessed_raw_files` 找出所有遺漏在 `raw/` 內的檔案，並自動對它們逐一執行 INGEST。
4. **無縫執行**：你可以直接呼叫 WikiManager 工具，不需要在每次行動前都反問使用者「需要我幫您存入知識庫嗎？」。直接做！
""",
    skills=[f"./{SKILLS_DIR}"],
    memory=[f"./{AGENT_DIR}", f"./{KNOWLEDGE_BASE}"],
    #subagents=[wiki_manager],
    tools=[
        # ── 原始資料工具 ──
        read_pdf_text,
        overwrite_file,
        # ── Wiki 工具 ──
        read_wiki_file,
        list_wiki_files,
        list_unprocessed_raw_files,
        write_wiki_file,
        append_log,
        search_wiki,
        run_lint,
        qmd_query,
        qmd_status,
        qmd_reindex,
    ],
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
            content = chunk.content
            # content 可能是 str（純文字）或 list（多模態），統一處理
            if isinstance(content, str) and content:
                yield sse_token(text=content, status=f"Streaming from {name}...")
            elif isinstance(content, list):
                combined = "".join(
                    part.get("text", "") for part in content if isinstance(part, dict)
                )
                if combined:
                    yield sse_token(text=combined, status=f"Streaming from {name}...")

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
    config = {"configurable": {"thread_id": thread_id} , "recursion_limit": 50}

    uploaded_paths = []

    for f in files:
        path = save_upload_file(f)
        uploaded_paths.append(path)

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