# -*- coding: utf-8 -*-
"""
真實 E2E：對 POST /chat 送 ingest 自然語言，串流讀完後掃描 wiki/sources。

進度：
- 即時印終端機（UTF-8）
- **同步寫** knowledge-base/output/e2e-ingest-live.log（不依賴 PowerShell Tee）
- **watchdog** 寫 e2e-watchdog.log，證明主緒仍活著

執行（於 Agent_Server，不要再用 Tee 包一層）：
  .\\.venv\\Scripts\\python.exe -u scripts\\e2e_ingest_chat.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient

TEXT = (
    "幫我攝取並分析現在有的PDF資料，請依照既有skills流程處理並寫入知識庫。"
    " 每個 PDF 至少一則 sources/<slug>.md，最後 append_log。"
)
THREAD = f"e2e-ingest-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

_STREAM_STATUS_INTERVAL_SEC = 4.0
_HEARTBEAT_LINES = 80


def _ts(t0: float) -> str:
    return f"{time.monotonic() - t0:7.1f}s"


def artifact_snapshot() -> str:
    src = ROOT / "knowledge-base" / "wiki" / "sources"
    if not src.exists():
        return "sources/: (目錄不存在)"
    mds = sorted(src.glob("*.md"))
    lines = [f"sources/*.md 數量: {len(mds)}"]
    for p in mds[:40]:
        lines.append(f"- {p.name}")
    if len(mds) > 40:
        lines.append(f"... 其餘 {len(mds) - 40} 個")
    return "\n".join(lines)


def _run_watchdog(t0: float, stop: threading.Event) -> None:
    wpath = ROOT / "knowledge-base" / "output" / "e2e-watchdog.log"
    wpath.parent.mkdir(parents=True, exist_ok=True)
    wpath.write_text(
        f"watchdog start iso={datetime.now().isoformat()}\n", encoding="utf-8"
    )
    while not stop.wait(8.0):
        elapsed = time.monotonic() - t0
        with wpath.open("a", encoding="utf-8") as wf:
            wf.write(
                f"{elapsed:8.1f}s 主緒仍阻塞在讀 SSE（正常＝等模型/tool；看 e2e-ingest-live.log）\n"
            )
            wf.flush()


def main() -> int:
    import agent as agent_mod  # noqa: WPS433

    t0 = time.monotonic()
    out_dir = ROOT / "conversation_history"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = out_dir / f"e2e-ingest-{stamp}.md"

    live_path = ROOT / "knowledge-base" / "output" / "e2e-ingest-live.log"
    live_path.parent.mkdir(parents=True, exist_ok=True)
    live_fp = live_path.open("w", encoding="utf-8", buffering=1)

    def _log(msg: str) -> None:
        line = f"[{_ts(t0)}] {msg}"
        print(line, flush=True)
        live_fp.write(line + "\n")
        live_fp.flush()

    stop_watch = threading.Event()
    threading.Thread(
        target=_run_watchdog, args=(t0, stop_watch), daemon=True
    ).start()

    before = artifact_snapshot()
    _log(f"thread={THREAD}")
    _log("執行前 sources 快照：")
    for line in before.splitlines():
        _log(f"  {line}")

    client = TestClient(agent_mod.app)
    tools: list[str] = []
    text_parts: list[str] = []
    raw_lines: list[str] = []
    last_stream_log = 0.0
    reply_chars = 0

    _log("POST /chat（iter_bytes 解析 SSE）")
    _log("live: " + str(live_path))
    _log("watchdog: " + str(ROOT / "knowledge-base/output/e2e-watchdog.log"))

    sse_done = False
    try:
        with client.stream(
            "POST",
            "/chat",
            data={"text": TEXT, "thread_id": THREAD},
        ) as resp:
            if resp.status_code != 200:
                log_path.write_text(
                    f"# E2E 失敗 HTTP {resp.status_code}\n\n{resp.text[:8000]}",
                    encoding="utf-8",
                )
                _log(f"HTTP 失敗 {resp.status_code}，已寫 {log_path}")
                live_fp.close()
                return 1

            _log(f"HTTP {resp.status_code}，讀 body…")
            buf = b""
            for chunk in resp.iter_bytes(chunk_size=4096):
                if sse_done:
                    break
                if not chunk:
                    continue
                buf += chunk
                while b"\n" in buf:
                    raw_line, buf = buf.split(b"\n", 1)
                    line = raw_line.decode("utf-8", errors="replace").rstrip("\r")
                    if line == "":
                        continue
                    raw_lines.append(line)

                    n = len(raw_lines)
                    if n % _HEARTBEAT_LINES == 0:
                        _log(f"SSE 已解析 {n} 行…")

                    if not line.startswith("data:"):
                        s = line.strip()
                        if s.startswith(":") or "ping" in s.lower():
                            _log(f"sse-keepalive: {s[:120]}")
                        elif s:
                            _log(f"sse(非 data): {line[:200]}")
                        continue

                    raw = line.split(":", 1)[1].strip() if ":" in line else ""
                    if raw == "[DONE]":
                        _log("SSE [DONE]")
                        sse_done = True
                        break

                    try:
                        obj = json.loads(raw)
                    except json.JSONDecodeError:
                        _log(f"sse JSON 失敗: {raw[:160]!r}")
                        continue

                    st = obj.get("status")
                    if st:
                        if "Executing tool:" in st:
                            m = re.search(r"Executing tool:\s*(\S+)", st)
                            name = m.group(1) if m else "?"
                            tools.append(name)
                            _log(f">>> TOOL {name}")
                        elif "Model starting" in st or "Entering:" in st:
                            _log(st)
                        elif "Streaming" in st:
                            now = time.monotonic()
                            if now - last_stream_log >= _STREAM_STATUS_INTERVAL_SEC:
                                _log(f"{st}（reply 累計 {reply_chars} 字）")
                                last_stream_log = now
                        else:
                            _log(f"status: {st}")

                    delta = (obj.get("choices") or [{}])[0].get("delta") or {}
                    t = delta.get("content")
                    if t:
                        text_parts.append(t)
                        reply_chars += len(t)
    finally:
        stop_watch.set()

    after = artifact_snapshot()
    _log("— 串流結束 —")
    _log("執行後 sources 快照：")
    for line in after.splitlines():
        _log(f"  {line}")
    live_fp.close()

    report = "\n".join(
        [
            "---",
            "type: e2e-ingest-log",
            f"thread: {THREAD}",
            "---",
            "",
            "## 提示詞",
            "",
            TEXT,
            "",
            "## 執行前 wiki/sources",
            "",
            before,
            "",
            "## 執行後 wiki/sources",
            "",
            after,
            "",
            "## 工具呼叫順序",
            "",
            "\n".join(f"{i+1}. `{x}`" for i, x in enumerate(tools)) or "(無)",
            "",
            "## 模型回覆（串流拼接）",
            "",
            "".join(text_parts) or "(空)",
            "",
            "## SSE 行數",
            "",
            str(len(raw_lines)),
            "",
            f"## 總耗時約 {_ts(t0).strip()}",
            "",
        ]
    )
    log_path.write_text(report, encoding="utf-8")
    print(f"[{_ts(t0)}] 完整報告: {log_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
