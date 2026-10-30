"""
내 업무 Agent - 배포용 웹 앱 (2부 완성본)
로컬 실행 : streamlit run streamlit_app.py
배포      : GitHub 에 올린 뒤 Streamlit Community Cloud 에서 이 파일을 'Main file' 로 지정
"""
import hmac
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))
import config  # noqa: E402
from date_utils import WEEKDAYS  # noqa: E402
from features import extract_action_items, items_to_markdown, summarize_schedule  # noqa: E402
from file_loader import read_text  # noqa: E402
from finder import find_files, indexed_files  # noqa: E402
from step3_agent import Agent  # noqa: E402

st.set_page_config(page_title="내 업무 Agent", page_icon="🗂️", layout="wide")
TODAY = config.today()
MON = TODAY - timedelta(days=TODAY.weekday())
SUN = MON + timedelta(days=6)


# ------------------------------------------------------------ ① 비밀번호 화면
def check_password() -> bool:
    """APP_PASSWORD 가 설정돼 있으면 비밀번호를 맞혀야 입장"""
    if not config.APP_PASSWORD or st.session_state.get("auth"):
        return True
    st.title("🔒 내 업무 Agent")
    with st.form("login"):
        pw = st.text_input("비밀번호", type="password")
        if st.form_submit_button("입장"):
            if hmac.compare_digest(pw, config.APP_PASSWORD):
                st.session_state.auth = True
                st.rerun()
            st.error("비밀번호가 틀렸습니다.")
    return False


if not check_password():
    st.stop()                                   # 여기서 멈춤 → 아래 화면은 안 보임

# ------------------------------------------------------------ ② 기억 상자 준비
ss = st.session_state
ss.setdefault("agent", Agent(verbose=False))
ss.setdefault("history", [])                     # [(role, text, trace)]
ss.setdefault("used", 0)                         # 이번 접속에서 AI를 부른 횟수
ss.setdefault("action_items", [])


def can_use_ai() -> bool:
    if ss.used >= config.MAX_QUESTIONS:
        st.warning(f"이번 접속의 사용 한도({config.MAX_QUESTIONS}회)를 다 썼습니다. 새로고침 후 다시 이용해 주세요.")
        return False
    ss.used += 1
    return True


# ------------------------------------------------------------ ③ 사이드바
with st.sidebar:
    st.header("🗂️ 내 업무 Agent")
    st.caption(f"기준일: {TODAY} ({WEEKDAYS[TODAY.weekday()]}) · 모델: {config.MODEL}")
    st.progress(ss.used / config.MAX_QUESTIONS, text=f"AI 사용 {ss.used}/{config.MAX_QUESTIONS}회")

    st.subheader("빠른 실행")
    quick = None
    if st.button("📅 오늘 일정 요약", width="stretch"):
        quick = ("오늘 일정 요약", lambda: summarize_schedule(TODAY, TODAY))
    if st.button("📅 이번 주 일정 요약", width="stretch"):
        quick = ("이번 주 일정 요약", lambda: summarize_schedule(MON, SUN))
    if st.button("✅ 이번 주 액션아이템", width="stretch"):
        def _actions():
            ss.action_items = extract_action_items(MON, SUN)
            return items_to_markdown(ss.action_items)
        quick = ("이번 주 액션아이템", _actions)

    st.divider()
    if st.button("🧹 대화 초기화", width="stretch"):
        for k in ("agent", "history", "action_items"):
            ss.pop(k, None)
        st.rerun()
    st.caption("예시 질문\n- 지난주 수요일에 무슨 일정 있었지?\n- 9월 채널별 ROAS 비교해줘\n- 이번 주 박민수 할 일만 보여줘")

# ------------------------------------------------------------ ④ 상단 숫자 카드
def count_schedule(d) -> int:
    """일정 파일 표에서 '| 09:30 |' 처럼 시간으로 시작하는 줄 수 = 일정 건수"""
    files = find_files(d, d, "일정")
    if not files:
        return 0
    return sum(line.startswith("| ") and line[2:3].isdigit() for line in read_text(files[0].path).splitlines())


all_files = indexed_files()
c1, c2, c3, c4 = st.columns(4)
c1.metric("오늘 일정", f"{count_schedule(TODAY)}건")
c2.metric("이번 주 회의", f"{len(find_files(MON, SUN, '회의록'))}건")
c3.metric("전체 문서", f"{len(all_files)}개")
c4.metric("미분류 문서", f"{sum(f.category == '미분류' for f in all_files)}개")

tab_chat, tab_sched, tab_action, tab_docs = st.tabs(["💬 채팅", "📅 일정", "✅ 액션아이템", "📁 문서 보기"])

# ------------------------------------------------------------ ⑤ 채팅 탭
with tab_chat:
    for role, text, trace in ss.history:
        with st.chat_message(role):
            if trace:
                with st.expander("🔧 Agent가 사용한 도구"):
                    st.code("\n".join(trace))
            st.markdown(text)

    question = st.chat_input("예) 어제 고객사 미팅에서 정한 가격이 얼마야?")
    if (quick or question) and can_use_ai():
        title = quick[0] if quick else question
        with st.chat_message("user"):
            st.markdown(title)
        with st.chat_message("assistant"), st.spinner("문서를 읽는 중..."):
            if quick:
                answer, trace = quick[1](), []
            else:
                answer = ss.agent.ask(question)
                trace = ss.agent.trace
            if trace:
                with st.expander("🔧 Agent가 사용한 도구"):
                    st.code("\n".join(trace))
            st.markdown(answer)
        ss.history += [("user", title, []), ("assistant", answer, trace)]

# ------------------------------------------------------------ ⑥ 일정 탭 (AI 없이 파일 그대로 + AI 요약)
with tab_sched:
    day = st.date_input("날짜", TODAY)
    files = find_files(day, day, "일정")
    if files:
        st.markdown(read_text(files[0].path))
        if st.button("🤖 이 날 일정 AI 요약") and can_use_ai():
            with st.spinner("요약 중..."):
                st.markdown(summarize_schedule(day, day))
    else:
        st.info(f"{day} 일정 파일이 없습니다.")

# ------------------------------------------------------------ ⑦ 액션아이템 탭
with tab_action:
    col_a, col_b = st.columns(2)
    start = col_a.date_input("시작일", MON, key="a_start")
    end = col_b.date_input("종료일", SUN, key="a_end")
    who = st.text_input("담당자 (비우면 전체)")
    if st.button("✅ 액션아이템 추출") and can_use_ai():
        with st.spinner("회의록을 읽는 중..."):
            ss.action_items = extract_action_items(start, end, who or None)
    if ss.action_items:
        df = pd.DataFrame(ss.action_items)
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("⬇️ CSV 다운로드", df.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"액션아이템_{start}_{end}.csv", mime="text/csv")

# ------------------------------------------------------------ ⑧ 문서 보기 탭
with tab_docs:
    category = st.radio("종류", ["전체", "일정", "회의록", "보고서", "미분류"], horizontal=True)
    shown = [f for f in all_files if category == "전체" or f.category == category]
    picked = st.selectbox("문서 선택", shown, format_func=lambda f: f"[{f.category}] {f.name}")
    if picked:
        text = read_text(picked.path)
        if picked.path.suffix == ".md":
            st.markdown(text)
        else:
            st.text(text)
