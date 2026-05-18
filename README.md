# Shrimp-LMM-Agent-Rag

本專案旨在結合 **大型多模態模型 (LMM)**、**AI Agent (代理人)** 與 **RAG (檢索增強生成)** 技術，實現智慧化的決策、資料檢索與增量型個人知識庫（LLM Wiki）系統。特別針對蝦隻養殖、水質管理與疾病診斷等領域打造專屬 AI 助手。

---

## 專案核心架構

本系統採用微服務架構，主要分為三大模組：

### 1. Agent Server (代理人與知識庫核心)
- **目錄位置**: `/Agent_Server`
- **技術棧**: FastAPI, LangChain, DeepAgents, qmd
- **核心功能**: 
  - 整合 `gemma-4-E4B-it` 等本地大型語言模型。
  - 實作了基於 Karpathy 思路的 **LLM Wiki 知識庫系統**（位於 `knowledge-base/`），包含 `raw` (原始資料層) 與 `wiki` (結構化概念/實體層)。
  - 提供 Agent 自主檢索 (`qmd_query`)、文獻攝入 (`ingest`)、反思綜合 (`reflect`) 與健康檢查 (`lint`) 等工具集。

### 2. API Server (動態網頁後端)
- **目錄位置**: `/Dynamic_Web/Api_Server`
- **技術棧**: FastAPI, Python
- **核心功能**: 處理前端請求，管理對話階段，並與 Agent Server 進行溝通。

### 3. SSSTI Web (動態網頁前端)
- **目錄位置**: `/Dynamic_Web/SSSTI_Web`
- **技術棧**: Bun, Vite, Vue/React (視實作而定)
- **核心功能**: 提供使用者直覺的操作介面，支援即時串流輸出 (SSE)、檔案上傳與對話互動。

---

## 系統需求 (Requirements)

- **OS:** Ubuntu 22.04+ (或相容的 Linux 發行版)
- **Python:** 3.10+
- **Node/Bun:** 推薦使用 Bun 進行前端開發
- **CUDA:** 12.6
- **GPU:** NVIDIA GPU (建議 12GB VRAM 以上)

---

## 環境配置 (Environment Setup)

本專案建議為每個後端模組建立獨立的虛擬環境：

### 1. Agent Server 配置
```bash
cd Agent_Server
python3 -m venv .venv
source .venv/bin/activate
# 安裝核心套件 (含 LangChain 與 LLM Wiki 支援)
pip install fastapi uvicorn sse-starlette langchain langchain-google-genai langchain-openai langgraph pymupdf
# 安裝 DeepAgents SDK (假設已在環境中或透過 pip 安裝)
pip install deepagents tavily-python
```

### 2. API Server 配置
```bash
cd Dynamic_Web/Api_Server
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn bcrypt pydantic
```

### 3. 前端 SSSTI Web 配置
```bash
cd Dynamic_Web/SSSTI_Web
bun install
```

---

## LMM 引擎 (llama.cpp) 部署

本專案依賴 `llama.cpp` 作為本地模型的推論引擎。

1. **取得 llama.cpp**: 請前往 [llama.cpp 官方 GitHub 儲存庫](https://github.com/ggml-org/llama.cpp) 下載預編譯版本或參考其說明進行編譯。
2. **啟動伺服器**: 
   啟動支援 OpenAI 相容介面的模型（以 Gemma 為例）：
   ```bash
   ./build/bin/llama-server -hf unsloth/gemma-4-E4B-it-GGUF:Q8_0 -ngl -1 -c 64000 --port 8080
   ```

---

## 服務啟動指南 (How to Run)

請分別在三個終端機視窗中啟動以下服務：

### 1. 啟動 Agent Server
```bash
cd Agent_Server
source .venv/bin/activate
python agent.py
```

### 2. 啟動 API Server
```bash
cd Dynamic_Web/Api_Server
source .venv/bin/activate
python main.py
```

### 3. 啟動前端開發伺服器
```bash
cd Dynamic_Web/SSSTI_Web
bun dev
```

---

## 知識庫 (LLM Wiki) 規範

系統的知識庫位於 `Agent_Server/knowledge-base`，嚴格遵守 `AGENTS.md` 的行為契約。
- **Raw 層 (`raw/`)**: 由人類管理，包含原始文獻、筆記與圖片，AI 僅能唯讀。
- **Wiki 層 (`wiki/`)**: 由 Agent 自主管理，包含 `concepts`、`entities`、`sources` 與 `synthesis`，強制使用英文小寫連字符 (Slug) 進行 Wikilink 連結。

您可以透過上傳檔案或對 Agent 下達 `ingest`、`query`、`lint` 等指令來維護此系統。
