---
name: shrimp-search
description: 檔案系統檢索與狀態監測專家。負責掃描專案目錄，驗證檔案存在性並補完絕對路徑，是 Agent 決策「執行推論」或「直接診斷」的關鍵依據。
---

# 技能：檔案系統搜索與目錄掃描 (Shrimp Search)

## 1. 核心功能 (Core Functions)

1. **目錄瀏覽 (Directory Browsing)**：
   - **主動掃描**：Agent 可調用工具查看 `/data/uploads`（待處理素材）或 `/data/processed/`（分析成果）。
   - **預設機制**：若使用者未指定路徑，應優先檢查 `${BASE_DIR}/data/uploads/`。

2. **智慧導引與路徑補完 (Path Guidance)**：
   - 當使用者提及檔名（如 `shrimp.mp4`）時，Agent 應自動搜尋其在 `/opt/Shrimp-LMM-Agent-Rag/data/uploads/` 中的**絕對路徑**，確保後續工具執行不報錯。

3. **分析紀錄校驗 (Result Verification)**：
   - **關鍵任務**：在 `shrimp-tracking` 啟動前，必須先驗證 `analysis_results.json` 或 `plots/` 是否已存在。
   - **決策支援**：根據校驗結果引導 Agent 跳過重複的 YOLO 推論，直接進入行為診斷階段。

## 2. 互動邏輯 (Interaction Logic)

1. **初始狀態掌握 (Initial State)**：
   在對話啟動或使用者詢問「目前有哪些資料」時，Agent 應主動列出待處理檔案與已分析結果的對比。

2. **智慧過濾 (Smart Filtering)**：
   - 自動隱藏系統檔（如 `.DS_Store`, `__pycache__`）。
   - 僅對使用者展示具備分析意義的格式：
     - **影像**: `.mp4`, `.avi`, `.jpg`, `.png`,`.mov`
     - **數據**: `.json`

3. **路徑回報規範 (Path Reporting)**：
   - **對外 (User)**：使用易讀的相對路徑（如 `uploads/shrimp.mp4`）。
   - **對內 (Tool Call)**：必須使用完整的絕對路徑（如 `/opt/Shrimp-LMM-Agent-Rag/data/uploads/shrimp.mp4`）。

## 3. 執行流程 (Execution Flow)

1. **接收檔名/路徑需求**。
2. **執行檢索**：調用 `shrimp_search` 工具確認物理檔案是否存在。
3. **分類回報**：
   - 狀態 A：**[全新素材]**（僅存在於 uploads）。
   - 狀態 B：**[已處理數據]**（存在於 processed，可直接診斷）。
   - 狀態 C：**[格式錯誤/遺失]**。

## 4. 輸出範例
> 「已為您掃描目錄：
> - **待處理影片**: `uploads/tank_A.mp4`
> - **已分析結果**: `tracks/tank_A/` (包含軌跡 JSON 與 45 張影格)
> 由於 `tank_A.mp4` 已有完整分析紀錄，我將直接為您讀取數據並產出診斷報告。」

## 參考路徑 (僅限瀏覽)
- **原始素材區**: `data/uploads/`
- **影片追蹤結果**: `data/processed/tracks/`
- **圖片偵測結果**: `data/processed/detections/plots/`