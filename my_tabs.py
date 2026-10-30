"""✅ 액션아이템 탭, 📁 문서 보기 탭 그리기 (my_app.py 에서 import 해서 씀)"""
from pathlib import Path

import streamlit as st

from features import extract_action_items, save_action_items_csv
from file_loader import read_text
from finder import find_files
from my_guard import can_use_ai


def show_action_tab(tab, week):
    """✅ 액션아이템 탭: 결과는 session_state 에 저장해 두고, 다른 버튼을 눌러도 유지"""
    with tab:
        c1, c2, c3 = st.columns(3)
        start = c1.date_input("시작일", value=week.start, key="act_start")
        end = c2.date_input("종료일", value=week.end, key="act_end")
        assignee = c3.text_input("담당자 (비우면 전체)", key="act_who")
        if st.button("액션아이템 추출") and can_use_ai():
            with st.spinner("회의록을 읽는 중..."):
                rows = extract_action_items(start, end, assignee.strip() or None)
            path = save_action_items_csv(rows) if rows else None  # output/ 에 utf-8-sig 로 저장
            st.session_state.action_result = {"rows": rows, "csv_path": path}
        if "action_result" in st.session_state:
            res = st.session_state.action_result
            if res["rows"]:
                st.dataframe(res["rows"])
                st.download_button("⬇️ CSV 다운로드", Path(res["csv_path"]).read_bytes(),
                                   file_name=Path(res["csv_path"]).name, mime="text/csv")
            else:
                st.info("해당 기간에 액션아이템이 없습니다.")


def show_docs_tab(tab):
    """📁 문서 보기 탭: 종류를 고르고 문서를 골라서 내용을 봄 (.md 는 markdown, 나머지는 text)"""
    with tab:
        kind = st.radio("종류", ["전체", "일정", "회의록", "보고서", "미분류"], horizontal=True)
        docs = find_files(category=None if kind == "전체" else kind)
        if not docs:
            st.info("해당 종류의 문서가 없습니다.")
        else:
            doc = st.selectbox("문서", docs, format_func=lambda f: f.rel())
            text = read_text(doc.path, max_chars=100000)
            if doc.path.suffix.lower() == ".md":
                st.markdown(text)
            else:
                st.text(text)
