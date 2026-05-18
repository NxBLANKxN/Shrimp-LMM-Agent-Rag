# ─────────────────────────────────────────────
# deep_agent.py — DeepAgent 實例建立
# ─────────────────────────────────────────────
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

from config import ROOT_DIR, AGENT_DIR, KNOWLEDGE_BASE, SKILLS_DIR
from llm import llm
from tools import ALL_TOOLS

checkpointer = MemorySaver()

backend = FilesystemBackend(
    root_dir=ROOT_DIR,
    virtual_mode=True,
)

agent = create_deep_agent(
    model=llm,
    backend=backend,
    system_prompt="""
你是一位專業智慧蝦隻養殖 AI 助手。
""",
    skills=[f"./{SKILLS_DIR}"],
    memory=[f"./{AGENT_DIR}", f"./{KNOWLEDGE_BASE}"],
    tools=ALL_TOOLS,
    checkpointer=checkpointer,
)
