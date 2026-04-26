import os
import json
import asyncio
import cv2
from ultralytics import YOLO
from langchain_core.tools import tool

# --- 基礎路徑與模型設定 ---
BASE_DIR = "/opt/Shrimp-LMM-Agent-Rag"
MODEL_PATH = os.path.join(BASE_DIR, "models/best20260401_2.pt")
UPLOAD_DIR = os.path.join(BASE_DIR, "data/uploads")

# ==========================================
# 1. 圖片偵測邏輯 (Image Detection)
# ==========================================

def _run_image_logic(filename: str):
    """內部的同步邏輯，執行 YOLO OBB 圖片預測"""
    input_path = os.path.join(UPLOAD_DIR, filename)
    output_dir = os.path.join(BASE_DIR, "data/processed/detections")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到圖片檔案: {input_path}")

    model = YOLO(MODEL_PATH)
    results = model.predict(
        source=input_path, 
        imgsz=640, 
        save=True, 
        project=output_dir, 
        name="plots", 
        exist_ok=True
    )
    
    count = len(results[0].obb) if results[0].obb is not None else 0
    return {"count": count, "dir": output_dir}

@tool
async def shrimp_image_detector(filename: str):
    """對單張圖片執行蝦隻偵測與計數 (OBB 模式)。"""
    try:
        res = await asyncio.to_thread(_run_image_logic, filename)
        return f"圖片偵測完成，共發現 {res['count']} 隻蝦子。結果圖已存於 {res['dir']}/plots/。"
    except Exception as e:
        return f"圖片分析失敗: {str(e)}"

# ==========================================
# 2. 影片追蹤邏輯 (Video Tracking)
# ==========================================

def _run_video_logic(filename: str):
    """
    內部的同步邏輯。
    修改點：將 JSON 與 Frames 統一存放於 data/processed/tracks/{pure_filename}/
    """
    pure_filename = os.path.basename(filename)
    input_path = os.path.join(UPLOAD_DIR, pure_filename)
    
    # --- 新的路徑架構 ---
    # 每個影片擁有獨立資料夾：/tracks/video_name.mp4/
    track_result_dir = os.path.join(BASE_DIR, "data/processed/tracks", pure_filename)
    frames_dir = os.path.join(track_result_dir, "frames") # 影格放在子目錄
    
    os.makedirs(track_result_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到影片檔案: {input_path}")

    model = YOLO(MODEL_PATH)
    
    vid_stride = 5
    results_generator = model.track(
        source=input_path, 
        persist=True, 
        imgsz=640, 
        stream=True, 
        vid_stride=vid_stride 
    )
    
    all_tracks = []
    captured_frames_list = []
    processed_idx = 0

    for r in results_generator:
        processed_idx += 1
        actual_frame_idx = processed_idx * vid_stride
        
        if r.obb is not None and r.obb.id is not None:
            obbs = r.obb.xywhr.cpu().numpy().tolist()
            ids = r.obb.id.cpu().numpy().astype(int).tolist()
            
            for obb, track_id in zip(obbs, ids):
                all_tracks.append({
                    "frame": actual_frame_idx,
                    "id": track_id,
                    "obb": [round(x, 4) for x in obb]
                })

        # 每 30 幀擷取一張視覺證據
        if processed_idx % 6 == 0:
            frame_filename = f"frame_{actual_frame_idx}.jpg"
            frame_path = os.path.join(frames_dir, frame_filename)
            cv2.imwrite(frame_path, r.plot()) 
            captured_frames_list.append(frame_path)

    # --- 儲存 JSON (現在放在與 frames 同級的資料夾中) ---
    json_path = os.path.join(track_result_dir, "analysis_results.json")
    output_payload = {
        "filename": pure_filename,
        "total_processed_frames": processed_idx,
        "actual_frames_covered": actual_frame_idx,
        "frames_root": frames_dir,
        "captured_images": [os.path.basename(p) for p in captured_frames_list],
        "data": all_tracks
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)

    return {
        "json_path": json_path,
        "frames_count": len(captured_frames_list),
        "result_dir": track_result_dir
    }

@tool
async def yolo_tracker(filename: str):
    """
    執行蝦隻 OBB 追蹤。結果 (JSON 與影格) 會統一存放於該影片的專屬目錄下。
    """
    try:
        pure_filename = os.path.basename(filename)
        # 預檢路徑：檢查該影片資料夾下的 JSON 是否已存在
        json_path = os.path.join(BASE_DIR, "data/processed/tracks", pure_filename, "analysis_results.json")
        
        if os.path.exists(json_path):
            return f"影片 '{pure_filename}' 先前已分析完成。系統已載入現有數據。"

        res = await asyncio.to_thread(_run_video_logic, filename)
        
        return (
            f"分析完成！結果已整合儲存至：{res['result_dir']}\n"
            f"共擷取 {res['frames_count']} 張影格。請 Agent 根據 JSON 數據與影像進行行為診斷。"
        )
    except Exception as e:
        return f"影片分析發生錯誤: {str(e)}"