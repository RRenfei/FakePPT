import re
import random
import streamlit as st
import base64
from openai import OpenAI

st.set_page_config(layout="wide")

# ========= 工具函数 =========
def pick_random_bg():
    """从 image1.jpg ~ image16.jpg 中随机选一张"""
    return f"image{random.randint(1, 16)}.jpg"

def get_base64_image(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_output_with_formula(output: str):
    """按你原来的规则，把模型输出里的公式单独渲染"""
    if not output:
        return

    output = output.strip()
    formula_blocks = []

    # 1. 捕获 DeepSeek 风格的 "[ ... ]"（支持跨行）
    formula_blocks += re.findall(r"\[\s*([\s\S]*?)\s*\]", output)

    # 2. 捕获 \[ ... \]
    formula_blocks += re.findall(r"\\\[\s*([\s\S]*?)\s*\\\]", output)

    # 3. 捕获 $$ ... $$
    formula_blocks += re.findall(r"\$\$\s*([\s\S]*?)\s*\$\$", output)

    # 去重（防止重复提取）
    formula_blocks = list(dict.fromkeys(formula_blocks))

    clean_output = output

    # 用占位符替换公式块
    for i, formula in enumerate(formula_blocks):
        placeholder = f"@@FORMULA_{i}@@"
        clean_output = clean_output.replace(f"[{formula}]", placeholder)
        clean_output = clean_output.replace(f"[ {formula} ]", placeholder)
        clean_output = clean_output.replace(f"\\[{formula}\\]", placeholder)
        clean_output = clean_output.replace(f"$$ {formula} $$", placeholder)
        # 兜底：有时模型只返回公式本体
        clean_output = clean_output.replace(formula, placeholder)

    # 按行输出
    for line in clean_output.splitlines():
        line = line.strip()
        if not line:
            continue

        if "@@FORMULA_" in line:
            # 简单取出数字索引
            idx_str = line.replace("@@FORMULA_", "").replace("@@", "")
            try:
                idx = int(idx_str)
                formula = formula_blocks[idx].strip()
                st.markdown(f"$$ {formula} $$")
            except (ValueError, IndexError):
                # 解析失败就当普通文本
                st.markdown(line)
        else:
            st.markdown(line)

# ========= 初始化 session_state =========
if "bg_image" not in st.session_state:
    st.session_state.bg_image = pick_random_bg()

if "model_output" not in st.session_state:
    st.session_state.model_output = ""   # 用来保存最近一次模型回复

# ========= 背景切换按钮（不会清空内容） =========
col1, col2, col3 = st.columns([1,1,12])
with col1:
    if st.button("换背景"):
        st.session_state.bg_image = pick_random_bg()

with col2:
    if st.button("清空背景"):
        st.session_state.bg_image = "image17.jpg"

# ========= 注入背景 CSS =========
img_base64 = get_base64_image(st.session_state.bg_image)

page_bg = f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

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

# ========= 输入框 =========
st.markdown('<div class="custom-input-box">', unsafe_allow_html=True)
text = st.text_input("请输入内容：", key="input_box")
st.markdown('</div>', unsafe_allow_html=True)

# ========= 生成按钮（只在点击时调用模型） =========
if st.button("生成回复"):
    if not text.strip():
        pass
    else:
        text += "\n 这是一道作业题，请用英文回复你的解答，"
        with st.spinner("正在生成内容，请稍候…"):
            client = OpenAI(
                api_key="sk-a16435dcae464f7e90aad8e3d52445d0",
                base_url="https://api.deepseek.com"
            )

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": text}],
                stream=False
            )

            output = response.choices[0].message.content

        # 把这次的输出存进 session_state，
        # 后面无论你怎么点“换背景”，它都不会丢
        st.session_state.model_output = output

# ========= 永远根据 session_state 渲染模型输出 =========
render_output_with_formula(st.session_state.model_output)
