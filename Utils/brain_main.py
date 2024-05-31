from PIL import Image
from io import BytesIO
import re
import base64
from Functions.weather.weather import wea_run
from Utils.tools import log
from Utils.tools import get_cur_time,get_time,get_bilibili_code,adapt_image_pix
from Utils.apis import braingpt,general,general_spark,generate_image,vqa_api

def brain_agent(inputs
                ,images
                ,history_braingpt
                ,history_general_problem
                ,history_chat_image
                ,image_base64_string
                ,max_length
                ,top_p
                ,temperature
                ,user_start_time
                ,ips
                ,spark_api_key):
    
    if user_start_time is None:
        user_start_time=get_cur_time('%Y年%m月%d日%H时%M分%S秒')
    user_time=get_cur_time('%Y年%m月%d日%H时%M分%S秒')


    if len(images)>0:
        image_base64_string=images[0]
        if image_base64_string.startswith("data:image"):
            _, image_base64_string = image_base64_string.split(",", 1)

        image_data = base64.b64decode(image_base64_string)
        image_stream = BytesIO(image_data)
        image = Image.open(image_stream)
        im_user=image
        if len(inputs)>20:
            file_name=user_time+inputs[:20]+'.png'
        else:
            file_name=user_time+inputs+'.png'
        local_image_path = "Datas/user_img/"+file_name
        image.save(local_image_path)
        print(f"用户图片已保存到{local_image_path}")

        prompt=inputs
        inputs='<|Input_image|>'+inputs


    brain_status_code,brain_data,history_braingpt=braingpt(inputs,history_braingpt,ips)

    if brain_status_code == 200:
        output=brain_data

        if history_braingpt[-1]['metadata']=='<|Get_time|>':
            match = re.search(r"key word='(.*?)'", history_braingpt[-1]['content'])
            assert match
            key_word=match.group(1)
            time_info=get_time(key_word)
            brain_status_code,response_text,history_braingpt=braingpt(time_info,history_braingpt, ips, role='observation')
            assert brain_status_code==200
            output=response_text
            log(f"time请求成功！", 'EVENT')
        
        if history_braingpt[-1]['metadata']=='<|Get_weather|>':
            match = re.search(r"city='(.*?)'", history_braingpt[-1]['content'])
            assert match
            city = match.group(1)
            match = re.search(r"time='(.*?)'", history_braingpt[-1]['content'])
            assert match
            time = match.group(1)
            wea_res=wea_run(city,time)
            brain_status_code,response_text,history_braingpt=braingpt(wea_res,history_braingpt, ips, role='observation')
            assert brain_status_code==200
            output=response_text
            log(f"weather请求成功！", 'EVENT')

        if history_braingpt[-1]['metadata']=='<|General_problem|>':
            # _,general_status_code,output,history_general_problem=general(inputs,history_general_problem)
            # assert general_status_code == 200
            # log(f"general请求成功！", 'EVENT')

            output,history_general_problem=general_spark(inputs,history_general_problem,spark_api_key)
            log(f"general—spark请求成功！", 'EVENT')

        
        if history_braingpt[-1]['metadata']=='<|Search_web|>':
            output,history_general_problem=general_spark(inputs,history_general_problem,ips)
            log(f"使用general—spark上网请求成功！", 'EVENT')
        
            
        if history_braingpt[-1]['metadata']=='<|Generate_image|>':
            match = re.search(r"key word='(.*?)'", history_braingpt[-1]['content'])
            assert match
            prompt_img= match.group(1)
            response=generate_image(prompt_img,ips)
            assert response.status_code == 200
            log(f"图像请求成功！", 'EVENT')

            brain_status_code,response_first,history_braingpt=braingpt('ok',history_braingpt,ips, role='observation')
            log(f"response_first : {response_first}", 'INFO')

            if len(prompt_img)>20:
                prompt_img=user_time+prompt_img[:20]+'.jpg'
            else:
                prompt_img=user_time+prompt_img+'.jpg'
            
            path=f'Datas/assistant_img/{prompt_img}'
            im_agi = Image.open(BytesIO(response.content))
            if im_agi is not None:
                im_agi.save(path)
                print(f'模型生成图像保存在{path}')
            
            new_width , new_height = adapt_image_pix(im_agi)
            output=f'{response_first}\n<img width="{new_width}px" height="{new_height}px" src="http://{ips["file_system"]}/assistant_img/{prompt_img}" alt="">'

        if history_braingpt[-1]['metadata']=='<|play_media|>':
            match1 = re.search(r"key word='(.*?)'", history_braingpt[-1]['content'])
            assert match1
            content = match1.group(1)
            html_code=get_bilibili_code(content)
            brain_status_code,response_first,history_braingpt=braingpt('ok',history_braingpt,ips, role='observation')
            output=f'{response_first}\n{html_code}'

        if history_braingpt[-1]['metadata']=='<|Chat_image|>':
            if im_user is None:
                output='抱歉，你好像没有输入图片呢'
            else:
                output,history_chat_image=vqa_api(prompt,image_base64_string,file_name,history_chat_image,ips)

    if inputs.startswith('<|Input_image|>'):
        inputs=inputs.replace('<|Input_image|>','')
 
        new_width , new_height = adapt_image_pix(im_user)
        # 构建HTML标签
        inputs += f'\n<img width="{new_width}px" height="{new_height}px" src="http://{ips["file_system"]}/user_img/{file_name}" alt="">'


    return inputs,output,history_braingpt,history_general_problem,history_chat_image,image_base64_string,user_start_time
