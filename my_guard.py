"""공유 링크용 안전장치: ① 비밀번호 화면 ② AI 사용 횟수 제한 (my_app.py 에서 import 해서 씀)"""
import hmac

import streamlit as st

import config


def check_password():
    """APP_PASSWORD 가 설정돼 있으면 맞는 비밀번호를 넣기 전까지 아래 화면을 멈춤"""
    if not config.APP_PASSWORD or st.session_state.get("logged_in"):
        return
    with st.form("login"):
        pw = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("입장")
    if submitted:
        # 글자 하나씩 비교하다 시간차로 비밀번호를 알아내는 것을 막기 위해 compare_digest 사용
        if hmac.compare_digest(pw.encode(), config.APP_PASSWORD.encode()):
            st.session_state.logged_in = True
            st.rerun()
        st.error("비밀번호가 틀렸습니다.")
    st.stop()


def can_use_ai() -> bool:
    """AI를 부르기 전에 확인. 한도를 넘었으면 경고만 띄우고 False, 아니면 횟수를 1 올리고 True"""
    used = st.session_state.get("ai_count", 0)
    if used >= config.MAX_QUESTIONS:
        st.warning(f"이번 접속의 AI 사용 한도({config.MAX_QUESTIONS}회)를 모두 썼습니다.")
        return False
    st.session_state.ai_count = used + 1
    return True


def show_usage():
    """사이드바에 AI 사용량을 막대로 보여줌"""
    used = st.session_state.get("ai_count", 0)
    limit = max(config.MAX_QUESTIONS, 1)
    st.sidebar.progress(min(used / limit, 1.0), text=f"AI 사용 {used}/{config.MAX_QUESTIONS}회")
