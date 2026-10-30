"""
4교시 완성본: 웹 화면으로 쓰는 업무 Agent
실행: streamlit run solution/step4_app.py
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

import config  # noqa: E402
from date_utils import WEEKDAYS  # noqa: E402
from features import extract_action_items, items_to_markdown, summarize_schedule  # noqa: E402
from finder import indexed_files  # noqa: E402
from step3_agent import Agent  # noqa: E402

st.set_page_config(page_title="내 업무 Agent", page_icon="🗂️", layout="wide")
today = config.today()
mon = today - timedelta(days=today.weekday())

if "agent" not in st.session_state:
    st.session_state.agent = Agent(verbose=False)
    st.session_state.history = []

# ------------------------------------------------------------------ 사이드바
with st.sidebar:
    st.header("🗂️ 내 업무 Agent")
    st.caption(f"오늘: {today} ({WEEKDAYS[today.weekday()]}) · 모델: {config.MODEL}")

    st.subheader("빠른 실행")
    if st.button("📅 오늘 일정 요약", width="stretch"):
        st.session_state.quick = ("오늘 일정 요약", lambda: summarize_schedule(today, today))
    if st.button("📅 이번 주 일정 요약", width="stretch"):
        st.session_state.quick = ("이번 주 일정 요약", lambda: summarize_schedule(mon, mon + timedelta(days=6)))
    if st.button("✅ 이번 주 액션아이템", width="stretch"):
        def _run():
            items = extract_action_items(mon, mon + timedelta(days=6))
            st.session_state.action_items = items
            return items_to_markdown(items)
        st.session_state.quick = ("이번 주 액션아이템", _run)

    with st.expander("📁 업무폴더 파일 목록"):
        for f in indexed_files():
            st.write(f"`{f.category}` {f.name}")

    if st.button("🧹 대화 초기화"):
        st.session_state.clear()
        st.rerun()

# ------------------------------------------------------------------ 본문
st.title("무엇을 도와드릴까요?")

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

quick = st.session_state.pop("quick", None)
question = st.chat_input("예) 지난주 수요일에 무슨 일정 있었지? / 9월 채널별 ROAS 비교해줘")

if quick:
    title, fn = quick
    with st.chat_message("user"):
        st.markdown(title)
    with st.chat_message("assistant"), st.spinner("문서를 읽는 중..."):
        answer = fn()
        st.markdown(answer)
    st.session_state.history += [("user", title), ("assistant", answer)]
elif question:
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"), st.spinner("생각하는 중..."):
        agent = st.session_state.agent
        answer = agent.ask(question)
        if agent.trace:
            with st.expander("🔧 Agent가 사용한 도구"):
                st.code("\n".join(agent.trace))
        st.markdown(answer)
    st.session_state.history += [("user", question), ("assistant", answer)]

if st.session_state.get("action_items"):
    import pandas as pd
    df = pd.DataFrame(st.session_state["action_items"])
    st.download_button("⬇️ 액션아이템 CSV 다운로드", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"액션아이템_{today}.csv", mime="text/csv")
