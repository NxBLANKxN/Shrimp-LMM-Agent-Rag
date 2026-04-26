---
name: shrimp-tracking
description: 蝦隻數據生產專家（執行層）。負責呼叫 YOLO OBB 模型對影像進行推論，產出追蹤 JSON 與標註影格，為後續行為分析提供基礎數據。
---

# 技能：蝦隻 OBB 數據推論與產出 (執行專用)

## 1. 職責定位與任務流轉 (Role & Workflow)
- **核心職責**：將原始影像轉化為可供讀取的數據。
- **任務交接**：
    - **開始前**：透過 `shrimp-search` 執行預檢，若路徑下已有 `analysis_results.json` 或 `plots/`，應立即停止本技能，將控制權交給 `shrimp-behavior-analysis`。
    - **結束後**：產出完整目錄後，通知 Agent 已準備好數據，引導進入診斷階段。

## 2. 推論執行規範 (Inference Protocol)

### A. 影片推論 (Video Tracking)
- **工具**：`yolo_tracker`
- **作業內容**：
    1. 執行 YOLO OBB 追蹤。
    2. 自動執行關鍵影格抽幀 (Keyframe Extraction)。
    3. **標註繪製**：在影格上繪製 Track ID 與 BBox（產出即具備視覺證據）。
- **產出路徑**：`${BASE_DIR}/data/processed/tracks/{filename}/`

### B. 靜態影像偵測 (Image Detection)
- **工具**：`shrimp_image_detector`
- **作業內容**：
    1. 執行單張影像偵測。
    2. 產出帶有 OBB 標註的視覺結果圖。
- **產出路徑**：`${BASE_DIR}/data/processed/detections/plots/{filename}`

## 3. 數據產出標準 (Standard Output)
為了確保後續診斷順利，產出必須包含：
1. **結構化 JSON**：包含座標、角度、ID、影格關聯。
2. **視覺標註檔案**：
    - 影片：`frames/*.jpg`（已繪製標註，**禁止要求後續技能再次偵測**）。
    - 圖片：`plots/*.jpg`（已繪製標註）。

## 4. 錯誤處理 (Error Handling)
- 若影像格式不符或損壞，應明確回報「推論失敗」而非嘗試解讀。
- 若硬體 (GPU) 資源不足導致逾時，應記錄最後處理進度。

## 5. 輸出範例
> 「已啟動 `yolo_tracker` 對影片 `shrimp_tank_A.mp4` 進行推論。
> 產出進度：
> - 數據檔案：`analysis_results.json` 已生成。
> - 視覺證據：30 張標註影格已存入 `/frames` 目錄。
> 數據生產完成，現在交由`shrimp-behavior-analysis`進行深度診斷。」

## 參考路徑 (僅限寫入與生成)
- **原始輸入**：`data/uploads/`
- **影片產出根目錄**：`data/processed/tracks/{filename}/`
- **圖片產出根目錄**：`data/processed/detections/plots/`