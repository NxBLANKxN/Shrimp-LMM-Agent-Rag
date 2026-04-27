---
name: shrimp-search
description: 知識庫路徑導航與狀態監測專家。底層透過跨平台目錄指令快速掃描 `knowledge-base`，驗證「原始素材」、「觀測數據」與「Wiki 頁面」的完整性。
---

# 技能：知識庫路徑搜索與狀態監測 (Shrimp Search - Cross Platform)

## 0. 路徑基準與跨平台原則

1. **路徑基準 (Base Path)**：
   - 一律先定位專案根目錄，再使用相對路徑：`Agent_Server/knowledge-base/`。
   - 禁止硬編碼 `/opt/...` 或特定機器絕對路徑。

2. **預設工作目錄 (Working Directory)**：
   - 若當前目錄是專案根目錄，使用 `Agent_Server/knowledge-base`。
   - 若當前目錄是 `Agent_Server`，使用 `knowledge-base`。
   - 若都不成立，先回報「找不到 knowledge-base」，中止後續掃描。

3. **命令選擇 (Command Selection)**：
   - Linux/WSL/macOS shell：可用 `ls -R`、`ls -lh`、`ls -F`。
   - PowerShell：改用 `Get-ChildItem`，不可使用 `ls -F`。

## 1. 核心功能 (Core Functions)

1. **高效目錄掃描 (High-Speed Listing)**：
   - **底層機制**：使用相容當前 shell 的列表指令，快速獲取 `Agent_Server/knowledge-base/` 下的檔案樹。
   - **掃描重點（含 fallback）**：
     - 原始素材：優先 `raw/clippings/`，若不存在則改掃 `raw/articles/`。
     - 觀測數據：`raw/observations/`（若不存在，標記為 `UNINITIALIZED`，不可當作執行失敗）。
     - 知識來源：優先 `wiki/sources/`，若不存在則 fallback 到 `wiki/`（排除系統頁與 `templates/`）。

2. **智慧路徑補完 (Path & Slug Guidance)**：
   - 當 Agent 接收到不完整的檔名時，透過列表指令搜尋匹配路徑。
   - 將搜尋結果轉化為標準 **Slug**（如 `tank_a.mp4` -> `tank-a`），用於跨目錄檢索。
   - Slug 正規化規則：小寫、底線轉連字號、空白轉連字號、移除副檔名。

3. **觀測事實校驗 (Observation Check)**：
   - **關鍵決策**：在執行 YOLO 推論前，先檢查 `raw/observations/{slug}/analysis_results.json` 是否存在。
   - 若檔案存在，強制 Agent 跳過 `shrimp-tracking`，直接調用診斷工具。

## 2. 互動邏輯 (Interaction Logic)

1. **初始狀態掌握 (Initial State)**：
   啟動時自動掃描素材區、觀測區、知識來源區，回報四態清單與空目錄提示。

2. **隱藏雜訊 (Noise Reduction)**：
   - 過濾 `.` 開頭的隱藏檔與 `.gitkeep`。
   - 僅向使用者呈現具備領域價值的格式（`.mp4`, `.jpg`, `.json`, `.md`）。

3. **空目錄回報規範 (Empty Folder Reporting)**：
   - 若目錄存在但沒有符合條件的檔案，固定回覆：`<資料夾路徑> 底下是空的`。
   - 範例：`raw/observations 底下是空的`、`wiki/sources 底下是空的`。

4. **路徑回報規範 (Path Reporting)**：
   - **對外 (User)**：顯示簡潔的路徑與檔案大小（如 `raw/observations/tank-a/ (45 frames, 1.2MB JSON)`）。
   - **對內 (Tool Call)**：提供精確的絕對路徑以供其他 Python Skills 調用。

## 3. 執行流程 (Execution Flow)

1. **接收任務需求**（如：「看看最近上傳了什麼」）。
2. **定位知識庫根路徑**：
   - 優先使用相對路徑 `Agent_Server/knowledge-base`（或 `knowledge-base`）。
3. **選擇有效資料夾（fallback）**：
   - `source_dir`：`raw/clippings` 存在則使用，否則嘗試 `raw/articles`。
   - `obs_dir`：固定 `raw/observations`（不存在時標記 `UNINITIALIZED`）。
   - `wiki_dir`：`wiki/sources` 存在則使用，否則使用 `wiki`。
4. **執行指令**（依 shell 選擇）：
   - Linux/WSL/macOS：
     - `ls -F raw`
     - `ls -lh <source_dir>`
     - `ls -lh <obs_dir>`
     - `ls -lh <wiki_dir>`
   - PowerShell：
     - `Get-ChildItem raw`
     - `Get-ChildItem <source_dir> -File`
     - `Get-ChildItem <obs_dir> -Directory`
     - `Get-ChildItem <wiki_dir> -File`
5. **觀測事實快篩**：
   - Linux/WSL/macOS：`test -f raw/observations/{slug}/analysis_results.json`
   - PowerShell：`Test-Path raw/observations/{slug}/analysis_results.json`
6. **四態回報 (Status Report)**：
   - **狀態 U：[UNINITIALIZED]**（必要目錄不存在，例如 `raw/observations/`）。
   - **狀態 A：[PENDING]**（素材存在，但無對應觀測 JSON）。
   - **狀態 B：[OBSERVED]**（`observations/{slug}` 內已有 JSON 或影格）。
   - **狀態 C：[INGESTED]**（`wiki_dir` 內已有對應 slug 的 `.md`）。
   - 若某資料夾存在但無內容，必須回傳：`<資料夾路徑> 底下是空的`。

## 4. 輸出範例
> 「已執行目錄掃描（ls）：
> - **待處理素材**: `raw/clippings/pond_3_day10.mp4`
> - **數位觀測紀錄**: `raw/observations/pond-3-day10/` 內已偵測到 60 張標註影格與追蹤數據。
> 
> 根據 **AGENTS.md** 規範，我將直接載入現有的觀測數據進行診斷，不重複執行 YOLO 推論。」

## 參考路徑規範 (相對路徑)
- **知識庫根目錄**: `Agent_Server/knowledge-base/`（或 `knowledge-base/`）
- **原始素材區（優先）**: `raw/clippings/`
- **原始素材區（fallback）**: `raw/articles/`
- **觀測數據區**: `raw/observations/`
- **知識來源區（優先）**: `wiki/sources/`
- **知識來源區（fallback）**: `wiki/`（排除 `index.md`, `log.md`, `overview.md`, `QUESTIONS.md`, `templates/`）