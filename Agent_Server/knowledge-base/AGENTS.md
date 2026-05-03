# AGENTS.md

# 系統概覽
- 三層架構說明（Raw/Wiki/Outputs）
- 核心原則：你完全擁有 `wiki/` 目錄的讀取和寫入權限，`raw/` 目錄由我（人類）擁有，你只能讀取，絕不修改（Raw 層不可變原則）。
- **LangChain DeepAgent 工具結合**：
  在執行以下操作時，請務必優先使用提供的自訂工具：
  - 讀取檔案：`read_wiki_file`
  - 寫入檔案：`write_wiki_file`
  - 追加日誌：`append_log`
  - 關鍵字搜尋：`search_wiki`
  - qmd 查詢與狀態：`qmd_query`, `qmd_status`, `qmd_reindex`
  - 執行檢查：`run_lint`

# INGEST 操作規範
觸發詞：ingest、攝入、處理這個

來源類型判斷（優先級由高到低）：
1. frontmatter 含 type: personal-writing → 走「個人寫作」流程
2. 檔案路徑包含 `raw/personal/` → 走「個人寫作」流程
3. frontmatter 含 type: pdf-reference → 走「PDF 參考」流程
4. 其他 → 走「外部來源」標準流程

缺少 frontmatter 時的處理規則：
- 從檔案第一個 `#` 標題提取 title；若無標題則從檔名推斷
- source 欄位留空，在 `wiki/sources/<slug>.md` 中標註「來源未知」
- date 使用檔案系統修改時間
- 不中斷 INGEST，但使用 `append_log` 在 `log.md` 記錄「警告：來源檔案缺少標準 frontmatter」

**外部來源標準流程（12 步）**：
1. 讀取目標原始來源（`raw/` 中的檔案，唯讀）
2. 計算原始檔案的 SHA-256 哈希（Python hashlib），此為 SHA-256 哈希記錄規則。
3. 與使用者確認核心要點（逐一攝入，保持參與感）。
4. **INGEST 去重檢測（含 canonical_source 譯文檢測）**：檢查 URL 及標題，若為已有來源的譯文，請填入 `canonical_source`，避免重複產生知識節點。
5. 生成 slug（小寫英文，用連字符，例如 `attention-is-all-you-need`）。
6. 使用 `write_wiki_file` 建立 `wiki/sources/<slug>.md`（使用 source-template.md），frontmatter 中寫入：
   - `raw_file`: 相對路徑
   - `raw_sha256`: SHA-256 哈希值
   - `last_verified`: 攝入日期（YYYY-MM-DD）
   - 若來源發表日期超過 2 年前：標註 `possibly_outdated: true`
7. **概念名稱對齊檢查**（提取概念之前必須執行）：
   - 將每個提取到的概念名稱統一映射為英文小寫連字符 slug
   - 在 `wiki/concepts/` 中查找該 slug 是否已存在
   - **同時檢查所有已有 concept 頁的 `aliases` 欄位**（`aliases` 匹配），支援中英文別名。
   - 若找到：更新已有頁面，不建立新頁面
   - 若找不到：建立新頁面，並在 `aliases` 同時填入中文名和英文名。
8. 針對每個概念/實體：
   - 若存在：更新並追加新來源引用，於 Evolution Log 追加紀錄，更新 source_count 和 confidence，**同時更新 last_reviewed**。
   - 格式：`- YYYY-MM-DD（N sources）：[本次認知變化的一句話描述]`
9. 更新 `wiki/index.md`：將來源從 Unprocessed 移動到 Processed。
10. **QUESTIONS.md 匹配檢查**：讀取 `wiki/QUESTIONS.md`，檢查本次來源是否能回答開放問題：
    - 若能：提示使用者「此來源可能回答了開放問題：[問題描述]，是否立即執行 QUERY？」
    - 確認後，執行 QUERY 並寫入 `wiki/synthesis/`。
11. 使用 `append_log` 記錄：`YYYY-MM-DD HH:MM | ingest | [來源標題]`。
12. **最後一步執行 qmd update**：呼叫 `qmd_reindex` 工具，確保索引與最新檔案同步。

**特殊情況：URL 直接輸入**
- 若使用者直接輸入 URL 進行 INGEST，必須自動呼叫 **defuddle 工具（URL 直接輸入的 defuddle 調用規則）** 抓取網頁內容並轉為 markdown 存入 `raw/articles/`，接著執行標準 INGEST 流程。

**個人寫作流程**：
- 不生成 Summary 節，核心論點寫入 concept 頁的 ## My Position（標註個人認知）。
- 不參與 confidence 的 source_count 計數。

# QUERY 操作規範
觸發詞：直接提問，或「根據我的知識庫」

執行步驟：
1. **優先使用 qmd_query 工具**：執行 `qmd_query(問題)` 獲取相關頁面（若 qmd 報錯，則 Fallback 呼叫 `list_wiki_files` 和 `read_wiki_file("index.md")`）。
2. 逐一完整讀取前 5 個相關檔案 (`read_wiki_file`)。
3. 產生答案，每個核心結論必須溯源到具體 `wiki/sources/<slug>.md`（**來源溯源要求**）；註明信心級別；矛盾時顯式標註分歧。
4. **高價值答案持久化規則**：若答案具備複用價值，使用 `write_wiki_file` 寫入 `wiki/outputs/YYYY-MM-DD-<topic>.md`，包含 `graph-excluded: true`。在輸出末尾必須包含「⚠ **Confidence Notes** 輸出要求」節。同時使用 `append_log` 追加紀錄。

# LINT 操作規範
觸發詞：lint、檢查、健康檢查

執行步驟：
1. 呼叫 `run_lint` 工具（執行 `scripts/lint.py`，包含 9 項檢查）。
2. 將報告寫入 `wiki/outputs/lint-YYYY-MM-DD.md`。
3. 呼叫 `qmd_status`，對比索引檔案數與實際 `.md` 檔案數（**執行 qmd 索引同步驗證**）；若落後則呼叫 `qmd_reindex`。
4. 向使用者展示摘要並詢問是否修復。

# REFLECT 操作規範
觸發詞：reflect、綜合分析、發現規律

四階段執行：
Stage 0（反向檢驗）：在生成任何合成結論之前，主動搜尋反駁證據。若無反對來源，在 Limitations 節標註「⚠ 迴音室風險：未找到反駁來源，結論可能存在確認偏差」。
Stage 1（模式掃描）：使用 qmd 或 grep 工具批次掃描。識別跨來源模式、隱性關聯、矛盾對。
Stage 2（深度合成）：對有證據支撐的候選項，完整讀取，寫入 `wiki/synthesis/<topic>-synthesis.md`。
Stage 3（Gap Analysis）：
- 分析 source_count = 1 且建立超過 30 天的孤立概念、隱性盲區、覆蓋稀薄領域。
- 輸出到 `wiki/outputs/gap-report-YYYY-MM-DD.md`。

# MERGE 操作規範
觸發詞：merge、去重

- 主 slug 保留，被合併頁面的 wikilinks 全部更新。
- **跨語言合併專項流程（redirect 檔案保留）**：主 slug 保留英文，aliases 取聯集，My Position 向使用者展示對比後合併。被合併的舊 slug 檔案保留為 redirect 檔案（如 `redirect: [[wiki/concepts/主slug]]`）。

# ADD-QUESTION 操作規範
觸發詞：我想搞清楚、add question、記錄一個問題
- 規範化問題後，追加到 `wiki/QUESTIONS.md`（checkbox 格式）。
- 呼叫 `append_log` 記錄。

# Wikilink 使用規範
**格式鐵律（不可違反）**：所有 wikilink 目標必須使用英文小寫連字符格式。✅ `[[value-investing]]` ❌ `[[價值投資]]`
**Wikilink 禁止清單**：任何頁面不得引用系統文件（`log`, `index`, `overview`, `QUESTIONS`，或 lint 報告，或操作名稱）。

# Wiki 語言規範
- Wiki 層（concept/entity/synthesis）統一用**繁體中文**寫作。
- concept 頁 title 欄位使用中文主名稱。英文術語首次出現時括號標註。
- 所有 slug（檔名）統一用英文小寫連字符。
- `aliases` 欄位涵蓋中英文所有叫法（跨語言）。

# Confidence 更新規則
- 1 個來源：low
- 3+ 個來源：medium
- **confidence: high 必須使用者確認，禁止自動晉升**。

# Source Integrity Rules
- 若 lint 報告 ⚠ SOURCE MODIFIED，需重新攝入該檔案並更新所有受影響頁面。
- 來源超過 2 年標註 `possibly_outdated: true`。

# 系統檔案隔離規則
以下檔案的 frontmatter 必須含 `graph-excluded: true`：`log.md`, `index.md`, `overview.md`, `QUESTIONS.md`, `outputs/` 下所有檔案。

# 文檔維護規則
當 `CLAUDE.md` 規則更新時，同步更新 `USER_GUIDE.md` 對應章節，確保兩份文件一致。
