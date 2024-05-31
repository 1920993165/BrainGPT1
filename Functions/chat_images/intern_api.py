import os
import torch
from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModel
import uvicorn, json, datetime
import base64
import json


def get_model():
    torch.set_grad_enabled(False)

    # init model and tokenizer
    path='../../Models/internlm-xcomposer2-4khd-7b'
    model = AutoModel.from_pretrained(path, torch_dtype=torch.bfloat16, trust_remote_code=True).cuda().eval()
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)

    return tokenizer, model

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE

def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


app = FastAPI()


@app.post("/")
async def create_item(request: Request):
    global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    image_base64_string = json_post_list.get('image_base64_string')
    history=json_post_list.get('history')
    file_name=json_post_list.get('file_name')
    # 检查Base64字符串是否包含数据URI前缀，如果有则移除它
    if isinstance(image_base64_string, str) and image_base64_string=='':
        query = prompt
    else:
        query = '<ImageHere>'+prompt
        if image_base64_string.startswith('data:image'):
            # 分割字符串以去除数据URI前缀
            image_base64_string = image_base64_string.split(',', 1)[1]

        # Base64字符串解码为二进制数据
        image_data = base64.b64decode(image_base64_string)

        # 将二进制数据写入文件
        with open(file_name, 'wb') as file:
            file.write(image_data)

        print(f'Image saved to {file_name}')

    with torch.cuda.amp.autocast():
        response, history = model.chat(tokenizer, query=query, image=file_name, hd_num=55, history=history, do_sample=False, num_beams=3)

    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": time
    }
    log = "[" + time + "] " + '", prompt:"' + prompt + '", response:"' + repr(response) + '"'
    print(log)
    return answer


if __name__ == '__main__':
    
    tokenizer, model = get_model()
    model = model.eval()
    uvicorn.run(app, host='0.0.0.0', port=6003, workers=1)

