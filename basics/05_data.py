"""05. 표 보여주고 파일로 내려받기
실행: streamlit run basics/05_data.py"""
import pandas as pd
import streamlit as st

st.title("📊 데이터 다루기")
df = pd.read_csv("업무폴더/보고서/2026-10_채널별일일성과.csv", encoding="utf-8-sig")
st.dataframe(df, width="stretch")           # 정렬·검색되는 표

channel = st.selectbox("채널", df["채널"].unique())
chart = df[df["채널"] == channel].set_index("날짜")["클릭"]
st.line_chart(chart)                                  # 선 그래프 한 줄로

st.download_button("⬇️ CSV 내려받기", df.to_csv(index=False).encode("utf-8-sig"),
                   file_name="채널성과.csv", mime="text/csv")
