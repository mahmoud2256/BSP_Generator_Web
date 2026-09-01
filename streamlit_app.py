import streamlit as st
import tempfile
import os
import base64
from datetime import datetime

from main import process_pdf
from logger_engine import get_log_path

st.set_page_config(
    page_title="BSP Generator - Kanoo Travel",
    page_icon="✈️",
    layout="centered",
)


def _img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------- خلفية بصورة (شعار IATA كـ watermark فاتح فوق خلفية غامقة) ----------
_bg_path = "assets/background.png"
_bg_css = ""
if os.path.isfile(_bg_path):
    _bg_b64 = _img_to_base64(_bg_path)
    _bg_css = f"""
    .stApp {{
        background-color: #0e1117;
        background-image:
            linear-gradient(rgba(14,17,23,0.88), rgba(14,17,23,0.88)),
            url("data:image/png;base64,{_bg_b64}");
        background-repeat: no-repeat;
        background-position: center 40%;
        background-size: 55% auto;
        background-attachment: fixed;
    }}
    """

st.markdown(
    f"""
    <style>
    {_bg_css if _bg_css else ".stApp { background-color: #0e1117; }"}
    .main-title {{ color: #ffffff; font-size: 28px; font-weight: 700; }}
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 4])
with col1:
    if os.path.isfile("assets/logo.png"):
        st.image("assets/logo.png", width=90)
with col2:
    st.markdown('<div class="main-title">BSP Generator – Kanoo Travel</div>', unsafe_allow_html=True)

st.write("ارفع ملف BSP PDF وحوّله لإكسيل جاهز للاستيراد.")

uploaded_pdf = st.file_uploader("اختر ملف BSP PDF", type=["pdf"])

if uploaded_pdf is not None:
    if st.button("🔄 Convert to Excel (EGP)", use_container_width=True):
        with st.spinner("جاري تحويل الملف..."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                pdf_path = os.path.join(tmp_dir, uploaded_pdf.name)
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                output_path = process_pdf(pdf_path, tmp_dir)

                if output_path and os.path.isfile(output_path):
                    with open(output_path, "rb") as f:
                        excel_bytes = f.read()

                    st.success("✅ تم التحويل بنجاح")
                    st.download_button(
                        label="⬇️ تحميل ملف الإكسل",
                        data=excel_bytes,
                        file_name=f"BSP_OUTPUT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                else:
                    st.error("❌ فشل التحويل - راجع سجل الأخطاء بالأسفل")

with st.expander("📄 عرض سجل الأخطاء (Log)"):
    log_path = get_log_path()
    if os.path.isfile(log_path):
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        st.text("".join(lines[-60:]) if lines else "اللوج فاضي.")
    else:
        st.text("لسه مفيش لوج.")
