import streamlit as st
import base64

from openai import OpenAI
from fpdf import FPDF

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

# ===== 输入框 =====
st.markdown('<div class="custom-input-box">', unsafe_allow_html=True)
text = st.text_input("请输入内容：", key="input_box")
st.markdown('</div>', unsafe_allow_html=True)

# ===== 按钮触发 LLM =====
if st.button("生成回复"):
    if not text.strip():
        st.warning("请输入内容再生成。")
    else:
        client = OpenAI(
            api_key="sk-a16435dcae464f7e90aad8e3d52445d0",
            base_url="https://api.deepseek.com"
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": text}],
            stream=False
        )

        output_text = response.choices[0].message.content

        # ===== 在页面渲染 markdown =====
        st.markdown("### 模型返回结果")
        st.markdown(output_text)

        # ===== 将内容生成 PDF  =====
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('Arial', '', fname='')
        pdf.set_font("Arial", size=12)

        # 按行加入 PDF（避免乱码）
        for line in output_text.split("\n"):
            pdf.multi_cell(0, 10, line)

        pdf_path = "result.pdf"
        pdf.output(pdf_path)

        # ===== 提供下载按钮 =====
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="下载 PDF",
                data=f,
                file_name="result.pdf",
                mime="application/pdf"
            )
