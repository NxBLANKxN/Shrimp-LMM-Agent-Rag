# ─────────────────────────────────────────────
# tools/pdf_tools.py — PDF 相關工具
# ─────────────────────────────────────────────
import fitz
from pathlib import Path
from langchain.tools import tool
from config import ROOT_DIR


@tool
def read_pdf_text(file_path: str) -> str:
    """
    讀取 PDF 純文字內容。可以傳入相對路徑或只有檔名，系統會自動在 raw/ 內尋找。
    """
    possible_paths = [
        Path(ROOT_DIR) / file_path,
        Path(ROOT_DIR) / "knowledge-base" / "raw" / file_path,
    ]

    target_path = None
    for p in possible_paths:
        if p.exists() and p.is_file():
            target_path = p
            break

    # 如果還是找不到，嘗試用檔名全域搜尋 knowledge-base/raw
    if not target_path:
        raw_root = Path(ROOT_DIR) / "knowledge-base" / "raw"
        basename = Path(file_path).name
        for p in raw_root.rglob("*.pdf"):
            if p.name == basename:
                target_path = p
                break

    if not target_path or not target_path.exists():
        return f"❌ 無法讀取 PDF：找不到檔案 '{file_path}'"

    try:
        text = ""
        with fitz.open(str(target_path)) as doc:
            for page in doc:
                text += page.get_text()

        if not text.strip():
            return "PDF 無法提取文字，可能是掃描檔"

        return text

    except Exception as e:
        return f"❌ 讀取 PDF 發生錯誤：{str(e)}"
