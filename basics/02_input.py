"""02. 입력 받고 버튼 누르기
실행: streamlit run basics/02_input.py"""
import streamlit as st

st.title("✍️ 입력 위젯")
name = st.text_input("이름을 입력하세요")                 # 글자 입력칸
team = st.selectbox("소속 팀", ["마케팅팀", "영업팀", "개발팀"])  # 선택 상자
day = st.date_input("날짜 선택")                          # 달력
hours = st.slider("오늘 회의 시간(시간)", 0, 8, 2)         # 슬라이더

if st.button("인사하기"):                                 # 버튼을 누른 순간만 True
    st.write(f"{team} {name}님, {day} 회의가 {hours}시간이네요!")
    st.balloons()
