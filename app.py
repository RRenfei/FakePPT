import streamlit as st
import base64
import os
from openai import OpenAI

st.set_page_config(layout="wide")

def get_base64_image(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_image("image.jpg")

page_bg = f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* 固定位置输入框 */
.custom-input-box {{
    position: fixed;
    top: 200px;
    left: 80px;
    width: 300px;
    z-index: 9999;
}}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# 输入框容器
st.markdown('<div class="custom-input-box">', unsafe_allow_html=True)
text = st.text_input("请输入内容：", key="input_box")
st.markdown('</div>', unsafe_allow_html=True)

client = OpenAI(
    api_key="sk-a16435dcae464f7e90aad8e3d52445d0",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": text},
    ],
    stream=False
)

print(response.choices[0].message.content)
