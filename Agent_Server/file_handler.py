# ─────────────────────────────────────────────
# file_handler.py — 上傳檔案的分類與儲存
# ─────────────────────────────────────────────
import shutil
from pathlib import Path
from fastapi import UploadFile
from config import ROOT_DIR, UPLOAD_MAP


def classify_file(filename: str) -> str:
    """根據副檔名回傳分類字串，對應到 UPLOAD_MAP 的 key。"""
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return "pdf"
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        return "image"
    elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
        return "video"
    elif ext in [".mp3", ".wav", ".m4a"]:
        return "audio"
    elif ext in [".xlsx", ".xls"]:
        return "excel"
    elif ext == ".csv":
        return "csv"
    elif ext in [".doc", ".docx", ".ppt", ".pptx"]:
        return "doc"
    elif ext in [".md", ".html", ".htm"]:
        return "clipping"   # Obsidian Web Clipper 網頁資料
    elif ext in [".py", ".js", ".ts", ".java", ".cpp", ".php", ".css"]:
        return "code"
    elif ext in [".txt", ".json", ".yaml", ".yml"]:
        return "text"

    return "unknown"


def save_upload_file(upload: UploadFile) -> str:
    """
    將上傳的檔案儲存到對應的 raw/ 子資料夾。
    回傳相對於 ROOT_DIR 的路徑字串。
    """
    file_type = classify_file(upload.filename)
    target_dir = UPLOAD_MAP[file_type]
    dest = Path(target_dir) / upload.filename

    with dest.open("wb") as out:
        shutil.copyfileobj(upload.file, out)

    return str(dest).replace(ROOT_DIR + "/", "")
