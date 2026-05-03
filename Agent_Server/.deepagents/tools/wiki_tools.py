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

import subprocess
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

# ── 路徑常數（相對於 agent.py 的工作目錄）──────────────────────────
WIKI_ROOT = Path("./knowledge-base/wiki")
RAW_ROOT = Path("./knowledge-base/raw")
LOG_FILE  = WIKI_ROOT / "log.md"
LINT_SCRIPT = Path("./knowledge-base/scripts/lint.py")


def _resolve(relative_path: str) -> Path:
    """把使用者傳入的相對路徑解析到 wiki 根目錄，防止路徑穿越。"""
    resolved = (WIKI_ROOT / relative_path).resolve()
    if not str(resolved).startswith(str(WIKI_ROOT.resolve())):
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
        for f in sorted(base.rglob("*.md")):
            rel = f.relative_to(WIKI_ROOT)
            try:
                first_line = f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
            except Exception:
                first_line = "(無法讀取)"
            lines.append(f"wiki/{rel} — {first_line}")

        return "\n".join(lines) if lines else "（wiki 目錄目前是空的）"
    except Exception as e:
        return f"list_wiki_files 發生錯誤：{e}"


# ── 2.5 掃描未處理的 raw 檔案 ─────────────────────────────────────
@tool
def list_unprocessed_raw_files() -> str:
    """
    掃描 raw/ 目錄下所有的原始檔案，並比對 wiki/sources/ 中的紀錄。
    回傳所有「尚未被攝入 (INGEST)」的原始檔案路徑清單。
    適合用來進行批次處理或自動化掃描。
    """
    try:
        if not RAW_ROOT.exists():
            return "❌ 找不到 raw/ 目錄"
            
        all_raw_files = [str(f.relative_to(Path("."))) for f in RAW_ROOT.rglob("*") if f.is_file()]
        
        # 讀取已處理的來源
        processed_raw_files = set()
        sources_dir = WIKI_ROOT / "sources"
        if sources_dir.exists():
            import re
            for f in sources_dir.rglob("*.md"):
                try:
                    content = f.read_text(encoding="utf-8")
                    match = re.search(r"^raw_file:\s*(.+)$", content, re.MULTILINE)
                    if match:
                        val = match.group(1).strip().strip("'\"")
                        processed_raw_files.add(Path(val).name)
                except Exception:
                    pass
                    
        unprocessed = [f for f in all_raw_files if Path(f).name not in processed_raw_files]
        
        if not unprocessed:
            return "✅ 所有 raw/ 檔案皆已攝入完成，沒有未處理的檔案。"
            
        return "以下是尚未處理的原始檔案（請對它們逐一執行 INGEST）：\n" + "\n".join(unprocessed)
    except Exception as e:
        return f"list_unprocessed_raw_files 發生錯誤：{e}"


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
    在 wiki/ 目錄的所有 Markdown 檔案中，用 grep 搜尋關鍵字（大小寫不敏感）。
    適合 Query 前定位相關頁面，無需 embedding 或向量資料庫。

    Args:
        keyword:     要搜尋的關鍵字或短語，例如 '生物絮' 或 'BFT'
        max_results: 最多回傳幾條結果（預設 20）

    Returns:
        每行格式為 `wiki/<file>:<line_num>: <matched_line>`
    """
    try:
        result = subprocess.run(
            ["grep", "-rni", "--include=*.md", keyword, str(WIKI_ROOT)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 1:
            return f"🔍 在 wiki 中找不到關鍵字：{keyword}"
        if result.returncode != 0:
            return f"grep 執行失敗：{result.stderr.strip()}"

        lines = result.stdout.strip().splitlines()[:max_results]
        # 將絕對路徑縮短為相對路徑
        cleaned = []
        for line in lines:
            cleaned.append(line.replace(str(WIKI_ROOT) + "/", "wiki/"))
        return "\n".join(cleaned)
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
            ["python", str(LINT_SCRIPT)],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        return output.strip() if output.strip() else "✅ Lint 完成，無輸出（可能已寫入 lint.md）"
    except Exception as e:
        return f"run_lint 發生錯誤：{e}"
