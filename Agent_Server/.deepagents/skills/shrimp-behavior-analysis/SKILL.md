---
name: shrimp-behavior-analysis
description: 蝦隻行為與狀態診斷專家（解讀層）。解析由 YOLO 產出的追蹤數據 (Tracks) 或偵測結果 (Detections)，結合視覺影格進行多模態判讀，不執行任何推論 (Inference)。
---

# 技能：蝦隻行為診斷與多模態判讀 (解讀專用)

## 1. 職責邊界與預檢 (Boundary & Pre-check)
- **唯讀約束 (Read-only)**：本技能**禁止**觸發 `yolo_tracker` 或 `shrimp_image_detector`。
- **診斷前提**：Agent 必須先透過 `shrimp-search` 確認路徑中存在 `analysis_results.json` (影片) 或 `plots/` (圖片)。
- **無數據處理**：若預檢發現數據缺失，應回報「數據尚未生產」，並引導 `shrimp-tracking` 技能介入。

## 2. 多模態診斷邏輯 (Multimodal Diagnosis)

### A. 數據與視覺的臨床對齊 (Data-Vision Alignment)
Agent 需同時調用定量與定性資料進行交叉驗證：
- **定量 (Quantitative)**：調用 `read_file` 讀取 JSON，鎖定速度異常值、位移歸零點或 ID 消失位置。
- **定性 (Qualitative)**：根據 JSON 鎖定的時間點，「直接觀測」對應的標註影格 (Frames)。**嚴禁對影格進行二次辨識。**

### B. 分流解讀重點
1. **動態影片 (Video Tracks)**：
   - **應激判定 (Stress)**：分析時序速度，觀察影格中是否有「跳躍」或「應激性彈跳」。
   - **健康評估**：檢查 ID 軌跡，識別「原地旋轉」或「側翻靜止」等病徵表現。
2. **靜態影像 (Image Detections)**：
   - **分布利用率**：觀察標註圖 (Plots) 判定蝦隻是否因環境因素（如死角、溶氧低）而避開特定區域。
   - **個體健康**：直接觀測蝦隻體色（如白濁、發紅）與外觀完整度。

## 3. LMM 診斷執行規範 (LMM Protocol)
當 Agent 調用後端診斷腳本（如 `behavior_expert_lmm.py`）時：
- **Context 封裝**：將 JSON 的統計摘要與「已標註影格」轉換為 Base64 傳送。
- **臨床報告**：報告中必須引用視覺證據。例如：「經觀測 `frame_0045.jpg`，標記為 ID#5 的蝦隻出現腹部朝上姿態，符合數據顯示之活力值喪失。」

## 4. 診斷報告結構 (Output Standard)
1. **分析對象 (Target)**：註明影片名稱或圖片編號。
2. **健康概覽 (Overview)**：池內整體活躍度或分布狀態。
3. **異常清單 (Anomalies)**：列出具體 ID、座標或影格編號，並描述異常行為（如：應激彈跳、側翻）。
4. **養殖處方 (Prescription)**：提供具體的行動建議（如：檢測水質、檢查增氧機、調整給餌量）。

## 參考路徑 (僅限讀取)
- **影片數據入口**：`data/processed/tracks/{filename}/analysis_results.json`
- **視覺影格證明**：`data/processed/tracks/{filename}/frames/*.jpg`
- **圖片分析結果**：`data/processed/detections/plots/{filename}`