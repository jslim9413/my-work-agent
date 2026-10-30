"""03. Streamlit의 핵심: 버튼을 누를 때마다 '위에서부터 다시 실행'된다
실행: streamlit run basics/03_rerun_state.py"""
import streamlit as st

st.title("🔁 다시 실행(rerun)과 기억(session_state)")

# ❌ 일반 변수: 버튼을 누를 때마다 파일 전체가 다시 실행되어 0으로 돌아감
count = 0
if st.button("일반 변수 +1"):
    count += 1
st.write("일반 변수:", count, "← 아무리 눌러도 1 이상 안 올라감")

# ✅ session_state: 다시 실행되어도 값이 남아 있는 '기억 상자'
if "count" not in st.session_state:
    st.session_state.count = 0
if st.button("session_state +1"):
    st.session_state.count += 1
st.write("session_state:", st.session_state.count, "← 계속 올라감")
