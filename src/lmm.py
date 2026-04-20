from transformers import AutoProcessor, AutoModelForCausalLM, TextStreamer,BitsAndBytesConfig
import torch
# import av
# import numpy as np
import os
# from fastapi import FastAPI
# import uvicorn
# import cv2  # 新增：用於處理影片
# from PIL import Image

MODEL_ID = "google/gemma-4-E4B-it"
VIDEO_PATH = r"D:\VS code file\Shrimp-LMM-Agent-Rag\video\20260306.mov"

model_kwargs = {
    "dtype": torch.bfloat16,
    "device_map": "auto",
    "quantization_config": BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_storage=torch.bfloat16,
    )
}


# 1. Load model & processor
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    #dtype= "auto",
    #device_map= "auto"
    **model_kwargs
)
streamer = TextStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=False)
'''
def read_video(path):
    """利用 PyAV 讀取完整影片數據"""
    container = av.open(path)
    frames = []
    for frame in container.decode(video=0):
        frames.append(frame.to_image())
    return frames
'''

#-------------
# chat model
#-------------

print("\n✅ 載入完成！你可以開始對話了 (輸入 'exit' 或 'quit' 結束)")
print("👉 [純文字] 直接輸入")
print("👉 [影音/圖片] 輸入 'path:檔案路徑 問題'")
print("-" * 50)


while True:
    user_raw = input("\n👤 你: ").strip()
    if user_raw.lower() in ['exit', 'quit']: break
    if not user_raw: continue

    # 構建訊息
    messages = []

    if user_raw.startswith("path:"):
        try:
            
            raw_content = user_raw[5:].strip() # 5 是 "path:" 的長度
            
            if " " in raw_content:
                file_path, prompt_text = raw_content.split(" ", 1)
            else:
                file_path = raw_content
                prompt_text = "描述此內容"
            
            # 取得副檔名判斷類型
            _, ext_raw = os.path.splitext(file_path)
            ext =ext_raw.lower()
            
            # 構建官方格式的 messages
            if ext in ['.mp4', '.mov', '.avi', '.mkv']:
                media_content = {"type": "video", "video": file_path} 
            elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                media_content = {"type": "image", "image": file_path} 
            else:
                print(f"⚠️ 不支援的格式 {ext}")
                continue
                
            messages = [{
                "role": "user",
                "content": [media_content, {"type": "text", "text": prompt_text}]
            }]
            print(f"🔍 正在載入並分析: {file_path}")
            
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            continue
    else:
        # 純文字模式
        messages = [{
            "role": "user",
            "content": [{"type": "text", "text": user_raw}]
        }]


    try:
        # 處理輸入
        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            add_generation_prompt=True,
            enable_thinking=False, # 👈 保持思考過程顯示
            processor_kwargs={
                "video_kwargs": {"num_frames": 8}
            }
        ).to(model.device)

    # 執行生成 (會透過 streamer 一邊算一邊噴字)
        print("\n🧠 思考中...")
        with torch.no_grad(): # 節省顯存開銷
            model.generate(
                **inputs,
                streamer=streamer,
                max_new_tokens=512,
                use_cache=True
            )
    except Exception as e:
        print(f"❌ 生成失敗: {e}")
        print("💡 提示：請嘗試較短的影片。")
    print("\n" + "-" * 50)

#-------------
# code input
#-------------
'''
def extract_frames(video_path, num_frames=4):
    cap = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    for i in range(num_frames):

        cap.set(cv2.CAP_PROP_POS_FRAMES, i * (total_frames // num_frames))
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame)
        pil_img.thumbnail((448, 448)) 
        frames.append(pil_img)
    cap.release()
    return frames


video_frames = extract_frames(VIDEO_PATH, num_frames=4)

messages = [
     {
        "role": "user",
        "content": [
            {"type": "text", "text": "你好,請問你是誰,你能為我做甚麼,用中文回答"},
        ],
    }
]

# 3. 後續處理 (保持不變)
inputs = processor.apply_chat_template(
    messages,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
    add_generation_prompt=True,
    enable_thinking=False
).to(model.device)

input_len = inputs["input_ids"].shape[-1]

streamer = TextStreamer(processor,skip_prompt=True, skip_special_tokens=False)


# 🔍 Debug 檢查
print(f"✅ Model device: {next(model.parameters()).device}")
print(f"✅ eos_token_id: {model.config.eos_token_id} (type: {type(model.config.eos_token_id)})")
print(f"✅ pad_token_id: {model.config.pad_token_id} (type: {type(model.config.pad_token_id)})")
print(f"✅ Input device: {inputs['input_ids'].device}")

# 檢查是否有 meta tensor
if any(p.device.type == "meta" for p in model.parameters()):
    print("❌ 警告：模型仍在 meta device！請檢查 accelerate / device_map 設定")


# Generate output
outputs = model.generate(**inputs,streamer = streamer, max_new_tokens=1024,use_cache=True)
response = processor.decode(outputs[0][input_len:], skip_special_tokens=False)

# Parse output
processor.parse_response(response)
# print ('\n')
# print (response)
'''

#-------------
# API server
#-------------
'''
app = FastAPI(title="Gemma 4 API Service")

class ChatRequest(BaseModel):
    prompt: str
    enable_thinking: bool = True

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # 2. 構建訊息格式
    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": request.prompt}],
        }
    ]

    # 3. 處理輸入
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        add_generation_prompt=True,
        enable_thinking=request.enable_thinking  # 根據請求決定是否顯示思考
    ).to(model.device)

    input_len = inputs["input_ids"].shape[-1]

    # 這裡的 streamer 會在伺服器端的終端機顯示過程
    streamer = TextStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=False)

    # 4. 生成輸出
    outputs = model.generate(
        **inputs,
        streamer=streamer,
        max_new_tokens=1024,
        use_cache=True
    )

    # 5. 解碼並回傳
    response = processor.decode(outputs[0][input_len:], skip_special_tokens=False)
    return {"response": response}

if __name__ == "__main__":
    # 在 WSL 運行，port 設為 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
