# ─────────────────────────────────────────────
# llm.py — LLM 實例（切換時只改這裡）
# ─────────────────────────────────────────────
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config import LLAMA_URL, LLAMA_MODEL

# ── 本機 llama.cpp（預設） ──
llm = ChatOpenAI(
    base_url=LLAMA_URL,
    api_key="not-needed",
    model=LLAMA_MODEL,
    max_tokens=200000,
)

# ── Google Gemini（備用，取消下方註解並將上方 llm 改為 llm = ... 即可） ──
"""
import os
llm = ChatGoogleGenerativeAI(
    api_key=os.environ.get("GOOGLE_API_KEY", ""),
    model="gemma-4-31b-it",
    max_tokens=200000,
)
"""
