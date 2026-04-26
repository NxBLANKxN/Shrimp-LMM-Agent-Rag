import os
import json
import base64
import requests
import glob
import cv2  # 用於縮小圖片以解決 400 錯誤
import numpy as np
from typing import Optional
from langchain_core.tools import tool

# 設定基礎路徑與 API 入口
BASE_DIR = "/opt/Shrimp-LMM-Agent-Rag"
LLAMA_CPP_ENDPOINT = "http://localhost:8080/v1/chat/completions"

def _prepare_base64_image(image_path: str, max_size: int = 800) -> str:
    """
    讀取、縮放並將影像轉換為 Base64 字串。
    縮放是為了解決 llama.cpp 處理過大 Base64 導致的 400 Bad Request。
    """
    # 讀取影像
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"無法讀取影像: {image_path}")

    # 取得原始尺寸
    h, w = img.shape[:2]
    
    # 如果圖片太大，等比例縮小 (有利於 API 傳輸與模型推理速度)
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    # 將圖片編碼為 JPG 格式
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

@tool
def analyze_behavior_with_lmm(filename: str, is_video: bool = True) -> str:
    """
    對已生成的蝦隻追蹤數據或偵測圖片進行智慧行為診斷。
    當需要分析蝦隻健康、游泳行為、應激反應時使用。
    
    Args:
        filename: 資料夾名稱(影片模式)或具體圖片檔名(偵測模式)。
        is_video: 布林值，預設為 True。
    """
    
    # 1. 路徑定位
    if is_video:
        data_root = os.path.join(BASE_DIR, "data", "processed", "tracks", filename)
        json_path = os.path.join(data_root, "analysis_results.json")
        frames_dir = os.path.join(data_root, "frames")
        
        # 動態搜尋可用的影格圖片
        available_frames = glob.glob(os.path.join(frames_dir, "*.jpg"))
        if not available_frames:
            return f"❌ 診斷失敗：在 {frames_dir} 內找不到任何 JPG 影格。"
        img_path = sorted(available_frames)[0] # 抓取第一張影格
    else:
        img_path = os.path.join(BASE_DIR, "data", "processed", "detections", "plots", filename)
        json_path = None

    # 2. 定量數據提取 (JSON)
    stats_summary = "無可用結構化數據"
    if json_path and os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 擷取關鍵摘要，避免 Text 內容過長超出 Context Window
                summary = data.get("summary", data)
                stats_summary = json.dumps(summary, indent=2, ensure_ascii=False)[:1000] 
        except:
            stats_summary = "數據解析失敗"

    # 3. 視覺準備 (Base64 + 自動縮放)
    if not os.path.exists(img_path):
        return f"❌ 診斷失敗：找不到視覺檔案 {img_path}"
    
    try:
        base64_image = _prepare_base64_image(img_path)
    except Exception as e:
        return f"❌ 影像處理失敗: {str(e)}"

    # 4. 構建 Prompt
    prompt = f"""
    你是一位資深的「智慧養殖行為專家」。請根據提供的數據與影像進行診斷。
    
    [模式] {"影片時序分析" if is_video else "單圖偵測分析"}
    [數據摘要]
    {stats_summary}
    
    [任務要求]
    1. 觀察影像中蝦隻的姿態（有無側翻、應激跳躍）。
    2. 結合數據，評估分布密度與運動速度是否正常。
    3. 給出具體的養殖與環境改善建議。
    請用繁體中文回覆。
    """

    # 5. 呼叫 llama.cpp (OpenAI v1 相容格式)
    payload = {
        "model": "shrimp-behavior-lmm",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        "temperature": 0.2,
        "max_tokens": 800
    }

    try:
        # 視覺推理耗時較長，timeout 設為 120 秒
        response = requests.post(LLAMA_CPP_ENDPOINT, json=payload, timeout=120)
        
        # 針對 400 錯誤提供更詳細的日誌
        if response.status_code == 400:
            return f"❌ API 400 錯誤：請檢查圖片大小或模型輸入格式。詳細訊息：{response.text}"
            
        response.raise_for_status()
        result = response.json()
        
        # 修正：OpenAI v1 回傳格式 choices 是一個串列，必須取 [0]
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.Timeout:
        return "❌ 專家診斷超時：llama.cpp 回應過慢，請檢查伺服器負載。"
    except Exception as e:
        return f"❌ 專家診斷中斷: {str(e)}"
