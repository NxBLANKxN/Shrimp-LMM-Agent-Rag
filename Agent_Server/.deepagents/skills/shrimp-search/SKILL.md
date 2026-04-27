---
name: shrimp-search
description: 知識庫路徑導航與狀態監測專家。底層透過 `ls` 系統指令快速掃描 `knowledge-base`，驗證「原始素材」、「觀測數據」與「Wiki 頁面」的完整性。
---

# 技能：知識庫路徑搜索與狀態監測 (Shrimp Search - LS Based)

## 1. 核心功能 (Core Functions)

1. **高效目錄掃描 (High-Speed Listing)**：
   - **底層機制**：使用 `ls -R` 或 `ls -lh` 快速獲取 `/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/` 下的檔案樹。
   - **掃描重點**：
     - `raw/clippings/`：掃描是否有新影片。
     - `raw/observations/`：掃描是否已有推論 JSON 與 `frames/` 資料夾。

2. **智慧路徑補完 (Path & Slug Guidance)**：
   - 當 Agent 接收到不完整的檔名時，透過 `ls` 搜尋匹配的絕對路徑。
   - 將搜尋結果轉化為標準 **Slug**（如 `tank_a.mp4` -> `tank-a`），用於跨目錄檢索。

3. **觀測事實校驗 (Observation Check)**：
   - **關鍵決策**：在執行 YOLO 推論前，先執行 `ls raw/observations/{slug}/analysis_results.json`。
   - 若檔案存在，強制 Agent 跳過 `shrimp-tracking`，直接調用診斷工具。

## 2. 互動邏輯 (Interaction Logic)

1. **初始狀態掌握 (Initial State)**：
   啟動時自動掃描觀測區，回報「目前已完成觀測的影片清單」與「待處理影片清單」。

2. **隱藏雜訊 (Noise Reduction)**：
   - 過濾 `.` 開頭的隱藏檔與 `.gitkeep`。
   - 僅向使用者呈現具備領域價值的格式（`.mp4`, `.jpg`, `.json`, `.md`）。

3. **路徑回報規範 (Path Reporting)**：
   - **對外 (User)**：顯示簡潔的路徑與檔案大小（如 `raw/observations/tank-a/ (45 frames, 1.2MB JSON)`）。
   - **對內 (Tool Call)**：提供精確的絕對路徑以供其他 Python Skills 調用。

## 3. 執行流程 (Execution Flow)

1. **接收任務需求**（如：「看看最近上傳了什麼」）。
2. **執行指令**：背景執行 `ls -F` 區分目錄與檔案。
3. **三態回報 (Status Report)**：
   - **狀態 A：[待推論]**（僅存在於 `clippings/`）。
   - **狀態 B：[已具備事實]**（`observations/` 內已有 JSON 與影格）。
   - **狀態 C：[已入庫]**（`wiki/sources/` 內已有對應 slug 的 `.md`）。

## 4. 輸出範例
> 「已執行目錄掃描（ls）：
> - **待處理素材**: `raw/clippings/pond_3_day10.mp4`
> - **數位觀測紀錄**: `raw/observations/pond-3-day10/` 內已偵測到 60 張標註影格與追蹤數據。
> 
> 根據 **AGENTS.md** 規範，我將直接載入現有的觀測數據進行診斷，不重複執行 YOLO 推論。」

## 參考路徑規範 (絕對路徑)
- **原始素材區**: `/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/raw/clippings/`
- **觀測數據區**: `/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/raw/observations/`
- **知識來源區**: `/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/wiki/sources/`