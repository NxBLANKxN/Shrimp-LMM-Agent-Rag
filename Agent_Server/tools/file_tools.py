# ─────────────────────────────────────────────
# tools/file_tools.py — 通用檔案操作工具
# ─────────────────────────────────────────────
from langchain.tools import tool
from config import ROOT_DIR


@tool
def overwrite_file(file_path: str, content: str) -> str:
    """
    完全覆蓋現有檔案的內容。此工具用於替換檔案的全部內容，而非僅僅編輯特定字串。
    當目標是更新知識庫中檔案的完整內容時，應使用此工具。

    Args:
        file_path (str): 需要被覆蓋的檔案的相對路徑（相對於 ROOT_DIR）。
        content (str): 用來替換現有檔案的完整新文本內容。

    Returns:
        str: 執行操作結果訊息（成功或失敗）。
    """
    path = f"{ROOT_DIR}/{file_path}"
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功：檔案 '{file_path}' 的內容已完全覆蓋並更新。"
    except FileNotFoundError:
        return f"錯誤：找不到檔案 '{file_path}'。請確認路徑是否正確。"
    except Exception as e:
        return f"執行 overwrite_file 發生未知錯誤：{str(e)}"
