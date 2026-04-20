import torch
from lmm import model, processor, streamer, prepare_multimodal_messages

def interactive_chat():
    print("\n✅ 你可以開始對話了 (輸入 'exit' 或 'quit' 結束)")
    print("👉 [純文字] 直接輸入問題")
    print("👉 [影音/圖片] 輸入 'path:檔案路徑 問題'")
    print("-" * 50)

    while True:
        user_raw = input("\n👤 你: ").strip()
        if user_raw.lower() in ['exit', 'quit']: 
            break
        if not user_raw: 
            continue

        prompt_text = user_raw
        file_path = None

        if user_raw.startswith("path:"):
            try:
                raw_content = user_raw[5:].strip()
                if " " in raw_content:
                    file_path, prompt_text = raw_content.split(" ", 1)
                else:
                    file_path = raw_content
                    prompt_text = "描述此內容"
                
                print(f"🔍 正在準備分析多媒體檔案: {file_path}")
            except Exception as e:
                print(f"❌ 參數解析錯誤: {e}")
                continue

        try:
            # 準備 messages
            messages = prepare_multimodal_messages(prompt=prompt_text, file_path=file_path)

            # 處理輸入
            inputs = processor.apply_chat_template(
                messages,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
                add_generation_prompt=True,
                enable_thinking=False,
                processor_kwargs={
                    "video_kwargs": {"num_frames": 8}
                }
            ).to(model.device)

            print("\n🧠 思考中...")
            with torch.no_grad():
                model.generate(
                    **inputs,
                    streamer=streamer,
                    max_new_tokens=1024,
                    use_cache=True
                )
        except Exception as e:
            print(f"❌ 執行失敗: {e}")
            print("💡 提示：請檢查路徑是否正確或影片是否過長。")
        
        print("\n" + "-" * 50)

if __name__ == "__main__":
    interactive_chat()
