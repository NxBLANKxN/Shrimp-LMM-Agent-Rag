import torch
from lmm import model, processor, prepare_multimodal_messages

def run_inference(prompt: str, media_path: str = None):
    print(f"\n[測試執行] 問題: {prompt}")
    if media_path:
        print(f"[測試執行] 檔案: {media_path}")

    try:
        messages = prepare_multimodal_messages(prompt, media_path)

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

        input_len = inputs["input_ids"].shape[-1]

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1024,
                use_cache=True
            )
            
        # 解碼回傳文字
        response = processor.decode(outputs[0][input_len:], skip_special_tokens=True)
        print(f"\n🤖 回覆:\n{response}")
        return response
    except Exception as e:
        print(f"❌ 推理失敗: {e}")
        return None

if __name__ == "__main__":
    # 您可以修改這裡來測試不同的輸入
    
    # 範例 1: 純文字
    run_inference(prompt="你好,請問你是誰,你能為我做甚麼,用中文回答")
    
    print("-" * 50)
    
    # 範例 2: 加上影片/圖片 (將路徑替換成您的實際檔案路徑)
    # run_inference(
    #     prompt="這段影片中發生了什麼事？",
    #     media_path=r"D:\VS code file\Shrimp-LMM-Agent-Rag\video\20260306.mov"
    # )
