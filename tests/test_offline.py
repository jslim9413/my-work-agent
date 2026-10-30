"""
API 키 없이 전체 흐름을 점검하는 테스트 (LLM을 가짜 함수로 바꿔치기)
실행: python -m pytest tests -q
"""
import json
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "solution"))
import config  # noqa: E402
import llm  # noqa: E402

config._today = "2026-10-30"


def test_read_all_formats():
    from file_loader import list_files, read_text
    files = list_files()
    assert len(files) >= 20
    docx = next(f for f in files if f.name.endswith(".docx"))
    assert "해담식품" in read_text(docx.path)
    csvf = next(f for f in files if f.name.endswith(".csv"))
    assert "네이버검색" in read_text(csvf.path)


def test_find_files_by_date():
    from finder import find_files
    names = [f.name for f in find_files(date(2026, 10, 21), date(2026, 10, 21), "일정")]
    assert names == ["2026-10-21_일정.md"]
    reports = [f.name for f in find_files(date(2026, 9, 1), date(2026, 9, 30), "보고서")]
    assert "2026-09_월간마케팅보고서.md" in reports and "2026-Q3_분기실적보고서.md" in reports


def test_action_items(monkeypatch):
    import features
    fake = [{"담당자": "박민수", "할일": "키워드 30개 발굴", "마감일": "2026-10-30", "상태": "임박", "출처": "x.md"}]
    monkeypatch.setattr(llm, "ask", lambda *a, **k: "```json\n" + json.dumps(fake, ensure_ascii=False) + "\n```")
    items = features.extract_action_items(date(2026, 10, 26), date(2026, 11, 1))
    assert items[0]["담당자"] == "박민수"
    assert "키워드" in features.items_to_markdown(items)
    path = features.save_action_items_csv(items)
    assert Path(path).exists()
    Path(path).unlink()


def test_agent_loop(monkeypatch):
    import step3_agent
    calls = iter([
        SimpleNamespace(content="", tool_calls=[SimpleNamespace(
            id="t1", function=SimpleNamespace(name="resolve_date", arguments='{"expression": "지난주 수요일"}'),
            model_dump=lambda: {"id": "t1", "type": "function",
                                "function": {"name": "resolve_date", "arguments": '{"expression": "지난주 수요일"}'}})]),
        SimpleNamespace(content="지난주 수요일은 2026-10-21 입니다.", tool_calls=None),
    ])
    monkeypatch.setattr(llm, "chat", lambda *a, **k: next(calls))
    agent = step3_agent.Agent(verbose=False)
    assert "2026-10-21" in agent.ask("지난주 수요일 일정?")
    assert agent.trace and "resolve_date" in agent.trace[0]
    tool_msg = agent.messages[-2]
    assert tool_msg["role"] == "tool" and "2026-10-21" in tool_msg["content"]
