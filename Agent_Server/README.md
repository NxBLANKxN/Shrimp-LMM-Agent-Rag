# Shrimp-LMM-Agent-Rag: Agent_Server

這是智慧蝦隻養殖知識庫 Agent 後端。系統採用 llm-wiki 模式：原始資料保存在 `knowledge-base/raw/`，Agent 將可長期複用的知識整理到 `knowledge-base/wiki/`，查詢與健康檢查輸出放在 `knowledge-base/output/`。

## 目錄重點

```text
Agent_Server/
├── .deepagents/
│   ├── AGENTS.md
│   ├── skills/
│   │   ├── wiki-ingest/
│   │   ├── wiki-query/
│   │   ├── wiki-lint/
│   │   ├── wiki-merge/
│   │   └── wiki-reflect/
│   └── tools/
│       ├── wiki_tools.py
│       └── qmd_tools.py
├── agent.py
└── knowledge-base/
    ├── raw/
    ├── wiki/
    ├── output/
    └── scripts/
```

## 環境需求

- Python 3.11+
- 本地 OpenAI-compatible LLM server，預設 `http://localhost:8080/v1`
- 或設定雲端 OpenAI-compatible API：`OPENAI_BASE_URL`、`OPENAI_API_KEY`、`MODEL_NAME`

安裝依賴：

```bash
pip install deepagents python-dotenv fastapi uvicorn langchain-openai python-multipart sse-starlette pymupdf pyyaml
```

`qmd` 語意索引是選配；若未安裝，Agent 會回退使用 `search_wiki` 關鍵字搜尋。

## 設定

在 `Agent_Server/` 建立 `.env`：

```env
PORT=8001
LLAMA_URL=http://localhost:8080/v1
LLAMA_MODEL=gemma-4-E4B-it-GGUF:Q8_0
LOCAL_LLM_ENABLED=1

OPENAI_BASE_URL=
OPENAI_API_KEY=
MODEL_NAME=
```

若 `LOCAL_LLM_ENABLED=1` 且本地 `/models` 可連線，系統會使用本地模型；否則會切到雲端設定。

## 啟動

在 `Agent_Server/` 目錄執行：

```bash
python -m uvicorn agent:app --host 0.0.0.0 --port 8001 --reload
```

或：

```bash
python agent.py
```

前端聊天頁目前直接呼叫 `http://127.0.0.1:8001/chat`，因此 Agent server 需要跑在 8001，除非同步修改前端設定。

## Skills

目前實際啟用的 skills：

| Skill | 用途 |
|---|---|
| `wiki-ingest` | 攝取 PDF/文字來源，寫入 `wiki/sources/`、相關 concepts/entities，並更新 log |
| `wiki-query` | 先查 wiki，再回答問題 |
| `wiki-lint` | 檢查 wiki frontmatter、wikilinks、索引與資料完整性 |
| `wiki-merge` | 經使用者確認後合併重複概念或實體 |
| `wiki-reflect` | 跨文獻綜合分析與知識盲區整理 |

詳細行為契約以 `.deepagents/AGENTS.md` 與各 `SKILL.md` 為準。

## 維護

執行 wiki lint：

```bash
python knowledge-base/scripts/lint.py
```

報告會寫入 `knowledge-base/output/lint-YYYY-MM-DD.md`。
