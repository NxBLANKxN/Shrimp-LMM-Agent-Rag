# AGENTS.md — 蝦隻養殖 AI 知識系統行為契約

## 系統概述

智慧蝦隻養殖 AI 知識系統，採用 **Karpathy llm-wiki 模式**：知識不是在每次問答時從頭檢索，而是由 Agent 持續維護一個結構化的 Markdown wiki，知識隨時間**累積複利**。

### 三層架構

| 層級 | 路徑 | 擁有者 | 權限 |
|---|---|---|---|
| **Raw Sources** | `knowledge-base/raw/` | 人類 | Agent **只讀所有資料夾與檔案**，絕不修改 |
| **Wiki** | `knowledge-base/wiki/` | Agent | Agent 完全讀寫 |
| **Outputs** | `knowledge-base/output/` | Agent | Agent 完全讀寫 |

---

## 目錄結構

每次執行前請使用 `ls` 完全掃描知識庫裡面每一層的檔案與資料夾

```
knowledge-base/
    ├── output/
    │   ├── lint.md                          # lint 報告
    │   └── query.md                         # 查詢結果
    ├── raw/                                 # ⛔ Agent 唯讀所有資料夾與檔案
    │   ├── articles/
    │   ├── audio/
    │   ├── clippings/
    │   ├── datasets/
    │   ├── documents/
    │   ├── images/
    │   ├── notes/
    │   ├── observations/
    │   ├── pdfs/
    │   ├── personal/                        # 個人寫作走特殊流程
    │   └── videos/
    ├── scripts/
    │   ├── lint.py                          # 9 項健康檢查
    │   └── qmd-reindex.sh
    └── wiki/                                # ⭐ Agent 維護的知識庫核心
        ├── QUESTIONS.md                     # 開放問題（graph-excluded）
        ├── concepts/                        # 概念定義頁（英文 slug 命名）
        ├── entities/                        # 實體頁（英文 slug 命名）
        ├── index.md                         # 全索引（graph-excluded）
        ├── log.md                           # 操作日誌（graph-excluded，append-only）
        ├── overview.md                      # Health Dashboard（graph-excluded）
        ├── sources/                         # 來源摘要頁（英文 slug 命名）
        ├── synthesis/                       # 跨來源合成
        └── templates/                       # 頁面模板（Agent 勿直接修改）
```

---

## 可用工具

### 📖 Wiki 操作工具
| 工具 | 用途 |
|------|------|
| `read_wiki_file` | 讀取 wiki/ 任意 .md 檔 |
| `list_wiki_files` | 列出所有頁面及首行摘要 |
| `write_wiki_file` | 建立或覆蓋 wiki/ 中的 .md 檔 |
| `append_log` | 向 wiki/log.md 追加記錄（append-only）|
| `search_wiki` | grep 搜尋 wiki 關鍵字 |
| `run_lint` | 執行 scripts/lint.py 健康檢查 |

### 📄 原始資料工具
| 工具 | 用途 |
|------|------|
| `read_pdf_text` | 讀取 PDF 純文字（前 15000 字）|
| `overwrite_file` | 覆蓋 wiki/ 外的檔案（如 output/lint.md）|

### 🔍 語意搜尋工具
| 工具 | 用途 |
|------|------|
| `qmd_query` | BM25 + 向量混合搜尋（模糊語意）|
| `qmd_status` | 查看 qmd 索引狀態 |
| `qmd_reindex` | 重建 qmd 索引 |

---

## 三大操作模式

| 觸發詞 | 操作 | Skill |
|---|---|---|
| 「整理」、「ingest」、「攝取」、上傳檔案 | **INGEST** | `skills/wiki-ingest/SKILL.md` |
| 任何問題（預設）| **QUERY** | `skills/wiki-query/SKILL.md` |
| 「lint」、「檢查」、「健康檢查」| **LINT** | `skills/wiki-lint/SKILL.md` |
| 「reflect」、「綜合分析」、「發現規律」| **REFLECT** | `skills/wiki-reflect/SKILL.md` |
| 「merge」、「去重」、「這兩個是一樣的」| **MERGE** | `skills/wiki-merge/SKILL.md` |

> 詳細 SOP 請參閱各 Skill 的 SKILL.md 文件。

---

## Wikilink 鐵律（不可違反）

所有 wikilink 目標**必須**使用英文小寫連字符格式：

```
✅ [[biofloc-technology]]
✅ [[penaeus-vannamei]]
✅ [[high-density-aquaculture]]

❌ [[生物絮技術]]   ← 中文詞彙
❌ [[BioFlocTech]]  ← 駝峰
❌ [[biofloc_tech]] ← 底線
```

**中文名稱的處理方式：**
- 寫入 concept/entity frontmatter 的 `aliases` 陣列
- concept 頁正文第一行用括號標注：`生物絮技術（Biofloc Technology）`
- Wikilink **永遠用英文 slug**

**允許使用 wikilinks 的場景：**
- concept 頁 → 其他 concept/entity 頁
- source 頁 → concept/entity 頁
- synthesis 頁 → concept/source/entity 頁

**禁止使用 wikilinks 的場景：**
- 任何頁面不得引用系統文件：`[[log]]`、`[[index]]`、`[[overview]]`
- log.md 內部只用純文字路徑（如 `wiki/sources/xxx.md`）

---

## 語言規範

- **wiki 層**（concept/entity/synthesis）統一用**繁體中文**寫作
- concept 頁 `title` 欄位使用中文主名稱（Obsidian 圖谱節點顯示）
- **slug（檔案名）**統一英文小寫連字符，不使用中文檔案名
- `aliases` 欄位覆蓋該概念的中英文所有叫法

---

## Confidence 更新規則

| 來源數量 | Confidence | 行為 |
|---|---|---|
| 1 個來源 | `low` | 自動設置 |
| 3+ 個來源 | `medium` | 自動設置 |
| 5+ 且無重大矛盾 | 候選 `high` | 向使用者展示 Definition 和 Sources，**等待確認** |
| 使用者明確回覆「確認」或「ok」| `high` | 才可設置 |

⚠ 個人寫作（`raw/personal/`）**不計入** source_count。

---

## Source Integrity 規則

- re-ingest：若 lint 報告 `⚠ SOURCE MODIFIED`，需重新攝取並更新所有受影響頁面
- 來源超過 2 年：設 `possibly_outdated: true`，摘要末尾加警示
- 矛盾來源：必須在 source 頁和 concept 頁的 `## Contradictions` 節**顯式記錄**，不得靜默覆蓋

---

## 系統文件隔離規則

以下文件的 frontmatter 必須含 `graph-excluded: true`：
- `wiki/log.md`
- `wiki/index.md`
- `wiki/overview.md`
- `wiki/QUESTIONS.md`
- `wiki/output/` 下所有文件

---

## 五大核心原則

1. **Query-First**：回答問題前必須先查 `index.md` + `QUESTIONS.md`
2. **raw/ 唯讀**：絕不修改 raw/ 目錄下的任何檔案
3. **每次操作都記 Log**：Ingest / Query / Lint 都必須在 `log.md` 留下記錄
4. **交叉連結是義務**：任何新頁面都必須與相關 concept/entity/source 頁互相連結
5. **index.md 必須保持最新**：每次 Ingest 完都要更新 index.md

### INGEST 完成定義（避免「只讀 PDF、目錄仍空」）

當使用者要求攝取／寫入／依 ingest 流程處理時，**同一回合結束前**至少須：

- 成功 `write_wiki_file` 建立或更新 **`sources/<slug>.md`**（每個處理的來源一份；可再擴充 concepts／entities）
- 成功 **`append_log`**（`ingest`）

僅輸出摘要、僅呼叫 `read_pdf_text`／`sha256_file`、或只請使用者「確認後再寫」**不算** ingest 完成（除非使用者明確只要預覽）。細節以 `skills/wiki-ingest/SKILL.md` Step 3 分岔為準。

---

## 子代理設計說明

目前採用**單一主代理 + Skill 分流**架構，無需啟用子代理。

| 未來子代理 | 啟用條件 |
|---|---|
| IngestAgent | 知識庫 > 200 篇原始文獻，需批次處理 |
| QueryAgent | 高頻查詢場景，需快取常見答案 |
| LintAgent | 需要排程自動執行健康檢查 |
