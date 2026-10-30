"""06. 채팅 화면 뼈대 (AI 없이 따라 말하기)
실행: streamlit run basics/06_chat.py"""
import streamlit as st

st.title("💬 채팅 화면")
if "history" not in st.session_state:          # 대화 기록 = 기억 상자에 저장
    st.session_state.history = []

for role, text in st.session_state.history:    # 지금까지 대화 다시 그리기
    with st.chat_message(role):
        st.markdown(text)

if q := st.chat_input("메시지를 입력하세요"):    # 화면 맨 아래 입력창
    #st.session_state.history.append(("user", q))
    #st.session_state.history.append(("assistant", f"따라 말하기: {q}"))
    history = []
    history.append(("user", q))
    st.rerun()                                  # 바로 다시 그리기
