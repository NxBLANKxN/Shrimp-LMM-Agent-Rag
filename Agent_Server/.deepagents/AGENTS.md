# AGENTS.md

## 專案概要
- **專案名稱**: Shrimp-LMM-Agent-Rag (智慧蝦類養殖行為分析系統)
- **描述**: 基於 YOLO OBB 追蹤與大型多模態模型 (LMM) 的自動化養殖監測系統，實現影像辨識與行為專家診斷的無縫銜接。
- **技術棧**: FastAPI, LangChain, DeepAgents, YOLOv11 OBB, React (TypeScript/Tailwind), llama.cpp (Backend LLM).

## 架構與技術決策
- **核心架構**: 原子化工具 (Atomic Tools) + 多模態行為診斷 (LMM Analysis)。
- **數據流**: 原始影像 → YOLO OBB 追蹤推論 → 結構化 JSON + 關鍵影格 → LMM 專家分析報告。
- **路徑規範**: 採用 **「影片專屬目錄制」**，將數據檔案與視覺證據 (Frames) 物理隔離但邏輯綁定。

## 程式碼規範 (Rules)
- **路徑處理**: 嚴格使用 `os.path.join` 構建路徑，禁止在程式碼中硬編碼 (Hard-coded) 斜線。
- **異步處理**: 所有的 Agent Tool 必須定義為 `async`，耗時的 YOLO 推論應封裝在 `asyncio.to_thread` 中執行。
- **語言規範 (Language)**: 
    - **動態語言適應**: 必須偵測並遵循使用者的輸入語言進行回覆（例如：使用者用繁體中文提問，則以繁體中文回答）。
    - **專業術語對照**: 在提及技術或養殖專有名詞時，應採用「中文 (英文)」格式（例如：物件偵測 (Object Detection)、溶氧量 (Dissolved Oxygen)）。
- **回應格式**: 隱藏底層 Linux 檔案路徑，轉而提供具備養殖專業洞察的描述。

---

# Agent Guide: 智慧蝦類養殖行為分析系統操作指南

## 1. 專案核心路徑 (Absolute Path Definitions)
必須將 `/opt/Shrimp-LMM-Agent-Rag/` 視為系統的【專案根目錄 (BASE_DIR)】。
- **後端服務**: `${BASE_DIR}/Agent_Server/`
- **數據倉庫 (Data Repository)**:
    - **上傳區**: `${BASE_DIR}/data/uploads/`
    - **影像偵測**: `${BASE_DIR}/data/processed/detections/`
    - **追蹤數據 (核心)**: `${BASE_DIR}/data/processed/tracks/{filename}/` 
        - **數據檔案**: `analysis_results.json`
        - **視覺證據**: `frames/`

## 2. 具備技能 (Available Skills)
1. **shrimp-tracking**: 執行 YOLO OBB 運算，產出追蹤座標、Track ID 與視覺標註圖。
2. **shrimp-behavior-analysis**: **行為診斷專家**。解析 JSON 數據並配合影格進行深度診斷（如：搶食、應激、健康評估）。
3. **shrimp-search**: 檔案檢索工具，掌握專案檔案與分析結果狀態。

## 3. 自主作業與執行規範 (Operational Protocol)
- **語言一致性策略**: Agent 在輸出診斷報告時，應確保專有名詞的一致性，並根據使用者語系調整表達方式，確保養殖專家建議的精確傳達。
- **路徑自動補完**: 接收檔案通知後，優先使用 `shrimp-search` 確認檔案名稱，並補完為絕對路徑。
- **快取優先原則 (Cache First)**: 執行 `yolo_tracker` 前，**必須**先檢查 `analysis_results.json` 是否存在，若存在則嚴禁重複執行推論。
- **多模態判讀邏輯**: 診斷行為時，Agent 必須同時參考 JSON 提供的座標位移（定量數據）與 `frames/` 資料夾中的圖片（定性特徵）。

## 4. 領域知識與分析指標
- **聚集度 (Aggregation Index)**: 評估進食反應（Feeding Response）。
- **異常位移 (Abnormal Movement)**: 
    - **應激反應 (Stress Response)**: 瞬間高速位移。
    - **病徵 (Clinical Signs)**: 識別原地旋轉、翻轉或靜止。
- **空間分布利用率 (Spatial Distribution)**: 分析池底死角與溶氧不足區域。