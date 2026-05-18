# ─────────────────────────────────────────────
# tools/__init__.py — 匯出所有工具（含外部 wiki/qmd）
# ─────────────────────────────────────────────
import sys
from pathlib import Path

from tools.pdf_tools   import read_pdf_text
from tools.file_tools  import overwrite_file
from tools.video_tools import analyze_video
from tools.wiki_tools  import read_wiki_file, list_wiki_files, write_wiki_file, append_log, search_wiki, run_lint, list_unprocessed_raw_files
from tools.qmd_tools import qmd_query, qmd_status, qmd_reindex


# ── 所有工具的完整清單（供 agent 使用） ──
ALL_TOOLS = [
    # 原始資料工具
    read_pdf_text,
    overwrite_file,
    analyze_video,
    # Wiki 工具
    read_wiki_file,
    list_wiki_files,
    list_unprocessed_raw_files,
    write_wiki_file,
    append_log,
    search_wiki,
    run_lint,
    # QMD 工具
    qmd_query,
    qmd_status,
    qmd_reindex,
]

__all__ = ["ALL_TOOLS"]
