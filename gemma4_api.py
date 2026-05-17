import yaml
from PIL import Image
import time
from transformers import AutoProcessor, AutoModelForMultimodalLM
import requests
import torch
from fastapi import FastAPI, Request
import uvicorn
import re
import threading

torch.backends.cudnn.enabled = False

model_id = "./gemma4_weights"
dtype = torch.bfloat16

model = AutoModelForMultimodalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=dtype,
).eval()
processor = AutoProcessor.from_pretrained(model_id)
print(f"Model device: {next(model.parameters()).device}")

app = FastAPI()

_av_lock = threading.Lock()

@app.post("/gemma4")
async def gemma4(request: Request):
    messages = await request.json()
    print(messages)

    with _av_lock:
        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)

    print("chat_template done!")

    input_len = inputs["input_ids"].shape[-1]
    inputs = inputs.to(model.device, dtype=model.dtype)

    with torch.inference_mode():
        generation = model.generate(**inputs, max_new_tokens=2000, do_sample=False)
        generation = generation[0][input_len:]

    print("generate done!")

    decoded = processor.decode(generation, skip_special_tokens=False)

    print("decode done!")
    print("out is👇")
    print(decoded)

    if "<channel|>" in decoded:
        answer_match = re.search(r'<channel\|>(.*?)$', decoded, re.DOTALL)
        answer = answer_match.group(1).strip()
        return answer.replace("<turn|>", "")
    else:
        return decoded.replace("<turn|>", "")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9999, workers=1)