這是一份為你的 **Agent_Server** 量身打造的 `README.md`。它將 **Shrimp-LMM-Agent-Rag** 的核心理念、Karpathy 的 **Wiki 架構** 以及你的 **技術棧** 完美整合。

---

# 🦐 Shrimp-LMM-Agent-Rag: Agent_Server

這是一個基於 **YOLOv11 OBB (Oriented Bounding Boxes)** 與 **大型多模態模型 (LMM)** 的智慧養殖監測系統後端。本系統採用 **Andrej Karpathy 的 LLM-Wiki 模式**，旨在將即時的影像觀測轉化為具備結構化、可檢索性的長期養殖知識庫。

## 🌟 核心理念：知識優先 (Knowledge-First)
本系統不只是執行推論的工具，它是一個**自我演進的知識體系**。
- **事實 (Raw)**：YOLO 產出的定量數據是觀測事實。
- **記憶 (Wiki)**：LMM 診斷後的報告是系統記憶。
- **憲法 (AGENTS.md)**：所有技能執行前必須檢索知識庫，避免重複運算並確保診斷的一致性。

---

## 🏗️ 知識庫架構 (Knowledge-Base Structure)

依照 `AGENTS.md` 規範，系統嚴格區分數據層級：

```text
<project-root>/Agent_Server
├── .deepagents/                        # 🤖 Agent 行為定義核心
│   ├── AGENTS.md                       # 行為管理規範
│   └── skills/                         # 封裝技能組 (含實作腳本)
│       ├── shrimp-behavior-analysis/   # 專家行為診斷 (LMM)
│       │   ├── SKILL.md
│       │   └── scripts/
│       ├── shrimp-distribution-mapping/# 空間分布映射
│       │   ├── SKILL.md
│       │   └── scripts/
│       ├── shrimp-search/              # 目錄導航與狀態驗證
│       │   ├── SKILL.md
│       │   └── scripts/
│       └── shrimp-tracking/            # 數位觀測事實生產 (YOLO)
│           ├── SKILL.md
│           └── scripts/
├── .env                                # 執行環境變數
├── README.md                           # 本說明文件
├── agent.py                            # 系統主程式
└── knowledge-base/                     # 🧠 全量數據與知識核心
    ├── README.md                       # 知識庫索引說明
    ├── output/                         # 系統檢測報告
    │   ├── lint.md                     # Wiki 鏈結檢查結果
    │   └── query.md                    # 檢索答案產出
    ├── raw/                            # 事實數據層 (事實)
    │   ├── articles/                   # 文獻資料
    │   ├── clippings/                  # 原始影像素材 (上傳入口)
    │   ├── images/                     # 靜態圖檔
    │   ├── notes/                      # 隨手筆記
    │   ├── observations/               # YOLO 數位觀測事實 (JSON/Frames)
    │   ├── pdfs/                       # 參考文檔
    │   └── personal/                   # 個人化設定
    ├── scripts/                        # 維護工具組
    │   ├── lint.py                     # 知識庫完整性校驗
    │   └── qmd-reindex.sh              # RAG 索引重建
    └── wiki/                           # 知識合成層 (記憶)
        ├── QUESTIONS.md                # 待解問題隊列
        ├── concepts/                   # 養殖模式與行為定義
        ├── entities/                   # 工具與設備定義
        ├── index.md                    # 知識庫索引
        ├── log.md                      # 操作日誌 (Graph-Excluded)
        ├── overview.md                 # 系統高層綜述
        ├── sources/                    # 診斷報告 (Source Pages)
        ├── synthesis/                  # 跨場域合成分析
        └── templates/                  # LLM 寫作模板
            ├── concept-template.md
            ├── entity-template.md
            ├── personal-writing-template.md
            ├── source-template.md
            └── synthesis-template.md
```

---

## 🚀 快速開始 (Quick Start)

### 1. 環境需求
- **Python**: 3.11+
- **CUDA**: 12.1+ (建議用於 YOLOv11 運算)
- **核心依賴**:
  ```bash
  pip install deepagents tavily-python python-dotenv fastapi uvicorn \
              langchain_openai python-multipart sse-starlette ultralytics \
              opencv-python pymupdf
  ```

### 2. 環境變數設定
在 `Agent_Server/` 目錄下建立 `.env`：
```env
OPENAI_API_KEY=
OPENAI_BASE_URL=
MODEL_NAME=
PORT=
WORKSPACE=
UPLOADS_DIR=
AGENT_DIR=
SKILLS_DIR=
```

### 3. 啟動服務
```bash
python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🛠️ 核心技能 (Agent Skills)

| 技能名稱 | 職責 | 遵守規範 |
| :--- | :--- | :--- |
| **shrimp-search** | 檔案與 Wiki 狀態檢索 | 使用 `ls` 快速驗證事實是否存在，落實知識優先。 |
| **shrimp-tracking** | YOLO OBB 事實生產 | 將結果寫入 `raw/observations/`，建立數位觀測記錄。 |
| **behavior-analysis** | 多模態行為診斷 | 解析觀測事實，自動套用模板撰寫 `wiki/sources/`。 |
| **wiki-management** | 知識庫維護 | 確保所有報告均有正確的 Wikilinks 與元數據。 |

---

## 🔍 自動化維護 (Maintenance)

為了確保知識庫的健康度，系統包含自動化腳本：
- **`scripts/lint.py`**: 執行 9 項健康檢查（包括 Broken Links、缺少 SHA-256、孤立概念等）。
- **`scripts/qmd-reindex.sh`**: 重建 `qmd` 索引，確保 RAG 檢索的即時性。

---

## ⚖️ 行為契約 (Behavioral Contract)
本專案的所有行為受 `Agent_Server/.deepagents/AGENTS.md` 約束。Agent 在執行任何任務前，必須先檢索知識庫以獲取上下文。

---

## 📝 開發規範
- **路徑**: 必須使用 `os.path.join`，禁止硬編碼路徑。
- **語言**: 診斷報告預設使用 **繁體中文 (Traditional Chinese)**。
- **術語**: 採用 `中文 (English)` 對照格式。