"""내 업무 Agent 웹 화면 (2부 뼈대). 1부의 기능은 solution/ 폴더의 모듈을 가져다 씀"""
import re
import sys
from pathlib import Path

import streamlit as st

# solution/ 폴더를 import 경로에 추가 (그 안의 config, finder 등을 바로 쓰기 위해)
sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))

import config  # noqa: E402
from date_utils import WEEKDAYS, parse_date_expression  # noqa: E402
from features import extract_action_items, items_to_markdown, summarize_schedule  # noqa: E402
from finder import find_files, indexed_files  # noqa: E402
from step3_agent import Agent  # noqa: E402
from my_guard import can_use_ai, check_password, show_usage  # noqa: E402
from my_tabs import show_action_tab, show_docs_tab  # noqa: E402

TIME_ROW = re.compile(r"^\|?\s*\d{1,2}:\d{2}")  # 시간으로 시작하는 줄 (일정 표의 행)


def count_schedule_rows(files) -> int:
    """일정 파일들에서 시간으로 시작하는 줄 수를 셈"""
    count = 0
    for f in files:
        text = f.path.read_text(encoding="utf-8", errors="ignore")
        count += sum(1 for line in text.splitlines() if TIME_ROW.match(line))
    return count


def get_agent() -> Agent:
    """Agent 를 세션당 한 번만 만들어 session_state 에 보관하고 계속 재사용"""
    if "agent" not in st.session_state:
        st.session_state.agent = Agent(verbose=False)
    return st.session_state.agent


def show_message(msg: dict):
    """대화 한 줄을 그림. Agent 답변이면 도구 사용 기록을 접을 수 있는 영역에 먼저 보여줌"""
    with st.chat_message(msg["role"]):
        if msg["trace"]:
            with st.expander("🔧 Agent가 사용한 도구"):
                st.text("\n".join(msg["trace"]))
        st.markdown(msg["content"])


def run_quick(label: str, func):
    """빠른 실행: 질문 말풍선을 넣고 features 함수를 바로 호출해 결과를 채팅 기록에 추가"""
    if not can_use_ai():
        return
    st.session_state.chat_log.append({"role": "user", "content": label, "trace": []})
    with st.spinner("문서를 읽는 중..."):
        try:
            answer = func()
        except Exception as e:  # noqa: BLE001  API 오류 등을 화면에 보여주기 위해
            answer = f"오류가 났습니다: {e}"
    st.session_state.chat_log.append({"role": "assistant", "content": answer, "trace": []})


st.set_page_config(page_title="내 업무 Agent", page_icon="🗂️", layout="wide")
check_password()  # 비밀번호가 맞아야 아래 화면이 보인다

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

today = config.today()
week = parse_date_expression("이번 주", today)  # 이번 주 월~일 범위 (날짜 계산은 date_utils 에 맡김)

# 사이드바: 제목, 기준일과 요일, 사용 모델, 빠른 실행 버튼
with st.sidebar:
    st.title("그린팜 업무 비서")
    st.write(f"**기준일:** {today.isoformat()} ({WEEKDAYS[today.weekday()]}요일)")
    st.write(f"**사용 모델:** {config.MODEL}")
    st.divider()
    st.subheader("⚡ 빠른 실행")
    if st.button("📅 오늘 일정 요약"):
        run_quick("📅 오늘 일정 요약", lambda: summarize_schedule(today, today))
    if st.button("📅 이번 주 일정 요약"):
        run_quick("📅 이번 주 일정 요약", lambda: summarize_schedule(week.start, week.end))
    if st.button("✅ 이번 주 액션아이템"):
        run_quick("✅ 이번 주 액션아이템",
                  lambda: items_to_markdown(extract_action_items(week.start, week.end)))

# 본문 맨 위: 요약 숫자 4칸
today_schedule = find_files(today, today, category="일정")
week_meetings = find_files(week.start, week.end, category="회의록")
all_files = indexed_files()
unsorted = find_files(category="미분류")

col1, col2, col3, col4 = st.columns(4)
col1.metric("오늘 일정 건수", count_schedule_rows(today_schedule))
col2.metric("이번 주 회의록 수", len(week_meetings))
col3.metric("전체 문서 수", len(all_files))
col4.metric("미분류 문서 수", len(unsorted))

# 그 아래: 탭 4개
tab_chat, tab_schedule, tab_action, tab_docs = st.tabs(
    ["💬 채팅", "📅 일정", "✅ 액션아이템", "📁 문서 보기"]
)

# 💬 채팅 탭: 대화 기록은 session_state 에 두고, 화면이 다시 그려질 때마다 다시 보여줌
with tab_chat:
    agent = get_agent()
    for msg in st.session_state.chat_log:
        show_message(msg)

    question = st.chat_input("질문을 입력하세요 (예: 이번 주 회의 액션아이템 정리해줘)")
    if question and can_use_ai():
        user_msg = {"role": "user", "content": question, "trace": []}
        st.session_state.chat_log.append(user_msg)
        show_message(user_msg)
        with st.spinner("문서를 읽는 중..."):
            try:
                answer = agent.ask(question)
            except Exception as e:  # noqa: BLE001  API 오류 등을 화면에 보여주기 위해
                answer = f"오류가 났습니다: {e}"
        bot_msg = {"role": "assistant", "content": answer, "trace": list(agent.trace)}
        st.session_state.chat_log.append(bot_msg)
        show_message(bot_msg)

# 📅 일정 탭: 파일 내용은 AI 없이 보여주고, 요약 버튼을 누를 때만 AI 호출
with tab_schedule:
    picked = st.date_input("날짜를 고르세요", value=today)
    day_files = find_files(picked, picked, category="일정")
    if not day_files:
        st.info(f"{picked.isoformat()} 일정 파일이 없습니다.")
    else:
        for f in day_files:
            st.caption(f"📄 {f.name}")
            st.markdown(f.path.read_text(encoding="utf-8", errors="ignore"))
        if st.button("🤖 이 날 일정 AI 요약") and can_use_ai():
            with st.spinner("일정을 요약하는 중..."):
                st.markdown(summarize_schedule(picked, picked))

# ✅ 액션아이템 탭 / 📁 문서 보기 탭은 my_tabs.py 에서 그림
show_action_tab(tab_action, week)
show_docs_tab(tab_docs)
show_usage()  # 사이드바 맨 아래: AI 사용량 (모든 AI 호출 뒤에 그려야 최신 값)
