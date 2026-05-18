# ─────────────────────────────────────────────
# tools/video_tools.py — 影片視覺分析工具 (Gemma 4 & DeepAgent 終極優化版)
# ─────────────────────────────────────────────
import base64
import cv2
import numpy as np  # 💡 記得補上 numpy，用於銳化矩陣
from pathlib import Path
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from config import ROOT_DIR, LLAMA_URL, LLAMA_MODEL

VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv"}


def _get_vision_llm() -> ChatOpenAI:
    """Lazy 初始化視覺模型"""
    return ChatOpenAI(
        base_url=LLAMA_URL,
        api_key="not-needed",
        model=LLAMA_MODEL,
        max_tokens=200000,
        temperature=0.2,
    )


def _resolve_video_path(file_path: str):
    """尋找影片檔案，支援相對路徑、只有檔名等多種輸入方式。"""
    possible_paths = [
        Path(ROOT_DIR) / file_path,
        Path(ROOT_DIR) / "knowledge-base" / "raw" / file_path,
        Path(ROOT_DIR) / "knowledge-base" / "raw" / "videos" / file_path,
    ]
    for p in possible_paths:
        if p.exists() and p.is_file() and p.suffix.lower() in VIDEO_EXTS:
            return p

    # 全域搜尋
    raw_root = Path(ROOT_DIR) / "knowledge-base" / "raw"
    basename = Path(file_path).name
    for p in raw_root.rglob("*"):
        if p.name == basename and p.suffix.lower() in VIDEO_EXTS:
            return p

    return None


def _extract_frames(video_path: Path, max_frames: int) -> tuple[float, list[tuple[float, str]]]:
    """
    【Gemma 4 特化高速版】用 OpenCV 線性擷取關鍵幀，拋棄緩慢的 cap.set()。
    不崩潰設計：若無法開啟影片，回傳空列表讓主函式處理，確保 Agent 穩定度。
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        # 💡 不要 raise，回傳特徵讓上層包裝成友善錯誤給 Agent
        return 0.0, []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    duration_sec = total_frames / fps

    # Gemma 4 處理長文本能力極強，放寬上限到 16 幀，留給 Agent 更多上下文推理
    max_frames = max(1, min(max_frames, 16))
    if total_frames < max_frames:
        target_indices = set(range(total_frames))
    else:
        step = total_frames / max_frames
        target_indices = set(int(i * step) for i in range(max_frames))

    frames: list[tuple[float, str]] = []
    current_idx = 0

    # ── 線性掃描（順著影片讀取，速度提升 3~10 倍） ──
    while len(frames) < len(target_indices):
        ret, frame = cap.read()
        if not ret:
            break
        
        if current_idx in target_indices:
            h, w = frame.shape[:2]
            
            # 調整至 1280 寬度（符合 Gemma 4 高畫質 Patch 切割比例）
            target_width = 1280
            if w > target_width:
                scale = target_width / w
                frame = cv2.resize(frame, (target_width, int(h * scale)), interpolation=cv2.INTER_AREA)
            
            # 💡 巡檢細節強化：輕微銳化，突顯蝦池水質或設備小燈邊緣
            kernel = np.array([[0, -0.1, 0], [-0.1, 1.4, -0.1], [0, -0.1, 0]])
            frame = cv2.filter2D(frame, -1, kernel)
                
            # 提高 JPEG 品質到 90%，讓 Gemma 4 辨識得更清楚
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            b64 = base64.b64encode(buf).decode("utf-8")
            frames.append((current_idx / fps, b64))
            
        current_idx += 1

    cap.release()
    return duration_sec, frames


@tool
def analyze_video(file_path: str, max_frames: int = 12, question: str = "") -> str:
    """
    分析影片內容。使用 OpenCV 從影片中均勻擷取關鍵幀，並將所有畫面一次性投放給視覺語言模型。
    模型將結合時間軸與多張畫面，進行連續性的狀態追蹤、異常診斷並產出摘要報告。
    適用於蝦池監控、設備巡檢等需要追蹤時間變化的場景。

    Args:
        file_path (str): 影片的相對路徑或純檔名，系統會自動搜尋。
        max_frames (int): 最多擷取的關鍵幀數量，預設 12 幀（建議範圍 4-12 幀以維持推理速度）。
        question (str):   想針對影片詢問的具體問題（如：蝦子活動力、設備是否有黃燈閃爍）；空白則做通用摘要。

    Returns:
        str: 結構化的 Markdown 影片巡檢分析報告。
    """
    # ── 1. 尋找影片 ──
    target_path = _resolve_video_path(file_path)
    if not target_path:
        return f"❌ 找不到影片檔案 '{file_path}'，請確認路徑或檔名是否正確。"

    # ── 2. 擷取關鍵幀 ──
    try:
        duration_sec, frames_b64 = _extract_frames(target_path, max_frames)
        if not frames_b64:
            return f"❌ 無法從影片 '{target_path.name}' 中擷取任何有效影格，可能影片已損毀或編碼不支援。"
    except Exception as e:
        return f"❌ 擷取影片幀時發生未預期的錯誤：{str(e)}"

    # ── 3. 封裝多圖訊息（One-Shot Multi-Image Approach） ──
    try:
        vision_llm = _get_vision_llm()
        message_content = []
        
        for idx, (ts, b64) in enumerate(frames_b64, 1):
            ts_str = f"{int(ts // 60):02d}:{int(ts % 60):02d}"
            message_content.extend([
                {"type": "text", "text": f"\n--- [關鍵幀 #{idx} | 影片時間戳: {ts_str}] ---"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ])
            
        # ── Gemma 4 特化高級提示詞 ──
        analysis_prompt = (
            f"\n\n[分析任務指引]\n"
            f"你現在收到了一段來自影片 '{target_path.name}' 的連續關鍵幀畫面（總時長 {duration_sec:.1f} 秒）。\n"
            f"請同時參閱上述所有帶有時間戳的畫面，完成以下分析並以 Markdown 格式輸出報告：\n\n"
            f"1. **📋 整體場景摘要**：說明這段影片的核心場景、環境背景與事件脈絡。\n"
            f"2. **🔍 逐幀狀態/動態追蹤**：請結合時間戳，描述畫面中主要物體/生物（如蝦子、巡檢設備）隨時間產生的變化、動作或狀態轉變。\n"
            f"3. **⚠️ 異常或值得注意的問題**：列出任何不尋常的跡象、設備故障、行為異常或潛在風險。若一切正常，請明確註明。\n"
        )
        
        if question:
            analysis_prompt += f"4. **🎯 針對特定問題的回答**：使用者特別關心以下問題，請優先且深入解答：\n👉 {question}\n"
            
        analysis_prompt += (
            f"\n[Gemma 4 視覺特化引導]\n"
            f"- 請發揮你對高解析度細節與多圖聯動的優秀推理能力。\n"
            f"- 仔細觀察畫面中的微小變動（如蝦池水面的氣泡、蝦隻分布密度、設備信號燈顏色變換）。\n"
            f"- 若發現特定時間點有局部異常，請精準指出是哪一個時間戳的關鍵幀，並具體描述該異常特徵。\n"
        )
            
        message_content.append({"type": "text", "text": analysis_prompt})

        # ── 4. 單次調用視覺模型 ──
        msg = HumanMessage(content=message_content)
        resp = vision_llm.invoke([msg])

        # ── 5. 組合最終報告 ──
        return (
            f"# 📹 影片分析報告\n"
            f"**檔案名稱**: `{target_path.name}`  \n"
            f"**影片時長**: {duration_sec:.1f} 秒  \n"
            f"**分析幀數**: {len(frames_b64)} 幀\n\n"
            f"---\n\n"
            f"{resp.content.strip()}"
        )

    except Exception as e:
        return (
            f"⚠️ 影片幀已擷取完成（{len(frames_b64)} 幀），但呼叫本地多模態模型失敗：{str(e)}\n"
            f"請檢查 llama.cpp 是否正常運作，以及 VRAM 是否充足。"
        )