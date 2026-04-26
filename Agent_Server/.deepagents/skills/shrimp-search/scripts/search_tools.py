import os
from langchain_core.tools import tool

BASE_DIR = "/opt/Shrimp-LMM-Agent-Rag"

@tool
def list_files_in_directory(directory_path: str = "data/uploads"):
    """
    列出指定資料夾內的所有檔案。
    可用於清查上傳影片(data/uploads)、追蹤紀錄(data/processed/tracks)或關鍵影格(data/processed/frames)。
    預設路徑為 'data/uploads'。
    """
    # 確保路徑安全且相對於 BASE_DIR
    target_path = os.path.join(BASE_DIR, directory_path)
    
    if not os.path.exists(target_path):
        return f"錯誤：找不到路徑 '{directory_path}'。"
    
    if not os.path.isdir(target_path):
        return f"錯誤：'{directory_path}' 並非一個資料夾。"

    try:
        files = os.listdir(target_path)
        if not files:
            return f"資料夾 '{directory_path}' 目前是空的。"
        
        # 區分資料夾與檔案，方便 Agent 判讀
        items = []
        for f in sorted(files):
            full_path = os.path.join(target_path, f)
            if os.path.isdir(full_path):
                items.append(f"[DIR] {f}")
            else:
                items.append(f"[FILE] {f}")
        
        return f"資料夾 '{directory_path}' 內容如下：\n" + "\n".join(items)
    except Exception as e:
        return f"讀取目錄時發生錯誤: {str(e)}"