import streamlit as st
import sys
import os
sys.path.append("/app") # Add root to path
from src.agent_graph import app_graph
from src.tools_audio import transcribe_audio, speak_text

st.set_page_config(page_title="Phil AI Agent 1.0.0", layout="wide")

st.title("🤖 Phil AI Agent 1.0.0")
st.caption("Nghe - Nói - Nhìn - Code - Tự Học")

# Sidebar: Inputs
with st.sidebar:
    st.header("Giác quan")
    uploaded_img = st.file_uploader("Gửi ảnh (Vision)", type=["jpg", "png"])
    uploaded_audio = st.file_uploader("Gửi giọng nói (Voice)", type=["wav", "mp3"])
    
    image_url = ""
    if uploaded_img:
        # Save temp to pass to agent
        with open("workspace/input_img.jpg", "wb") as f: f.write(uploaded_img.getbuffer())
        image_url = "workspace/input_img.jpg" # Local path logic needs refinement for real URL
        st.image(uploaded_img, caption="Đã nhận ảnh")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"])

# Input Logic
user_text = st.chat_input("Nhập yêu cầu...")
audio_text = ""

if uploaded_audio:
    with open("workspace/input_audio.wav", "wb") as f: f.write(uploaded_audio.getbuffer())
    st.toast("Đang nghe...")
    audio_text = transcribe_audio("workspace/input_audio.wav")
    st.info(f"Đã nghe thấy: {audio_text}")

final_input = user_text if user_text else audio_text

if final_input:
    # 1. Hiển thị user msg
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.write(final_input)

    # 2. Chạy Agent
    with st.spinner("Agent đang suy nghĩ & viết code..."):
        inputs = {
            "user_input_vn": final_input, 
            "image_url": image_url, 
            "iterations": 0,
            "technical_plan": "", "code": "", "exec_result": ""
        }
        final_state = app_graph.invoke(inputs)
        bot_response = final_state['final_response_vn']

    # 3. Tạo giọng nói (TTS)
    audio_path = speak_text(bot_response)

    # 4. Hiển thị Bot msg
    msg_data = {"role": "assistant", "content": bot_response}
    if audio_path:
        msg_data["audio"] = audio_path
    
    st.session_state.messages.append(msg_data)
    with st.chat_message("assistant"):
        st.write(bot_response)
        if audio_path:
            st.audio(audio_path, format="audio/wav", autoplay=True)