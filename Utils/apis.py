import requests
from Utils.tools import log
from Functions.general_gpt.spark_lite import spark_lite_main


def braingpt(inputs, history,ips, role = None):
    
    url_b = f'http://{ips["braingpt"]}'
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "prompt": inputs,
        "history": history,
        "role": role if role else 'user'
    }
    res_brain = requests.post(url_b, headers=headers, json=data)
    response_data = res_brain.json()
    brain_data = response_data.get('response', '')
    history_b = response_data.get('history', '')
    log(f"brain_data : {brain_data}", 'INFO')        
    log(f"history_b : {history_b}", 'INFO')

    return res_brain.status_code,brain_data,history_b

def general(inputs, history_l,ips):

    url_l = f'http://{ips["generalgpt"]}'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "prompt": inputs,
        "history": history_l
    }
    res_language = requests.post(url_l, headers=headers, json=data)
    log(f"language is done", 'EVENT')
    assert res_language.status_code==200
    response_data = res_language.json()
    response_text = response_data.get('response', '')
    history_l = response_data.get('history', '')

    return response_data,res_language.status_code,response_text,history_l

def general_spark(inputs, history_l,spark_api_key):
    
    return spark_lite_main(
        appid=spark_api_key['appid'],
        api_secret=spark_api_key['api_secret'],
        api_key=spark_api_key['api_key'],
        #appid、api_secret、api_key三个服务认证信息请前往开放平台控制台查看（https://console.xfyun.cn/services/bm35）
        # gpt_url="wss://spark-api.xf-yun.com/v3.5/chat",
        # Spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # v3.0环境的地址
        # Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址
        gpt_url = "ws://spark-api.xf-yun.com/v1.1/chat",  # v1.5环境的地址
        # domain="generalv3.5",
        # domain = "generalv3"    # v3.0版本
        # domain = "generalv2"    # v2.0版本
        domain = "general",    # v2.0版本
        query=inputs,
        history=history_l
    )


def generate_image(key_word,ips):
    url = f'http://{ips["generate_image"]}/generate_image'
            
    data = {
        "prompt": key_word
    }
    
    response = requests.post(url, json=data)
    log(f"generate image is done", 'EVENT')

    return response


def vqa_api(prompt,image_base64_string,file_name,history_chat_image,ips):
    print(ips)
    print(ips["chat_with_image"])
    url = f'http://{ips["chat_with_image"]}'

    #save image of user
    headers = {
        'Content-Type': 'application/json'
    }

    data = {'prompt':prompt, 'history':history_chat_image, 'image_base64_string' : image_base64_string, 'file_name' : file_name}
    
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code==200
    response_data = response.json()
    response_text = response_data.get('response', '')
    history_chat_image = response_data.get('history', '')
    log(f"chat image is done", 'EVENT')
    return response_text,history_chat_image

