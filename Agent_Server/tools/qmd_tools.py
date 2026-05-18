import subprocess
from langchain_core.tools import tool

ROOT_DIR = "./knowledge-base"


@tool
def qmd_query(question: str) -> str:
    """
    使用 qmd 搜尋知識庫內容。
    適合回答蝦子疾病、養殖、水質、研究文獻等問題。
    """

    try:
        result = subprocess.run(
            ["qmd", "query", question],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR
        )

        if result.returncode != 0:
            return f"qmd 查詢失敗：{result.stderr}"

        return result.stdout

    except Exception as e:
        return f"執行 qmd_query 發生錯誤：{str(e)}"


@tool
def qmd_status(_: str = "") -> str:
    """
    查看 qmd 索引狀態。
    適合知識庫健康檢查。
    """

    try:
        result = subprocess.run(
            ["qmd", "status"],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR
        )

        return result.stdout

    except Exception as e:
        return str(e)


@tool
def qmd_reindex(_: str = "") -> str:
    """
    重建知識庫索引。
    當新增大量文件或搜尋異常時使用。
    """

    try:
        result = subprocess.run(
            ["qmd", "add", "wiki/"],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR
        )

        return result.stdout

    except Exception as e:
        return str(e)