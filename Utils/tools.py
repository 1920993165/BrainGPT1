import pytz
import csv
import json
from PIL import Image
import os
import re
import requests
import datetime, sys
from rich.console import Console
console = Console()

def log(event:str, type:str):
	back_frame = sys._getframe().f_back
	if back_frame is not None:
		back_filename = os.path.basename(back_frame.f_code.co_filename)
		back_funcname = back_frame.f_code.co_name
		back_lineno = back_frame.f_lineno
	else:
		back_filename = "Unknown"
		back_funcname = "Unknown"
		back_lineno = "Unknown"
	now = datetime.datetime.now()
	time = now.strftime("%Y-%m-%d %H:%M:%S")
	logger = f"[{time}] <{back_filename}:{back_lineno}> <{back_funcname}()> {type}: {event}"
	if type.lower() == "info":
		style = "green"
	elif type.lower() == "error":
		style = "red"
	elif type.lower() == "critical":
		style = "bold red"
	elif type.lower() == "event":
		style = "#ffab70"
	else:
		style = ""
	console.print(logger, style = style)
	with open('latest.log','a', encoding='utf-8') as f:
		f.write(f'{logger}\n')


def deal_lang_history(response_data,inputs):
    language_data = response_data.get('response', '')
    temp_his_l = response_data.get('history', '')
    #让语言模型的历史记录里没有记录到网页信息，网页信息比较多
    if len(temp_his_l)==2:
        history_l=[ {'role': 'user', 'content': inputs}, {'role': 'assistant', 'metadata': '', 'content': language_data}]
    else:
        history_l=temp_his_l[:-2]+[ {'role': 'user', 'content': inputs}, {'role': 'assistant', 'metadata': '', 'content': language_data}]
    return language_data,history_l

def get_cur_time(format_t='%Y_%m_%d__%H_%M_%S'):
    from datetime import datetime
    # 获得当前时间
    beijing_timezone = pytz.timezone('Asia/Shanghai')                
    # 获取当前时间
    current_utc_time = datetime.utcnow()                
    # 将当前时间转换为北京时间
    current_beijing_time = current_utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_timezone)
    # 格式化输出北京时间
    return current_beijing_time.strftime(format_t)

def get_time(brain_str):
    if brain_str=='几点':
        formatted_time = get_cur_time('%H:%M')                 
    elif brain_str=='几号':
        formatted_time = get_cur_time('%Y:%m:%d')       
    else:
        formatted_time = get_cur_time('%Y:%m:%d:%H:%M')       
    return formatted_time

def get_cid(bid):
    headers = {
            "referer": "https://search.bilibili.com/all?keyword=%E4%B8%BB%E6%92%AD%E8%AF%B4%E8%81%94%E6%92%AD&from_source=webtop_search&spm_id_from=333.1007&search_source=5&page=4&o=90",
            "origin": "https://search.bilibili.com",
            'accept-language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept-Encoding': 'gzip, deflate, br',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'accept':'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
   
    data=requests.get(f'https://api.bilibili.com/x/player/pagelist?bvid={bid}',headers=headers)#

    try:
        json_data = data.json()
    except requests.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    return json_data['data'][0]['cid']

def get_bilibili_code(content):

    # 目标网址
    url = f"https://search.bilibili.com/all?keyword={content}"
    headers = {
            "referer": "https://search.bilibili.com/all?keyword=%E4%B8%BB%E6%92%AD%E8%AF%B4%E8%81%94%E6%92%AD&from_source=webtop_search&spm_id_from=333.1007&search_source=5&page=4&o=90",
            "origin": "https://search.bilibili.com",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept-Encoding': 'gzip, deflate, br'
        }
    # 发送GET请求
    response = requests.get(url,headers=headers)#.content.decode('utf-8')

    # 检查请求是否成功
    assert response.status_code == 200
    # 获取网页源码
    html_content = response.text

    # 编译正则表达式
    pattern = re.compile(r'//www.bilibili.com/video/(\w+)/')

    # 搜索所有匹配项
    matches = pattern.findall(html_content)
    
    #去重
    unique_matches = []
    for item in matches:
        if item not in unique_matches:
            unique_matches.append(item)
    # print(unique_matches)

    unique_matches
    bid=unique_matches[0]
    cid=get_cid(bid)
    return f'<iframe width="500" height="360" src="//player.bilibili.com/player.html?isOutside=true&bvid={bid}&cid={cid}&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>'


    

def parse_text(text):
    """copy from https://github.com/GaiZhenbiao/ChuanhuChatGPT/"""
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>"+line
    text = "".join(lines)
    return text

def adapt_image_pix(img):
    # 假设 im_user 是通过 PIL库打开的图片对象
    image_width, image_height = img.size

    # 设置最大宽度和最大高度
    max_width = 450
    max_height = 500

    # 初始化新的宽度和高度
    new_width = image_width
    new_height = image_height

    # 检查是否需要缩放宽度
    if image_width > max_width:
        scale_width = max_width / image_width
        new_width = max_width
        new_height = int(image_height * scale_width)

    # 使用新的宽度检查是否需要进一步缩放高度
    if new_height > max_height:
        scale_height = max_height / new_height
        new_height = max_height
        # 如果高度缩放比例更小，则应用这个比例到宽度
        new_width = int(new_width * scale_height)
    return new_width , new_height