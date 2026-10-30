"""
웹 앱(streamlit_app.py) 동작 테스트 - API 키 없이 가짜 AI로 버튼·탭을 눌러 봄
실행: python -m pytest tests -q
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "solution"))
import config  # noqa: E402
import llm  # noqa: E402

FAKE_ITEMS = [{"담당자": "박민수", "할일": "키워드 30개 발굴", "마감일": "2026-10-30", "상태": "임박", "출처": "x.md"}]


def _fake(monkeypatch):
    monkeypatch.setattr(config, "APP_PASSWORD", "")
    monkeypatch.setattr(llm, "ask", lambda *a, **k: json.dumps(FAKE_ITEMS, ensure_ascii=False)
                        if "액션" in a[0] or "회의록" in a[0] else "가짜 요약")
    monkeypatch.setattr(llm, "chat", lambda *a, **k: SimpleNamespace(content="가짜 답변", tool_calls=None))


def test_app_renders_and_buttons(monkeypatch):
    _fake(monkeypatch)
    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    assert not at.exception
    assert [m.value for m in at.metric][:2] == ["3건", "3건"]

    next(b for b in at.button if "오늘 일정 요약" in b.label).click().run()
    assert any("가짜 요약" in m.value for m in at.markdown)

    next(b for b in at.button if "액션아이템 추출" in b.label).click().run()
    assert not at.exception
    assert at.dataframe and at.session_state["used"] == 2

    at.chat_input[0].set_value("오늘 일정?").run()
    assert any("가짜 답변" in m.value for m in at.markdown)


def test_password_gate(monkeypatch):
    _fake(monkeypatch)
    monkeypatch.setattr(config, "APP_PASSWORD", "abc")
    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    assert at.title[0].value.startswith("🔒")
    assert not at.metric                       # 비밀번호 전에는 본 화면이 안 보임
    at.text_input[0].set_value("abc")
    at.button[0].click().run()
    assert at.metric


def test_usage_limit(monkeypatch):
    _fake(monkeypatch)
    monkeypatch.setattr(config, "MAX_QUESTIONS", 1)
    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    at.chat_input[0].set_value("하나").run()
    at.chat_input[0].set_value("둘").run()
    assert any("사용 한도" in w.value for w in at.warning)
