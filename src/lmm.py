from transformers import AutoProcessor, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig
import torch
import os

MODEL_ID = "google/gemma-4-E4B-it"

model_kwargs = {
    "torch_dtype": torch.bfloat16,
    "device_map": "auto",
    "quantization_config": BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_storage=torch.bfloat16,
    )
}

print("🔄 正在載入模型與處理器，請稍候...")
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    **model_kwargs
)
streamer = TextStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=False)
print("✅ 模型載入完成！")

def prepare_multimodal_messages(prompt: str, file_path: str = None) -> list:
    """
    根據傳入的 prompt 與可選的 file_path，構建適合 Gemma 多模態模型的 messages 格式。
    自動判斷 file_path 是圖片還是影片。
    """
    if not file_path:
        return [{
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        }]

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到檔案: {file_path}")

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext in ['.mp4', '.mov', '.avi', '.mkv']:
        media_content = {"type": "video", "video": file_path}
    elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
        media_content = {"type": "image", "image": file_path}
    else:
        raise ValueError(f"不支援的副檔名格式: {ext}")

    return [{
        "role": "user",
        "content": [media_content, {"type": "text", "text": prompt}]
    }]
