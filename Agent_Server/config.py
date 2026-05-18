# ─────────────────────────────────────────────
# config.py — 所有全域常數的單一真實來源
# ─────────────────────────────────────────────
import os

# ── 伺服器 ──
LLAMA_URL   = "http://localhost:8080/v1"
LLAMA_MODEL = "gemma-4-E4B-it-GGUF:Q8_0"
PORT        = 8001

# ── 路徑 ──
ROOT_DIR   = "/opt/Shrimp-LMM-Agent-Rag/Agent_Server"
WORKSPACE  = f"{ROOT_DIR}/knowledge-base"
RAW_DIR    = f"{WORKSPACE}/raw"

# ── DeepAgents 設定路徑 ──
AGENT_DIR      = ".deepagents/AGENTS.md"
KNOWLEDGE_BASE = ".deepagents/knowledge-base/AGENTS.md"
SKILLS_DIR     = ".deepagents/skills/"

# ── 上傳檔案分類路徑 ──
UPLOAD_MAP = {
    "pdf":      f"{RAW_DIR}/pdfs",
    "image":    f"{RAW_DIR}/images",
    "video":    f"{RAW_DIR}/videos",
    "audio":    f"{RAW_DIR}/audios",
    "excel":    f"{RAW_DIR}/notes",
    "csv":      f"{RAW_DIR}/notes",
    "doc":      f"{RAW_DIR}/articles",
    "code":     f"{RAW_DIR}/notes",
    "text":     f"{RAW_DIR}/notes",
    "clipping": f"{RAW_DIR}/clippings",
    "unknown":  f"{RAW_DIR}/others",
}

# 確保所有上傳資料夾存在
for _path in UPLOAD_MAP.values():
    os.makedirs(_path, exist_ok=True)
