from transformers import AutoProcessor, AutoModelForCausalLM 
import torch
import cv2  # 新增：用於處理影片
from PIL import Image

MODEL_ID = "google/gemma-4-E4B-it"
VIDEO_PATH = r"D:\VS code file\Shrimp-LMM-Agent-Rag\video\20260306.mov"

# 1. Load model & processor
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype="auto",
    device_map="auto",
)


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
            *[{"type": "image", "image": f} for f in video_frames],
            {"type": "text", "text": "圖中的蝦子有幾隻,給我他們每一隻大概的位置,用中文回答"},
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
).to(model.device)

input_len = inputs["input_ids"].shape[-1]

# Generate output
outputs = model.generate(**inputs, max_new_tokens=512)
response = processor.decode(outputs[0][input_len:], skip_special_tokens=False)

# Parse output
processor.parse_response(response)
print(response)