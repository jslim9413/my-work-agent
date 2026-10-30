"""07. 채팅 화면 + 진짜 AI 연결 (1부에서 만든 llm.py 재사용)
실행: streamlit run basics/07_llm_chat.py"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "solution"))
import llm  # noqa: E402

st.title("🤖 AI 채팅")
if "history" not in st.session_state:
    st.session_state.history = []

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

if q := st.chat_input("무엇이든 물어보세요"):
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"), st.spinner("생각하는 중..."):   # 기다리는 동안 빙글빙글
        answer = llm.ask("너는 친절한 업무 비서다. 한국어로 짧게 답한다.", q)
        st.markdown(answer)
    st.session_state.history += [("user", q), ("assistant", answer)]
