import json
import os
import subprocess
import sys
from pathlib import Path

from langchain_core.tools import tool

# 以檔案位置固定 knowledge-base，避免 process cwd 不在 Agent_Server 時失敗
_ROOT = Path(__file__).resolve().parents[2]
ROOT_DIR = str(_ROOT / "knowledge-base")


def _qmd_cmd_base() -> list[str]:
    """
    取得 qmd 執行基底指令。
    一律用與 agent 相同的直譯器執行 `python -m qmd`，避免 Windows 上 PATH 的 npm/qmd
    shim（常依賴 /bin/sh）導致 CreateProcess 失敗。
    """
    return [sys.executable, "-m", "qmd"]


def _run_qmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    # Windows 預設 pipe 解碼常為 cp950，qmd 輸出含 UTF-8/emoji 會炸；子行程也強制 UTF-8 避免其內部 print 失敗
    child_env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        _qmd_cmd_base() + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT_DIR,
        env=child_env,
    )


def _pick_default_collection() -> str | None:
    """
    從 `qmd collection list` 解析第一個 collection 名稱。
    PyPI qmd 目前輸出為 JSON 陣列，元素為 {"name": "...", ...}。
    """
    result = _run_qmd(["collection", "list"])
    if result.returncode != 0:
        return None
    raw = (result.stdout or "").strip()
    if not raw or raw == "[]":
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list) or not data:
        return None
    first = data[0]
    if isinstance(first, dict) and "name" in first:
        name = first["name"]
        return str(name) if name else None
    if isinstance(first, str):
        return first
    return None


def _default_collection_name() -> str:
    """無任何 collection 時，用固定名稱讓 document add 建立索引。"""
    return "wiki"


@tool
def qmd_query(question: str) -> str:
    """
    使用 qmd 搜尋知識庫內容。
    適合回答蝦子疾病、養殖、水質、研究文獻等問題。
    """

    try:
        collection = _pick_default_collection() or _default_collection_name()

        result = _run_qmd(
            ["search", "--collection", collection, "--query", question, "--top-k", "8"]
        )

        if result.returncode != 0:
            return f"qmd 查詢失敗：{result.stderr or result.stdout}"

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
        result = _run_qmd(["collection", "list"])
        if result.returncode != 0:
            return f"qmd 狀態查詢失敗：{result.stderr or result.stdout}"
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
        collection = _pick_default_collection() or _default_collection_name()
        wiki_root = Path(ROOT_DIR) / "wiki"
        if not wiki_root.exists():
            return f"qmd 重建索引失敗：找不到 {wiki_root}"

        added = 0
        errors: list[str] = []
        for md in sorted(wiki_root.rglob("*.md")):
            rel = md.relative_to(wiki_root).as_posix()
            doc_id = rel.replace("/", "__")
            result = _run_qmd(
                [
                    "document",
                    "add",
                    "--collection",
                    collection,
                    "--document-id",
                    doc_id,
                    "--markdown-file",
                    str(md),
                ]
            )
            if result.returncode != 0:
                err = (result.stderr or result.stdout or "").strip()
                errors.append(f"{rel}: {err}")
                continue
            added += 1

        summary = (
            f"qmd 重新索引完成：collection={collection}，成功加入 {added} 份 markdown。"
        )
        if errors:
            summary += "\n部分失敗：\n" + "\n".join(errors[:20])
            if len(errors) > 20:
                summary += f"\n... 另有 {len(errors) - 20} 筆錯誤"
        return summary

    except Exception as e:
        return str(e)