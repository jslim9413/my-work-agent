"""01. 화면에 글자 띄우기
실행: streamlit run basics/01_hello.py"""
import streamlit as st

st.title("🌱 안녕하세요, Streamlit!")          # 큰 제목
st.header("파이썬만으로 웹 화면 만들기")          # 중간 제목
st.write("st.write 는 글자, 숫자, 표, 무엇이든 알아서 보여줍니다.")
st.markdown("**굵게**, *기울임*, `코드`, [링크](https://streamlit.io) 처럼 마크다운도 됩니다.")
st.write(1 + 2, "← 계산 결과도 그대로")
st.info("ℹ️ 안내 상자")
st.success("✅ 성공 상자")
st.warning("⚠️ 경고 상자")
