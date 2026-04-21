import os
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from transformers import pipeline

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lmm import model, processor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATHS = ["/.deepagents/AGENTS.md"]
SKILL_PATHS = ["/.deepagents/skills/"]


def search_local_data(query: str) -> str:
    """搜尋本地資料的示範工具。"""
    print(f"[工具] 搜尋本地資料: {query}")
    return f"目前只接上了示範搜尋工具，尚未實作 '{query}' 的實際資料查詢。"


def calculate_math(expression: str) -> str:
    """使用工具執行精確數學運算。"""
    print(f"[工具] 數學計算: {expression}")
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"計算失敗: {exc}"


def build_chat_model() -> ChatHuggingFace:
    text_generation_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=processor.tokenizer,
        max_new_tokens=1024,
        return_full_text=False,
    )
    llm = HuggingFacePipeline(pipeline=text_generation_pipeline)
    return ChatHuggingFace(llm=llm)


def build_agent():
    backend = FilesystemBackend(root_dir=str(PROJECT_ROOT))
    return create_deep_agent(
        model=build_chat_model(),
        tools=[search_local_data, calculate_math],
        backend=backend,
        memory=MEMORY_PATHS,
        skills=SKILL_PATHS,
        system_prompt="請善用工具來回答使用者的問題。",
    )


print("正在初始化 LangChain Deep Agent...")
agent = build_agent()


def run_agent(prompt: str):
    print(f"\n使用者: {prompt}")
    print("Agent 思考中...")

    try:
        result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
        final_message = result["messages"][-1].content
        print(f"\nAgent 回覆:\n{final_message}")
        return final_message
    except Exception as exc:
        print(f"\nAgent 執行失敗: {exc}")
        print("提示：Deep Agents 需要支援 tool calling 的 chat model，若模型不支援，skills 與工具都不會正常運作。")
        return None


if __name__ == "__main__":
    print("\nDeep Agent 已啟動，輸入 'exit' 或 'quit' 可離開。")
    print("你可以直接問一般問題，或要求它做數學計算，例如 123 * 456。")
    print("-" * 50)

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
        if user_input:
            run_agent(user_input)
