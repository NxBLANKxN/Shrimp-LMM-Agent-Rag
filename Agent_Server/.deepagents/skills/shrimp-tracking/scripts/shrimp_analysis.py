import os
import json
import asyncio
import cv2
import hashlib
from ultralytics import YOLO
from langchain_core.tools import tool

# --- 基礎路徑與 Wiki 結構設定 ---
BASE_DIR = "/opt/Shrimp-LMM-Agent-Rag/Agent_Server"
KNOWLEDGE_BASE = os.path.join(BASE_DIR, "knowledge-base")
MODEL_PATH = os.path.join(BASE_DIR, "models/best20260401_2.pt")

# 符合 AGENTS.md 的路徑規範
CLIPPINGS_DIR = os.path.join(KNOWLEDGE_BASE, "raw/clippings")
OBSERVATIONS_BASE = os.path.join(KNOWLEDGE_BASE, "raw/observations")

def get_slug(filename: str) -> str:
    """將檔名轉化為小寫連字符的 slug 格式"""
    name = os.path.splitext(os.path.basename(filename))[0]
    return name.lower().replace("_", "-").replace(" ", "-")

def calculate_sha256(filepath: str) -> str:
    """計算原始檔案的 SHA-256 哈希值"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# ==========================================
# 1. 圖片偵測邏輯 (Image Detection)
# ==========================================

def _run_image_logic(filename: str):
    slug = get_slug(filename)
    input_path = os.path.join(CLIPPINGS_DIR, filename)
    # 輸出至 raw/observations/{slug}/
    observation_dir = os.path.join(OBSERVATIONS_BASE, slug)
    plots_dir = os.path.join(observation_dir, "plots")
    
    os.makedirs(plots_dir, exist_ok=True)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到原始檔案: {input_path}")

    model = YOLO(MODEL_PATH)
    results = model.predict(
        source=input_path, 
        imgsz=640, 
        save=True, 
        project=observation_dir, 
        name="plots", 
        exist_ok=True
    )
    
    count = len(results[0].obb) if results[0].obb is not None else 0
    
    # 產出觀測紀錄 JSON
    summary = {
        "type": "image_observation",
        "raw_sha256": calculate_sha256(input_path),
        "shrimp_count": count,
        "plots_path": "plots/"
    }
    with open(os.path.join(observation_dir, "observation_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)

    return {"count": count, "dir": observation_dir}

@tool
async def shrimp_image_detector(filename: str):
    """對單張圖片執行 OBB 偵測。結果將作為觀測事實存入知識庫。"""
    try:
        res = await asyncio.to_thread(_run_image_logic, filename)
        return f"偵測完成！發現 {res['count']} 隻蝦子。觀測數據已存入知識庫：{res['dir']}"
    except Exception as e:
        return f"圖片分析失敗: {str(e)}"

# ==========================================
# 2. 影片追蹤邏輯 (Video Tracking)
# ==========================================

def _run_video_logic(filename: str):
    slug = get_slug(filename)
    input_path = os.path.join(CLIPPINGS_DIR, filename)
    
    # 數位觀測紀錄目錄：raw/observations/{slug}/
    observation_dir = os.path.join(OBSERVATIONS_BASE, slug)
    frames_dir = os.path.join(observation_dir, "frames")
    
    os.makedirs(frames_dir, exist_ok=True)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到原始影片: {input_path}")

    model = YOLO(MODEL_PATH)
    vid_stride = 5 # 跳幀推論提高效率
    results_generator = model.track(
        source=input_path, persist=True, imgsz=640, stream=True, vid_stride=vid_stride 
    )
    
    all_tracks = []
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

        # 每 30 幀擷取一張視覺證據（標註圖），供 LMM 進行定性診斷
        if processed_idx % 6 == 0:
            frame_filename = f"frame_{actual_frame_idx}.jpg"
            frame_path = os.path.join(frames_dir, frame_filename)
            # r.plot() 會回傳繪製好 BBox 與 ID 的影像
            cv2.imwrite(frame_path, r.plot())

    # --- 儲存數位觀測紀錄 JSON ---
    json_path = os.path.join(observation_dir, "analysis_results.json")
    output_payload = {
        "slug": slug,
        "raw_file": os.path.join("raw/clippings", filename),
        "raw_sha256": calculate_sha256(input_path),
        "total_processed_frames": processed_idx,
        "frames_root": "frames/",
        "data": all_tracks
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)

    return {"observation_dir": observation_dir, "json_path": json_path}

@tool
async def yolo_tracker(filename: str):
    """
    執行蝦隻 OBB 追蹤。將「光號」轉化為「觀測事實」，存入知識庫 Raw 層。
    """
    try:
        slug = get_slug(filename)
        # 知識優先預檢：若 JSON 已存在則不重複運算
        json_path = os.path.join(OBSERVATIONS_BASE, slug, "analysis_results.json")
        
        if os.path.exists(json_path):
            return f"觀測紀錄 '{slug}' 已存在。請 Agent 直接執行分析流程。"

        res = await asyncio.to_thread(_run_video_logic, filename)
        
        return (
            f"觀測紀錄生產完成！數據已存入：{res['observation_dir']}\n"
            f"請 Agent 根據此事實與 Wiki 歷史基準進行行為診斷。"
        )
    except Exception as e:
        return f"影片觀測發生錯誤: {str(e)}"