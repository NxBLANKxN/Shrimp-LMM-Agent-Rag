---
type: system-test-report
graph-excluded: true
date: 2026-04-29
---

# Skill E2E 測試報告（自然語言觸發）

## 測試範圍
- `wiki-ingest`
- `wiki-query`
- `wiki-lint`
- `wiki-reflect`
- `wiki-merge`

## 測試方式
- 透過 `/chat` API 使用自然語言觸發各 skill。
- 觀察 SSE 狀態流（tool call 與模型回應）。
- 檢查實際產物（`wiki/sources`, `wiki/concepts`, `wiki/entities`, `wiki/synthesis`, `output/lint.md`）。

## 測試輸入與觀察

### 1) wiki-ingest
- 輸入：`幫我攝取並分析現在有的PDF資料，請依照既有skills流程處理並寫入知識庫`
- 觀察到的流程：
  - 有讀取 `wiki-ingest` skill。
  - 有掃描 `raw/`，找到 4 份 PDF。
  - 有呼叫 `read_pdf_text`、`sha256_file`。
  - 有產出「請使用者確認摘要」回覆。
- 問題：
  - 沒有看到 `write_wiki_file` 寫入 `sources/`、`concepts/`、`entities/` 的穩定完成訊號。
  - 測試在長串流中超時，未完成 end-to-end 寫入。

### 2) wiki-query
- 輸入：`根據目前知識庫，生物絮技術對蝦養殖有什麼好處？請引用來源`
- 觀察到的流程：
  - 先走 `qmd_query`，再嘗試 `search_wiki`、`list_wiki_files`。
  - 最終回覆「目前知識庫尚未攝取相關文獻」。
- 問題：
  - 與現況不一致：`raw/articles` 有 PDF，但 wiki 層缺正式來源頁，導致查詢降級為「無可引用來源」。

### 3) wiki-lint
- 輸入：`請幫我做一次wiki健康檢查，輸出lint報告`
- 觀察到的流程：
  - 有呼叫 `run_lint`，但回報 `yaml` 模組缺失（工具執行環境依賴問題）。
  - Agent 改走手動 lint 推理，發現 index 與實際目錄不同步。
  - 嘗試寫報告時先用 `write_file`（工具不匹配），後續流程未完整收斂。
- 問題：
  - `run_lint` 依賴在 agent 執行環境未滿足。
  - 工具選用不穩定（`overwrite_file` vs `write_file`）。

### 4) wiki-reflect
- 輸入：`請根據目前知識庫做一次綜合分析，找出跨來源規律並寫成synthesis`
- 觀察到的流程：
  - 有讀 `wiki-reflect` skill 並建立待辦。
  - 發現 wiki 內容目錄為空後，轉而想先 ingest 再 reflect。
  - 進入長鏈計畫與摘要，最終超時。
- 問題：
  - 前置條件不滿足（wiki 無 sources/concepts/entities 內容）。
  - 流程缺「前置檢查失敗就快速返回」機制，導致任務漂移與超時。

### 5) wiki-merge
- 輸入：`幫我檢查概念有沒有重複，若重複請merge並更新引用`
- 觀察到的流程：
  - 有讀 `wiki-merge` skill。
  - 先嘗試 `run_lint`（同樣遇到 yaml 依賴問題）。
  - 改手動檢查後判定：`index.md` 與實際 wiki 目錄不一致，無可 merge 目標。
  - 有給出合理結論與後續建議（先 ingest）。

## 實際產物檢查（測試後）
- `wiki/sources`: 0 files
- `wiki/concepts`: 0 files
- `wiki/entities`: 0 files
- `wiki/synthesis`: 0 files
- `output/lint.md`: 仍為空檔

## 結論
- 技能觸發本身可用（自然語言可命中對應 skill）。
- 主要失敗不在「觸發」，而在「流程收斂與落地」：
  1. 前置依賴缺失（`run_lint` 的 yaml）。
  2. 前置條件未滿足時未快速 fail-fast（導致長鏈漂移）。
  3. ingest 流程雖能讀 PDF 與算 SHA，但未穩定走到 wiki 寫入完成。

## 建議下一步
1. 修 `run_lint` 執行環境依賴（或在工具內做依賴檢查與可讀錯誤回傳）。
2. 在 `wiki-reflect` / `wiki-merge` 加 fail-fast：若 `sources` 為空，直接回「需先 ingest」。
3. 為 `wiki-ingest` 加完成門檻：未產生 `sources/*.md` 不可回覆完成。

---

## 補記（2026-04-30）：與本報告「測試方式」的對照

本報告 **§測試方式** 定義的是：**`/chat` + 自然語言 + SSE + 事後檢查產物目錄** 的 skill E2E（五條輸入各一輪）。

**2026-04-30 另一次驗證**（自動化／模組層）**沒有**重跑上述五條自然語言全路徑；改跑的是：

| 項目 | 是否等同本報告 E2E | 說明 |
|------|-------------------|------|
| `compileall`、`lint.py`、`qmd_*` / `wiki_*` 直接 `invoke` | 否 | 驗證工具與依賴，**不**經由 agent 選 tool、也不看 SSE |
| `import agent`、`TestClient GET /status` | 否 | 僅啟動層與靜態路由 |
| `TestClient` 對 `POST /chat` 串流直到 `[DONE]`（極短使用者句） | **部分** | 僅證明 **SSE + 雲端 LLM 一輪對話** 可走完；**未**依 §測試輸入逐條驗證 ingest/query/reflect/merge |

**產物目錄（2026-04-30 檢查）**：`wiki/sources`、`wiki/concepts` 內仍 **0** 份正式內容頁（與本報告 §實際產物檢查 結論一致）；代表 **ingest 落地問題尚未因工具層修補而自動消失**，仍需依 §建議下一步 用 **行為／gate** 或再跑一輪完整 **§測試輸入** 的 `/chat` E2E 驗收。

若要補齊與本報告同級的證據：請再用同一組五句自然語言打 `/chat`，並在每次回合後複查 `wiki/sources` 等目錄與 `output/lint.md`。
