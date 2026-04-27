# Shrimp-LMM-Agent-Rag

本專案旨在結合 **大型多模態模型 (LMM)**、**AI Agent (代理人)** 與 **RAG (檢索增強生成)** 技術，實現智慧化的決策與資料檢索系統。

## 系統需求 (Requirements)

- **OS:** Ubuntu 22.04+ (或相容的 Linux 發行版)
- **Python:** 3.10+
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
pip install python-dotenv
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

### 1. 編譯建置 (Build)
下載並啟用 CUDA 硬體加速進行編譯：

```bash
# Clone 儲存庫
git clone [https://github.com/ggml-org/llama.cpp.git](https://github.com/ggml-org/llama.cpp.git)
cd llama.cpp/

# 執行 CMake 編譯 (開啟 GGML_CUDA)
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j $(nproc)
```

### 2. 啟動伺服器 (Server Startup)
使用 Hugging Face 權重啟動服務，此指令會自動下載模型：

```bash
./build/bin/llama-server -hf bartowski/google_gemma-4-E4B-it-GGUF:Q8_0 -ngl -1 -c 64000 --port 8080
```

#### 參數說明：
- `-hf`: 從 Hugging Face 自動載入模型位址。
- `-ngl -1`: 將所有的模型層 (Layers) 卸載到 GPU 上執行 (Offload)。
- `-c 64000`: 設定上下文視窗大小為 64,000 tokens。
- `--port 8080`: 設定 API 服務監聽端口。
