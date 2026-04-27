這是 **Shrimp-LMM-Agent-Rag** 系統中最核心的「智慧大腦」技能。為了落實 **LLM-Wiki 模式**，這個技能不僅要負責分析，更要負責**知識的產出（撰寫 Wiki 頁面）**。

依照你要求的「知識優先」與「全量 Wiki 化」架構，以下是修改後的技能定義：

---

name: shrimp-behavior-analysis
description: 蝦隻行為與狀態診斷專家（解讀層）。解析 YOLO 觀測數據，結合標註影格進行多模態判讀，並將診斷結果轉化為 Wiki 知識資產。不執行任何推論 (Inference)。
---

# 技能：蝦隻行為診斷與多模態判讀 (解讀專用)

## 1. 職責邊界與預檢 (Boundary & Pre-check)
- **唯讀約束 (Read-only)**：本技能**禁止**觸發 `yolo_tracker`。
- **診斷前提**：必須先透過 `shrimp-search` 執行「三態校驗」，確認 `raw/observations/{slug}/` 內存在 `analysis_results.json` 或標註圖。
- **知識優先**：在開始診斷前，Agent 應主動檢索 `wiki/concepts/` 了解該池的歷史基準值（如：平時的平均聚集度），作為對比基準。

## 2. 多模態診斷邏輯 (Multimodal Diagnosis)

### A. 數據與視覺的臨床對齊 (Data-Vision Alignment)
Agent 需結合「定量事實」與「定性證據」：
- **定量 (Quantitative)**：解析 JSON 數據。鎖定速度異常值（應激）、位移歸零（死亡/靜止）、聚集度變化（進食反應）。
- **定性 (Qualitative)**：根據 JSON 鎖定的時間點，「直接觀測」`frames/` 資料夾中已繪製標註的影格。**嚴禁二次辨識，僅進行視覺特徵解讀（如體色、泳姿）。**

### B. 分流解讀重點
1. **動態觀測 (Observations - Video)**：
   - **應激判定 (Stress)**：分析時序速度，觀察影格中是否有「應激性彈跳 (Stress Jump)」。
   - **健康評估**：檢查 ID 軌跡，識別「原地旋轉」或「側翻靜止」等病徵。
2. **靜態觀測 (Observations - Image)**：
   - **分布利用率**：觀察 `plots/` 判定蝦隻是否因環境因素（如死角、溶氧低）而避開特定區域。
   - **個體健康**：觀測體色（如白濁、發紅）與外觀完整度。

## 3. Wiki 知識合成規範 (Wiki Synthesis Protocol)
診斷完成後，Agent 的輸出必須包含以下動作：
- **建立 Source 頁面**：依照 `source-template.md` 在 `wiki/sources/{slug}.md` 建立報告。
- **鏈結 Concept**：若發現特定行為（如應激），必須使用 Wikilink `[[stress-response]]` 鏈結至知識庫，並記錄於該概念的 **Evolution Log** 中。
- **更新 QUESTIONS**：若診斷出無法解釋的群體行為，應在 `wiki/QUESTIONS.md` 記錄新問題。

## 4. 診斷報告結構 (Output Standard)
1. **分析對象 (Target)**：註明影片 Slug 與原始路徑。
2. **健康概覽 (Overview)**：整體活躍度評估。
3. **異常清單 (Anomalies)**：列出具體 ID、影格編號與行為描述。引用視覺證據，例：「觀測 `frame_0045.jpg`，ID#5 出現腹部朝上，符合活力值喪失之數據。」
4. **信心等級 (Confidence)**：根據數據完整度標註 Low/Medium/High。
5. **養殖處方 (Prescription)**：提供行動建議（如：調整給餌量、檢查水質）。

## 參考路徑 (僅限讀取)
- **觀測數據入口**：`/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/raw/observations/{slug}/analysis_results.json`
- **視覺影格證明**：`/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/raw/observations/{slug}/frames/*.jpg`
- **Wiki 報告位置**：`/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/wiki/sources/{slug}.md`
---
