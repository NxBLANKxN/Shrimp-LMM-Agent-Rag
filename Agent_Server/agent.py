# ─────────────────────────────────────────────
# agent.py — 入口點（僅負責啟動 uvicorn）
# ─────────────────────────────────────────────
# 模組結構：
#   config.py        — 所有常數（路徑、URL 等）
#   llm.py           — LLM 實例（切換 LLM 只改這裡）
#   tools/
#     __init__.py    — 匯出 ALL_TOOLS 清單
#     pdf_tools.py   — read_pdf_text
#     file_tools.py  — overwrite_file
#     video_tools.py — analyze_video（OpenCV + Gemini vision）
#   file_handler.py  — 上傳分類 & 儲存（classify_file / save_upload_file）
#   deep_agent.py    — DeepAgent 實例
#   app.py           — FastAPI 應用、SSE 串流、路由
# ─────────────────────────────────────────────

from config import PORT

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True)