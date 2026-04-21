import os
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent
import torch
from transformers import AutoProcessor, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig
from deepagents.backends.filesystem import FilesystemBackend
from langchain.tools import tool
from deepagents.backends import LocalShellBackend


# 先透過 init_chat_model 初始化模型
model = init_chat_model(
    model="google/gemma-4-E4B-it",
    model_provider="huggingface",
    model_kwargs = {
        "dtype": torch.bfloat16,
        "device_map": "auto",
        "quantization_config": BitsAndBytesConfig(
            load_in_2bit=True,
            bnb_2bit_use_double_quant=True,
            bnb_2bit_quant_type="nf2",
            bnb_2bit_compute_dtype=torch.bfloat16,
            bnb_2bit_quant_storage=torch.bfloat16,
            temperature=0.7,
            max_tokens=512,
            enable_thinking=False
        )
    },
    skills=["skills/"],
    memory=["AGENTS.md"],
    
)

checkpointer = MemorySaver()

@tool
def read_file(path: str) -> str:
    """Read a file from the filesystem and return its content."""
    try:
        # 1. 檢查檔案是否存在
        if not os.path.exists(path):
            return f"❌ 錯誤：找不到路徑 '{path}'"
        
        # 2. 檢查是否為檔案而非目錄
        if not os.path.isfile(path):
            return f"❌ 錯誤：'{path}' 是一個目錄，不是檔案"

        # 3. 讀取內容 (建議加上編碼處理)
        with open(path, 'r', encoding='utf-8') as f:
            # 💡 關鍵：限制讀取長度（例如前 5000 字），防止爆顯存
            content = f.read(5000) 
            
            if not content:
                return f"檔案 '{path}' 是空的。"
            
            return content

    except UnicodeDecodeError:
        return f"❌ 錯誤：無法讀取 '{path}'。這可能不是文字檔（例如圖檔或二進制檔）。"
    except Exception as e:
        return f"❌ 讀取檔案時發生預期外的錯誤：{str(e)}"

# 再將初始化好的模型傳給 create_deep_agent
agent = create_deep_agent(
    model=model,
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    tools=[read_file],
    interrupt_on={"read_file": True},
    checkpointer=checkpointer
)

os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    print("✅ Agent 初始化完成！可以開始對話。輸入 'quit' 或 'exit' 來結束對話。")
    print("-" * 50)
    
    while True:
        user_input = input("\n你: ")
        if user_input.strip().lower() in ["quit", "exit"]:
            print("再見！")
            break

        thread_config = {"configurable": {"thread_id": "user_001"}}
        print("\nDeep Agent: ", end="", flush=True)

        try:
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config=thread_config,
                stream_mode="messages" # 這裡選擇以訊息模式流式輸出
            ):
                # chunk 是一個元組 (message, metadata)
                message_chunk, metadata = chunk
            
                # 只印出 content 部分，實現打字機效果
                if message_chunk.content:
                    print(message_chunk.content, end="", flush=True)
          
            print() # 完成後換行
        
        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")