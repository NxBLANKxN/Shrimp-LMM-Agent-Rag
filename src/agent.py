import sys
import os

# 確保能找到 lmm
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
from deepagents import create_deep_agent

# 從我們剛才整理好的核心模組載入已初始化的 Gemma 模型與處理器
from lmm import model, processor

print("🔧 正在初始化 LangChain 與 Deep Agent 環境...")

# 1. 將本地的 Gemma 模型包裝成 LangChain 的 Pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=processor.tokenizer,
    max_new_tokens=1024,
    return_full_text=False # 避免重複輸出 prompt
)

# 2. 轉換為 LangChain LLM
llm = HuggingFacePipeline(pipeline=pipe)

# 3. 轉換為支援對話格式的 Chat Model (確保能處理 HumanMessage/AIMessage)
chat_model = ChatHuggingFace(llm=llm)

# 4. 定義 Agent 可用的工具 (Tools)
# 您專案名為 Shrimp-LMM-Agent-Rag，這裡我們先示範一個簡單的檢索工具
def search_local_data(query: str) -> str:
    """搜尋本地端知識庫的工具。
    
    Args:
        query: 想要搜尋的關鍵字或問題
    """
    print(f"🛠️ [工具執行中] 正在搜尋: {query}")
    return f"這是一個模擬的檢索結果，關於 '{query}' 的資訊是：本地端資料庫尚未建立完整索引。"

def calculate_math(expression: str) -> str:
    """處理精確數值運算的數學計算機工具。
    
    Args:
        expression: 數學運算式 (例如 100 * 0.8)
    """
    print(f"🛠️ [工具執行中] 正在計算: {expression}")
    try:
        return str(eval(expression))
    except Exception as e:
        return f"計算錯誤: {e}"

# 5. 建立 Deep Agent
agent = create_deep_agent(
    model=chat_model,
    tools=[search_local_data, calculate_math],
    # 這裡的 prompt 會與 .deepagents/agent.md 自動結合
    system_prompt="請善用工具來回答使用者的問題。"
)

def run_agent(prompt: str):
    print(f"\n👤 使用者: {prompt}")
    print("🧠 Agent 思考與執行中...")
    
    try:
        # 執行 Agent
        result = agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
        
        # 取得最後一則訊息 (Agent 的最終回答)
        final_message = result["messages"][-1].content
        print(f"\n🤖 Agent 回覆:\n{final_message}")
        return final_message
    except Exception as e:
        print(f"\n❌ Agent 執行發生錯誤: {e}")
        print("💡 提示：如果出現 bind_tools 錯誤，可能是因為目前的 Gemma 模型 Chat Template 不原生支援工具綁定，您可能需要額外設計 ReAct 的 Prompting。")

if __name__ == "__main__":
    print("\n🤖 Deep Agent 已啟動！(輸入 'exit' 或 'quit' 離開)")
    print("💡 提示：您可以問它「什麼是 RAG？」或是請它「算一下 123 乘以 456」來測試技能。")
    print("-" * 50)
    
    while True:
        user_input = input("\n👤 說些什麼：").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        if user_input:
            run_agent(user_input)
