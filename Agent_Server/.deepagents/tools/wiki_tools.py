"""
llm-wiki 工具集
實作 Karpathy llm-wiki 模式的 Ingest / Query / Lint 三大操作所需的工具。

工具清單：
  - read_wiki_file   : 讀取 wiki 中任意 md 檔
  - list_wiki_files  : 列出 wiki 目錄下所有檔案（帶一行摘要）
  - write_wiki_file  : 寫入 / 覆蓋 wiki 的 md 檔
  - append_log       : 向 log.md 追加一條 append-only 記錄
  - search_wiki      : 在 wiki 目錄用 grep 搜尋關鍵字
  - run_lint         : 執行 scripts/lint.py，回傳健康報告
"""

import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

# ── 路徑常數（以本檔位置推導，不依賴 process cwd）────────────────────
# wiki_tools.py 位於 Agent_Server/.deepagents/tools/
_AGENT_SERVER = Path(__file__).resolve().parents[2]
_KB_ROOT = _AGENT_SERVER / "knowledge-base"
WIKI_ROOT = _KB_ROOT / "wiki"
LOG_FILE = WIKI_ROOT / "log.md"
LINT_SCRIPT = _KB_ROOT / "scripts" / "lint.py"


def _resolve(relative_path: str) -> Path:
    """把使用者傳入的相對路徑解析到 wiki 根目錄，防止路徑穿越。"""
    resolved = (WIKI_ROOT / relative_path).resolve()
    root = WIKI_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ValueError(f"路徑穿越攻擊被阻擋：{relative_path}")
    return resolved


# ── 1. 讀取 wiki 檔案 ─────────────────────────────────────────────
@tool
def read_wiki_file(relative_path: str) -> str:
    """
    讀取 wiki 目錄中的任意 Markdown 檔案。

    Args:
        relative_path: 相對於 wiki/ 的路徑，例如 'index.md'、'concepts/BFT.md'

    Returns:
        檔案的完整文字內容，或錯誤訊息。
    """
    try:
        path = _resolve(relative_path)
        if not path.exists():
            return f"❌ 找不到檔案：wiki/{relative_path}"
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"read_wiki_file 發生錯誤：{e}"


# ── 2. 列出 wiki 所有檔案 ─────────────────────────────────────────
@tool
def list_wiki_files(subdir: str = "") -> str:
    """
    列出 wiki 目錄（或子目錄）下所有 .md 檔案，並讀取每個檔案的第一行作為摘要。
    適合在 Query 前快速瀏覽知識庫結構。

    Args:
        subdir: 可選的子目錄，例如 'concepts'、'sources'。空字串代表整個 wiki/。

    Returns:
        每行格式為 `wiki/<path> — <第一行內容>`
    """
    try:
        base = (WIKI_ROOT / subdir).resolve() if subdir else WIKI_ROOT.resolve()
        if not base.exists():
            return f"❌ 目錄不存在：wiki/{subdir}"

        lines = []
        root = WIKI_ROOT.resolve()
        for f in sorted(base.rglob("*.md")):
            try:
                rel = f.resolve().relative_to(root)
            except Exception:
                # Windows 路徑大小寫/分隔符差異時，保底改用檔名
                rel = f.name
            try:
                first_line = f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
            except Exception:
                first_line = "(無法讀取)"
            lines.append(f"wiki/{rel} — {first_line}")

        return "\n".join(lines) if lines else "（wiki 目錄目前是空的）"
    except Exception as e:
        return f"list_wiki_files 發生錯誤：{e}"


# ── 3. 寫入 wiki 檔案 ────────────────────────────────────────────
@tool
def write_wiki_file(relative_path: str, content: str) -> str:
    """
    建立或完整覆蓋 wiki 目錄中的一個 Markdown 檔案。
    適合 Ingest 時寫入新的 source 摘要、concept 頁、entity 頁，或更新 index.md。

    Args:
        relative_path: 相對於 wiki/ 的路徑，例如 'sources/BFT-paper.md'
        content: 要寫入的完整 Markdown 文字

    Returns:
        成功或失敗訊息。
    """
    try:
        path = _resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"✅ 已寫入：wiki/{relative_path}"
    except Exception as e:
        return f"write_wiki_file 發生錯誤：{e}"


# ── 4. 追加 log 記錄 ──────────────────────────────────────────────
@tool
def append_log(action: str, title: str, detail: str = "") -> str:
    """
    向 wiki/log.md 追加一條 append-only 的操作記錄。
    格式：## [YYYY-MM-DD] <action> | <title>

    Args:
        action: 操作類型，例如 'ingest'、'query'、'lint'、'update'
        title:  本次操作的標題，例如文獻名稱或問題摘要
        detail: 可選的詳細描述，會附加在標題行下方

    Returns:
        成功或失敗訊息。
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n## [{today}] {action} | {title}\n"
        if detail:
            entry += f"{detail.strip()}\n"

        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(entry)

        return f"✅ Log 已記錄：[{today}] {action} | {title}"
    except Exception as e:
        return f"append_log 發生錯誤：{e}"


# ── 5. 搜尋 wiki ──────────────────────────────────────────────────
@tool
def search_wiki(keyword: str, max_results: int = 20) -> str:
    """
    在 wiki/ 目錄的所有 Markdown 檔案中，以純 Python 進行大小寫不敏感搜尋。
    適合 Query 前定位相關頁面，避免依賴系統 grep。

    Args:
        keyword:     要搜尋的關鍵字或短語，例如 '生物絮' 或 'BFT'
        max_results: 最多回傳幾條結果（預設 20）

    Returns:
        每行格式為 `wiki/<file>:<line_num>: <matched_line>`
    """
    try:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        root = WIKI_ROOT.resolve()
        matches: list[str] = []
        for f in sorted(root.rglob("*.md")):
            try:
                rel = f.resolve().relative_to(root)
                lines = f.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            for i, line in enumerate(lines, start=1):
                if pattern.search(line):
                    matches.append(f"wiki/{rel}:{i}: {line.strip()}")
                    if len(matches) >= max_results:
                        return "\n".join(matches)
        if not matches:
            return f"🔍 在 wiki 中找不到關鍵字：{keyword}"
        return "\n".join(matches)
    except Exception as e:
        return f"search_wiki 發生錯誤：{e}"


# ── 6. 執行 lint ──────────────────────────────────────────────────
@tool
def run_lint(_: str = "") -> str:
    """
    執行 knowledge-base/scripts/lint.py，對 wiki 進行健康檢查。
    會偵測：孤兒頁面、缺少交叉連結、index.md 遺漏條目、過時聲明等。
    結果同時寫入 knowledge-base/output/lint.md。

    Returns:
        lint 報告的文字輸出。
    """
    try:
        if not LINT_SCRIPT.exists():
            return f"❌ 找不到 lint 腳本：{LINT_SCRIPT}"

        result = subprocess.run(
            [sys.executable, str(LINT_SCRIPT.resolve())],
            capture_output=True,
            text=True,
            cwd=str(_AGENT_SERVER),
        )
        output = result.stdout + result.stderr
        return output.strip() if output.strip() else "✅ Lint 完成，無輸出（可能已寫入 lint.md）"
    except Exception as e:
        return f"run_lint 發生錯誤：{e}"
