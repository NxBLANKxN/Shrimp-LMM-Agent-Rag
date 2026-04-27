# AGENTS.md — LLM 核心行為契約 (Core Behavioral Contract)

## 一、系統概述 (System Overview)
- **三層架構說明**：
    - **Raw (原始層)**：存放由人類收集的原始文件。LLM 僅具備讀取權限，**絕不修改**。
    - **Wiki (知識層)**：LLM 完全擁有的二階知識庫，負責存儲經過推理與結構化的內容。
    - **Outputs (輸出層)**：存放查詢結果、圖表、幻燈片及健康檢查報告。
- **核心原則**：你完全擁有 `wiki/` 目錄的讀取和寫入權限，你是這個知識花園的園丁。

## 二、INGEST 操作規範 (Ingestion Protocol)
**觸發詞**：`ingest`、`攝入`、`處理這個`

### 來源類型判斷（優先級由高到低）：
1. frontmatter 含 `type: personal-writing` → 走「個人寫作」流程。
2. 文件路徑包含 `raw/personal/` → 走「個人寫作」流程。
3. frontmatter 含 `type: pdf-reference` → 走「PDF 參考」流程。
4. 其他 → 走「外部來源」標準流程。

**缺少 frontmatter 處理規則**：
- 從文件第一個 `#` 標題提取 title。
- source 欄位留空，在 `wiki/sources/<slug>.md` 中標註「來源未知」。
- date 使用文件系統修改時間。
- 在 `log.md` 記錄「警告：來源文件缺少標準 frontmatter」。

### 外部來源標準流程（11 步）：
1. **讀取**目標原始來源（`raw/` 中的文件，只讀）。
2. **計算**原始文件的 SHA-256 哈希。
3. **確認**核心要點（逐一攝入，保持參與感）。
4. **生成** slug（小寫英文、連字符，如 `shrimp-molting-cycle`）。
5. **創建** `wiki/sources/<slug>.md`（使用 `source-template.md`）。
   - 若發表於 2 年前，標註 `possibly_outdated: true`。
6. **概念名稱對齊檢查**（關鍵）：
   - 映射為英文 slug。
   - 遍歷 `wiki/concepts/*.md` 及其 `aliases` 列表。
   - 若匹配到已有頁面：更新已有頁面；若無匹配：創建新頁面並填入中英文 `aliases`。
7. **更新/創建概念**：追加引用、更新 `source_count` 與 `confidence`、更新 `last_reviewed`、追加 **Evolution Log**。
8. **處理實體**：同上述概念邏輯。
9. **更新 index.md**：將來源從 Unprocessed 移動到 Processed。
10. **檢查 QUESTIONS.md**：若能回答開放問題，提示用戶是否執行 QUERY。
11. **記錄日誌**：在 `wiki/log.md` 追加一列。

### 個人寫作流程：
- 不生成 Summary，核心論點寫入 concept 頁的 `## My Position`（標註「個人認知」）。
- 不參與 `source_count` 基準計數。
- 提取外部引用並嘗試建立 wikilinks。

## 三、QUERY 操作規範 (Querying Protocol)
**觸發詞**：直接提問，或「根據我的知識庫」

- **Step Q1**：執行 `qmd query "<問題>" --json` 獲取 top 5。
- **Step Q2**：逐一完整讀取 top 5 文件。
- **Step Q3**：合成答案，必須溯源至 `wiki/sources/`；標註分歧。
- **Step Q4**：寫入 `wiki/outputs/`，更新 `index.md` 與 `log.md`。

## 四、LINT 操作規範 (Linting Protocol)
**觸發詞**：`lint`、`檢查`、`健康檢查`

1. 運行 `scripts/lint.py`。
2. 將報告寫入 `wiki/outputs/lint-YYYY-MM-DD.md` (graph-excluded)。
3. 執行 `qmd status`，若索引落後則執行 `qmd add wiki/`。

## 五、REFLECT 操作規範 (Reflection Protocol)
**觸發詞**：`reflect`、`綜合分析`、`發現規律`

- **Stage 0 (反向檢驗)**：主動搜索反駁證據，若無則標註「回音室風險」。
- **Stage 1 (模式掃描)**：使用 `qmd multi-get` 識別跨來源關聯與隱性盲區。
- **Stage 2 (深度合成)**：寫入 `wiki/synthesis/`。
- **Stage 3 (Gap Analysis)**：識別孤立概念，輸出至 `outputs/`。
- **完成後**：更新 `overview.md` 的 Dashboard 與 `log.md`。

## 六、MERGE 操作規範 (Merging Protocol)
- **同語言**：保留主 slug，舊頁面改為 `redirect: [[slug]]`。
- **跨語言**：保留英文 slug，`aliases` 取聯集，合併 Evolution Log。

## 七、Wikilink 使用規範 (Linking Protocol)
- **格式鐵律**：目標必須使用英文小寫連字符（如 `[[shrimp-biology]]`）。**絕對禁止中文 slug**。
- **Wiki 語言**：正文統一用**繁體中文**寫作，術語首次出現時括號標註英文。

## 八、Confidence 更新規則
| 來源數量 | Confidence | 處理方式 |
| :--- | :--- | :--- |
| 1 個來源 | low | 自動設置 |
| 3+ 個來源 | medium | 自動設置 |
| 5+ 且無矛盾 | 候選 high | 展示並等待用戶確認 |

---

## 📅 初始化驗證報告 (Validation Report)

### 1. 知識庫目錄樹
```text
knowledge-base/
├── raw/ (ReadOnly)
│   ├── articles/
│   ├── clippings/ (Main Entrance)
│   ├── images/
│   ├── pdfs/
│   ├── notes/
│   └── personal/
├── wiki/ (LLM Owned)
│   ├── index.md (Index)
│   ├── log.md (Log)
│   ├── overview.md (Dashboard)
│   ├── QUESTIONS.md (Queue)
│   ├── sources/
│   ├── concepts/
│   ├── entities/
│   ├── synthesis/
│   └── templates/
├── outputs/
└── scripts/
    ├── lint.py
    └── qmd-reindex.sh
```

### 2. 核心模板列表 (wiki/templates/)
- `source-template.md` (14 欄 frontmatter)
- `personal-writing-template.md` (12 欄 frontmatter)
- `concept-template.md` (10 欄 frontmatter)
- `entity-template.md`
- `synthesis-template.md`

### 3. qmd 狀態
已執行 `qmd add wiki/`。當前索引已同步。

### 4. lint.py 檢查項
1. Broken Links 檢查
2. Frontmatter 完整性檢查
3. Aliases 重複檢查
4. Hash 一致性檢查
5. 孤立概念掃描
6. 語言與 Slug 一致性
7. Stale 頁面檢測
8. 矛盾標記檢查
9. Confidence 等級校對