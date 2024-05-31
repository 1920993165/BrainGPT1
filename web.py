import streamlit as st
from streamlit_chat import message
from st_multimodal_chatinput import multimodal_chatinput
from Utils.brain_main import brain_agent

__version__ = "1"

#下面3个参数实际并没有与braingpt关联，有需要可以自己修改一下
max_length=4096
top_p=0.8
temperature=0.95
#端口号
ips={
        "file_system":"0.0.0.0:5999",
        "braingpt":"0.0.0.0:6000",
        "generalgpt":"0.0.0.0:6001",
        "generate_image":"0.0.0.0:6002",
        "chat_with_image":"0.0.0.0:6003"
    }
#sparkapi需要的参数,https://console.xfyun.cn/services/bm35获取
spark_api_key={
        'appid':"",
        'api_secret':"",
        'api_key':""
    }


def clear_chat_history():
    del st.session_state.past[:]
    del st.session_state.generated[:]

def chat_with_braingpt(chat_input_dict):
    image=chat_input_dict['images']
    inputs=chat_input_dict['text']    
    

    inputs,output,st.session_state.history_braingpt,st.session_state.history_general_problem,st.session_state.history_chat_image,st.session_state.image_base64_string,st.session_state.user_start_time=brain_agent(inputs
                                                                                                                                                                        ,image
                                                                                                                                                                        ,st.session_state.history_braingpt
                                                                                                                                                                        ,st.session_state.history_general_problem
                                                                                                                                                                        ,st.session_state.history_chat_image
                                                                                                                                                                        ,st.session_state.image_base64_string
                                                                                                                                                                        ,max_length
                                                                                                                                                                        ,top_p
                                                                                                                                                                        ,temperature
                                                                                                                                                                        ,st.session_state.user_start_time
                                                                                                                                                                        ,ips
                                                                                                                                                                        ,spark_api_key)
    st.session_state.past.append({'type': 'normal', 'data': inputs})
    st.session_state.generated.append({'type': 'normal', 'data': output})

    return True

st.set_page_config(
    page_title=f"Braingpt v{__version__}",
    page_icon="🤖",
)
st.title(f"Braingpt v{__version__}")

top = st.container()
bottom = st.container()

chat_input_dict = None
chat_input_human_message = None

st.session_state.user_start_time=None
st.session_state.image_base64_string=''
st.session_state.history_braingpt=[]
st.session_state.history_general_problem=[]
st.session_state.history_chat_image=[]
st.session_state.setdefault(
    'past', 
    []
)
st.session_state.setdefault(
    'generated', 
    []
)

with top:
    if chat_input_human_message:
        chat_placeholder = st.empty()
        with chat_placeholder.container():    
            for i in range(len(st.session_state['generated'])):                
                message(
                    st.session_state['past'][i]['data'], 
                    key=f"{i}_user", 
                    is_user=True,
                    allow_html=True,
                    is_table=True if st.session_state['generated'][i]['type']=='table' else False
                )
                message(
                    st.session_state['generated'][i]['data'], 
                    key=f"{i}", 
                    allow_html=True,
                    is_table=True if st.session_state['generated'][i]['type']=='table' else False
                )
            
            st.button("清空对话", on_click=clear_chat_history)

        chat_input_human_message = None

with bottom:
    chat_input_dict = multimodal_chatinput(text_color="black")
    if chat_input_dict:
        chat_input_human_message=chat_with_braingpt(chat_input_dict)


