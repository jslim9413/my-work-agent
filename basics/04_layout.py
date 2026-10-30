"""04. 화면 배치: 사이드바, 칸 나누기, 탭, 접기
실행: streamlit run basics/04_layout.py"""
import streamlit as st

st.set_page_config(page_title="레이아웃 예제", page_icon="🧱", layout="wide")  # 맨 위에 한 번

with st.sidebar:                                 # 왼쪽 사이드바
    st.header("메뉴")
    st.button("📅 오늘 일정")

col1, col2, col3 = st.columns(3)                 # 가로로 3칸
col1.metric("오늘 일정", "3건")
col2.metric("이번 주 회의", "3건", "+1")
col3.metric("미분류 파일", "1개", "-2", delta_color="inverse")

tab1, tab2 = st.tabs(["💬 채팅", "📁 문서"])     # 탭
with tab1:
    st.write("채팅 화면 자리")
with tab2:
    with st.expander("파일 목록 펼치기"):         # 접었다 펴기
        st.write("2026-10-30_일정.md")
