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

### 1. 建立虛擬環境
建議在專案目錄下建立虛擬環境以隔離套件：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安裝 GPU 版 PyTorch (torch)
針對 CUDA 12.6 安裝對應的 PyTorch 版本：

```bash
pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu126
pip install python-dotenv fastapi uvicorn langchain langchain-google-genai langchain-openai sse-starlette pymupdf
```

---

## CUDA 工具包與編譯環境 (CUDA Toolkit & Compilation)

### 1. 檢查 CUDA 版本
確保驅動程式與工具包版本正確：

```bash
nvidia-smi
```

### 2. 安裝 CUDA Toolkit
若尚未安裝，請前往 [NVIDIA 官網下載](https://developer.nvidia.com/cuda-toolkit-archive) 並安裝對應版本。

### 3. 設定環境變數
將 CUDA 加到 `~/.bashrc` 或目前的終端機 Session（請將 `[版本號]` 替換為 `12.6` 或您的實際版本）：

```bash
export PATH=/usr/local/cuda-[版本號]/bin:$PATH
```

---

## llama.cpp Server 建置與部署

本專案使用 `llama.cpp` 提供本地 LMM 介面。

### 1. 編譯建置 (Build)
下載並啟用 CUDA 硬體加速進行編譯：

```bash
# Clone 儲存庫
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp/

# 執行 CMake 編譯 (開啟 GGML_CUDA)
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j $(nproc)
```

### 2. 啟動伺服器 (Server Startup)
使用 Hugging Face 權重啟動服務，此指令會自動下載模型：

```bash
./build/bin/llama-server -hf unsloth/gemma-4-E4B-it-GGUF:Q8_0 -ngl -1 -c 64000 --port 8080
```

#### 參數說明：
- `-hf`: 從 Hugging Face 自動載入模型位址。
- `-ngl -1`: 將所有的模型層 (Layers) 卸載到 GPU 上執行 (Offload)。
- `-c 64000`: 設定上下文視窗大小為 64,000 tokens。
- `--port 8080`: 設定 API 服務監聽端口。

---

## 服務啟動指南 (How to Run)

在確保 `llama.cpp` Server 已經在 `8080` 端口運行的前提下，請開啟多個終端機分別啟動以下服務：

### 1. 啟動 Agent Server
此服務將載入 DeepAgents 工具與 LLM Wiki 工具集：
```bash
cd Agent_Server
source ../.venv/bin/activate
python agent.py
# 預設運行於 http://localhost:8001
```

### 2. 啟動 API Server
```bash
cd Dynamic_Web/Api_Server
source ../../.venv/bin/activate
python main.py
```

### 3. 啟動前端開發伺服器
```bash
cd Dynamic_Web/SSSTI_Web
bun install
bun dev
```

---

## 知識庫 (LLM Wiki) 規範

系統的知識庫位於 `Agent_Server/knowledge-base`，嚴格遵守 `CLAUDE.md` 的行為契約。
- **Raw 層 (`raw/`)**: 由人類管理，包含原始文獻、筆記與圖片，AI 僅能唯讀。
- **Wiki 層 (`wiki/`)**: 由 Agent 自主管理，包含 `concepts`、`entities`、`sources` 與 `synthesis`，強制使用英文小寫連字符 (Slug) 進行 Wikilink 連結。

您可以透過上傳檔案或對 Agent 下達 `ingest`、`query`、`lint` 等指令來維護此系統。
