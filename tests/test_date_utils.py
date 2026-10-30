"""
날짜 해석 자동 테스트 (기준일 2026-10-30 금요일)
실행: python -m pytest tests -q   또는   python tests/test_date_utils.py
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "solution"))
from date_utils import file_date_range, guess_category, parse_date_expression  # noqa: E402

TODAY = date(2026, 10, 30)  # 금요일

CASES = [
    ("오늘 일정 알려줘", "2026-10-30", "2026-10-30"),
    ("어제 회의 뭐였지?", "2026-10-29", "2026-10-29"),
    ("그저께 미팅", "2026-10-28", "2026-10-28"),
    ("내일 일정", "2026-10-31", "2026-10-31"),
    ("지난주 수요일 일정", "2026-10-21", "2026-10-21"),
    ("이번 주 월요일 회의록", "2026-10-26", "2026-10-26"),
    ("다음주 월요일에 뭐 있어?", "2026-11-02", "2026-11-02"),
    ("목요일 고객사 미팅", "2026-10-29", "2026-10-29"),
    ("이번 주 액션아이템 정리", "2026-10-26", "2026-11-01"),
    ("지난주 회의록", "2026-10-19", "2026-10-25"),
    ("3일 전 일정", "2026-10-27", "2026-10-27"),
    ("최근 7일 회의", "2026-10-24", "2026-10-30"),
    ("10월 22일 회의록", "2026-10-22", "2026-10-22"),
    ("10/28 회의", "2026-10-28", "2026-10-28"),
    ("2026-10-19 일정", "2026-10-19", "2026-10-19"),
    ("지난달 보고서 요약", "2026-09-01", "2026-09-30"),
    ("9월 광고비 얼마야?", "2026-09-01", "2026-09-30"),
    ("3분기 실적", "2026-07-01", "2026-09-30"),
]


def test_expressions():
    for text, s, e in CASES:
        r = parse_date_expression(text, TODAY)
        assert r is not None, text
        assert (r.start.isoformat(), r.end.isoformat()) == (s, e), f"{text} → {r}"


def test_no_date():
    assert parse_date_expression("인스타그램 CPC가 왜 올랐어?", TODAY) is None


def test_filenames():
    assert file_date_range("2026-10-28_마케팅회의.md") == (date(2026, 10, 28), date(2026, 10, 28))
    assert file_date_range("2026-09_월간마케팅보고서.md") == (date(2026, 9, 1), date(2026, 9, 30))
    assert file_date_range("2026-Q3_분기실적보고서.md") == (date(2026, 7, 1), date(2026, 9, 30))
    assert file_date_range("회의메모_최종_진짜최종.txt") is None


def test_category():
    assert guess_category("오늘 일정 알려줘") == "일정"
    assert guess_category("어제 회의록 액션아이템") == "회의록"
    assert guess_category("지난달 매출 실적") == "보고서"


if __name__ == "__main__":
    for fn in (test_expressions, test_no_date, test_filenames, test_category):
        fn()
        print("✅", fn.__name__)
    print("모든 테스트 통과!")
