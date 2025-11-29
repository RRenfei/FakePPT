import re
import streamlit as st
import base64
from openai import OpenAI

st.set_page_config(layout="wide")

# ===== 背景处理函数 =====
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

# ===== 输入框 =====
st.markdown('<div class="custom-input-box">', unsafe_allow_html=True)
text = st.text_input("请输入内容：", key="input_box")
st.markdown('</div>', unsafe_allow_html=True)

# ===== 生成按钮 =====
if st.button("生成回复"):
    if not text.strip():
        st.warning("请输入内容再生成。")
    else:
        with st.spinner("正在生成内容，请稍候…"):

            client = OpenAI(
                api_key="sk-a16435dcae464f7e90aad8e3d52445d0",   # 别再用明文泄露那个旧 key 了，记得在后台重置
                base_url="https://api.deepseek.com"
            )

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": text}],
                stream=False
            )

            output = response.choices[0].message.content

        st.markdown("### 模型返回结果")

        output = output.strip()

        # 收集所有公式块
        formula_blocks = []

        # 1. 捕获 DeepSeek 风格的 "[ ... ]"（支持跨行）
        formula_blocks += re.findall(r"\[\s*([\s\S]*?)\s*\]", output)

        # 2. 捕获 \[ ... \]
        formula_blocks += re.findall(r"\\\[\s*([\s\S]*?)\s*\\\]", output)

        # 3. 捕获 $$ ... $$
        formula_blocks += re.findall(r"\$\$\s*([\s\S]*?)\s*\$\$", output)

        # 去重（防止重复提取）
        formula_blocks = list(dict.fromkeys(formula_blocks))

        # ==== 逐段渲染 ====
        clean_output = output

        # 替换公式块为占位符
        for i, formula in enumerate(formula_blocks):
            placeholder = f"@@FORMULA_{i}@@"
            clean_output = clean_output.replace(f"[{formula}]", placeholder)
            clean_output = clean_output.replace(f"[ {formula} ]", placeholder)
            clean_output = clean_output.replace(f"\\[{formula}\\]", placeholder)
            clean_output = clean_output.replace(f"$$ {formula} $$", placeholder)
            clean_output = clean_output.replace(formula, placeholder)  # 最后兜底

        # 把普通文字按行输出
        for line in clean_output.splitlines():
            line = line.strip()
            if not line:
                continue

            # 如果是占位符，则渲染公式
            if "@@FORMULA_" in line:
                idx = int(line.replace("@@", "").replace("FORMULA_", "").replace("@@", ""))
                formula = formula_blocks[idx].strip()
                st.markdown(f"$$ {formula} $$")
            else:
                st.markdown(line)
