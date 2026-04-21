from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Optional
import torch

from lmm import model, processor, prepare_multimodal_messages

app = FastAPI(title="Gemma Multimodal API Service")

class ChatRequest(BaseModel):
    prompt: str
    file_path: Optional[str] = None
    enable_thinking: bool = False

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. 構建訊息格式
        messages = prepare_multimodal_messages(
            prompt=request.prompt, 
            file_path=request.file_path
        )

        # 2. 處理輸入
        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            add_generation_prompt=True,
            enable_thinking=request.enable_thinking,
            processor_kwargs={
                "video_kwargs": {"num_frames": 8}
            }
        ).to(model.device)

        input_len = inputs["input_ids"].shape[-1]

        # 3. 生成輸出
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1024,
                use_cache=True
            )

        # 4. 解碼並回傳
        response = processor.decode(outputs[0][input_len:], skip_special_tokens=True)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 在本機運行，port 設為 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
