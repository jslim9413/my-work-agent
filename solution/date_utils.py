"""
2교시: 날짜 자동 인식
 (1) 질문 속 날짜 표현  → 기간(start~end)   예) "지난주 수요일 회의록" → 10/21~10/21
 (2) 파일 이름 속 날짜   → 기간(start~end)   예) "2026-09_월간보고서.md" → 9/1~9/30
 (3) 두 기간이 겹치는 파일만 골라내기
"""
import re
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta

WEEKDAYS = "월화수목금토일"


@dataclass
class DateRange:
    start: date
    end: date
    label: str

    def __str__(self):
        if self.start == self.end:
            return f"{self.label} ({self.start.isoformat()} {WEEKDAYS[self.start.weekday()]})"
        return f"{self.label} ({self.start.isoformat()} ~ {self.end.isoformat()})"


def _week(d: date) -> tuple[date, date]:
    mon = d - timedelta(days=d.weekday())
    return mon, mon + timedelta(days=6)


def _month(y: int, m: int) -> tuple[date, date]:
    return date(y, m, 1), date(y, m, monthrange(y, m)[1])


def _quarter(y: int, q: int) -> tuple[date, date]:
    s, _ = _month(y, 3 * q - 2)
    _, e = _month(y, 3 * q)
    return s, e


# ---------------------------------------------------------------- (1) 질문 → 기간
def parse_date_expression(text: str, today: date) -> DateRange | None:
    t = text.replace(" ", "")

    # ① 명시적 날짜: 2026-10-28 / 2026.10.28 / 2026/10/28
    m = re.search(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", t)
    if m:
        d = date(int(m[1]), int(m[2]), int(m[3]))
        return DateRange(d, d, "지정일")
    # ② 10월 28일 / 10/28
    m = re.search(r"(\d{1,2})월(\d{1,2})일", t) or re.search(r"(?<!\d)(\d{1,2})/(\d{1,2})(?!\d)", t)
    if m:
        d = date(today.year, int(m[1]), int(m[2]))
        return DateRange(d, d, "지정일")

    # ③ 주 + 요일: 지난주 수요일 / 이번 주 금요일 / 다음주 월요일 / (그냥) 수요일
    m = re.search(r"(지난주|저번주|전주|이번주|금주|다음주|차주)?([월화수목금토일])요일", t)
    if m:
        shift = {"지난주": -7, "저번주": -7, "전주": -7, "다음주": 7, "차주": 7}.get(m[1] or "", 0)
        mon, _ = _week(today)
        d = mon + timedelta(days=shift + WEEKDAYS.index(m[2]))
        return DateRange(d, d, f"{m[1] or '이번주'} {m[2]}요일")

    # ④ 상대 일자
    rel = {"그저께": -2, "그제": -2, "어제": -1, "오늘": 0, "금일": 0, "내일": 1, "모레": 2}
    for word, n in rel.items():
        if word in t:
            d = today + timedelta(days=n)
            return DateRange(d, d, word)
    m = re.search(r"(\d+)일전", t)
    if m:
        d = today - timedelta(days=int(m[1]))
        return DateRange(d, d, f"{m[1]}일 전")
    m = re.search(r"최근(\d+)일", t)
    if m:
        return DateRange(today - timedelta(days=int(m[1]) - 1), today, f"최근 {m[1]}일")

    # ⑤ 주 단위
    for words, shift, label in ((("지난주", "저번주", "전주"), -7, "지난주"),
                                (("다음주", "차주"), 7, "다음 주"),
                                (("이번주", "금주"), 0, "이번 주")):
        if any(w in t for w in words):
            s, e = _week(today + timedelta(days=shift))
            return DateRange(s, e, label)

    # ⑥ 월 / 분기
    if any(w in t for w in ("지난달", "저번달", "전월")):
        last = today.replace(day=1) - timedelta(days=1)
        return DateRange(*_month(last.year, last.month), "지난달")
    if any(w in t for w in ("이번달", "금월")):
        return DateRange(*_month(today.year, today.month), "이번 달")
    m = re.search(r"(?<!\d)(\d{1,2})월", t)
    if m and 1 <= int(m[1]) <= 12:
        return DateRange(*_month(today.year, int(m[1])), f"{int(m[1])}월")
    m = re.search(r"([1-4])분기|Q([1-4])", t, re.I)
    if m:
        q = int(m[1] or m[2])
        return DateRange(*_quarter(today.year, q), f"{q}분기")
    return None


# ---------------------------------------------------------------- (2) 파일명 → 기간
def file_date_range(filename: str) -> tuple[date, date] | None:
    """파일명 맨 앞의 날짜 규칙을 해석. 규칙: YYYY-MM-DD_ / YYYY-MM_ / YYYY-Q1_"""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", filename)
    if m:
        d = date(int(m[1]), int(m[2]), int(m[3]))
        return d, d
    m = re.match(r"(\d{4})-[Qq]([1-4])", filename)
    if m:
        return _quarter(int(m[1]), int(m[2]))
    m = re.match(r"(\d{4})-(\d{2})(?!\d)", filename)
    if m:
        return _month(int(m[1]), int(m[2]))
    return None


# ---------------------------------------------------------------- (3) 겹치는지 확인
def overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return a_start <= b_end and b_start <= a_end


CATEGORY_WORDS = {
    "일정": ("일정", "스케줄", "약속", "미팅 시간", "뭐 있"),
    "회의록": ("회의", "미팅", "회의록", "액션", "할 일", "할일", "담당"),
    "보고서": ("보고서", "보고", "실적", "성과", "매출", "광고비", "전환율", "ROAS"),
}


def guess_category(text: str) -> str | None:
    """질문에서 어떤 종류의 문서를 원하는지 추정 (가장 많이 맞은 카테고리)"""
    scores = {c: sum(w in text for w in ws) for c, ws in CATEGORY_WORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else None
