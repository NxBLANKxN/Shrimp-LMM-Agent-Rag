---
name: shrimp-tracking
description: 蝦隻數據生產專家（執行層）。負責呼叫 YOLO OBB 模型對影像進行推論，產出追蹤 JSON 與標註影格，將「光號」轉化為「觀測事實」，存入 Wiki 的 Raw 層。
---

# 技能：蝦隻 OBB 數據推論與產出 (執行專用)

## 1. 職責定位與任務流轉 (Role & Workflow)
- **核心職責**：將原始影像轉化為結構化的**數位觀測紀錄 (Digital Observations)**。
- **任務交接**：
    - **開始前（知識優先）**：必須先檢查 `knowledge-base/raw/observations/{video_slug}/` 是否已有 `analysis_results.json`。若有，應立即終止本技能，回報「已有觀測數據」，並引導 Agent 進入 `shrimp-behavior-analysis`。
    - **結束後**：產出數據後，在 `wiki/log.md` 記錄 INGEST 動作，通知 Agent 已準備好數據。

## 2. 推論執行規範 (Inference Protocol)

### A. 影片追蹤推論 (Video Tracking)
- **工具**：`yolo_tracker`
- **作業內容**：
    1. 執行 YOLOv11 OBB 追蹤。
    2. 執行關鍵影格抽幀 (Keyframe Extraction)。
    3. **標註繪製**：在影格上繪製 Track ID 與 BBox（產出即具備視覺證據）。
- **寫入路徑**：`knowledge-base/raw/observations/{video_slug}/`

### B. 靜態影像偵測 (Image Detection)
- **工具**：`shrimp_image_detector`
- **作業內容**：
    1. 執行單張影像偵測並產出 OBB 標註圖。
- **寫入路徑**：`knowledge-base/raw/observations/{image_slug}/`

## 3. 數據產出標準 (Standard Output)
為了確保後續診斷順利，產出必須包含：
1. **結構化 JSON** (`analysis_results.json`)：包含座標、角度、Track ID、影格時間點。
2. **視覺標註檔案**：
    - 影片：`frames/*.jpg`（**必須預先繪製標註**，作為 LMM 診斷的定性證據）。
    - 圖片：`plots/*.jpg`。

## 4. 異常處理與安全性 (Safety & Error Handling)
- **路徑安全**：嚴禁寫入 `knowledge-base/wiki/` 目錄。本技能僅限寫入 `knowledge-base/raw/observations/`。
- **硬體回報**：若 GPU 顯存不足導致推論失敗，應回報具體錯誤代碼而非嘗試解讀損壞數據。

## 5. 輸出語境範例 (Output Example)
> 「已偵測到新影片上傳，正在執行觀測作業：
> 1. 已啟動 `yolo_tracker` 對影片 `shrimp_pond_01.mp4` 進行 OBB 推論。
> 2. 數據已存入：`knowledge-base/raw/observations/shrimp-pond-01/`。
> 3. 已生成 45 張關鍵影格供 LMM 診斷。
> 
> 數位觀測紀錄生產完成，現在交由 `shrimp-behavior-analysis` 結合 Wiki 知識進行專家診斷。」

## 參考路徑規範 (絕對路徑對齊)
- **輸入來源**：`/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/raw/clippings/`
- **輸出目標**：`/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/raw/observations/{slug}/`

---