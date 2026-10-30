"""
3교시: Agent 핵심 기능 3가지
  ① summarize_schedule   일정 요약
  ② extract_action_items 회의록 → 액션아이템 표 + CSV 저장
  ③ ask_reports          보고서 질의응답
"""
import csv
from datetime import date, datetime

import config
import llm
from date_utils import WEEKDAYS, parse_date_expression
from file_loader import WorkFile, read_text
from finder import find_files


def _today_str() -> str:
    t = config.today()
    return f"{t.isoformat()} ({WEEKDAYS[t.weekday()]}요일)"


def _context_with_dates(files: list[WorkFile]) -> str:
    """각 파일에 '문서 날짜'를 붙여서 LLM이 '다음 주 화요일' 같은 상대 마감일을 계산할 수 있게 함"""
    blocks = []
    for f in files:
        d = f"{f.start.isoformat()} ({WEEKDAYS[f.start.weekday()]})" if f.start else "알 수 없음"
        blocks.append(f"### [파일: {f.rel()}] [문서 날짜: {d}]\n{read_text(f.path)}")
    return "\n\n".join(blocks)


# ------------------------------------------------------------------ ① 일정 요약
SCHEDULE_PROMPT = """너는 바쁜 직장인의 일정 비서다. 오늘은 {today}.
아래 일정 문서를 보고 다음 형식으로 정리해라.

## 📅 한눈에 보기
- 날짜별로 '시간 - 일정(장소)'를 한 줄씩. 날짜 머리에는 요일을 붙인다.

## ⚠️ 챙길 것
- 이동이 필요한 외부 일정, 마감이 걸린 일정, 준비물이 필요한 일정을 골라 이유와 함께 적는다.
- 일정 간격이 1시간 이내로 붙어 있어 빠듯한 경우도 알려준다.

## ⭐ 가장 중요한 일정 3개
- 중요도 순으로, 왜 중요한지 한 문장씩.

문서에 없는 일정은 절대 만들지 않는다."""


def summarize_schedule(start: date, end: date) -> str:
    files = find_files(start, end, "일정")
    if not files:
        return f"{start}~{end} 기간의 일정 파일이 없습니다."
    return llm.ask(SCHEDULE_PROMPT.format(today=_today_str()), _context_with_dates(files))


# ------------------------------------------------------------ ② 액션아이템 추출
ACTION_PROMPT = """너는 회의록에서 '누가 언제까지 무엇을 해야 하는지'를 뽑아내는 전문가다. 오늘은 {today}.

규칙
1. 'Action Items' 섹션뿐 아니라 본문 문장 속 약속("~하기로 함", "~까지 공유 예정")도 모두 찾는다.
2. 마감일은 YYYY-MM-DD 로 바꾼다. '오늘', '다음 주 화요일', '이번 주 금요일' 같은 표현은
   **그 회의록의 [문서 날짜] 기준**으로 계산한다. 마감이 없거나 모호하면 "미정".
3. 담당자는 이름만 적는다(직급 제외). 외부인은 이름 뒤에 (회사명).
4. 상태: 마감일이 오늘({today_iso})보다 이전이면 "기한지남", 오늘~3일 이내면 "임박", 그 외 "예정", 미정이면 "확인필요".
5. 아래 JSON 배열만 출력한다. 설명 문장, 코드블록 표시 금지.
[{{"담당자": "", "할일": "", "마감일": "", "상태": "", "출처": "파일명"}}]"""


def extract_action_items(start: date, end: date, assignee: str | None = None) -> list[dict]:
    files = [f for f in find_files(start, end) if f.category in ("회의록", "미분류")]
    if not files:
        return []
    raw = llm.ask(ACTION_PROMPT.format(today=_today_str(), today_iso=config.today().isoformat()),
                  _context_with_dates(files), temperature=0)
    try:
        items = llm.parse_json(raw)
    except Exception:
        return [{"담당자": "-", "할일": "JSON 변환 실패. 원문: " + raw[:300], "마감일": "", "상태": "", "출처": ""}]
    if assignee:
        items = [i for i in items if assignee in i.get("담당자", "")]
    return sorted(items, key=lambda i: i.get("마감일") or "9999")


def save_action_items_csv(items: list[dict]) -> str:
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    path = config.OUTPUT_DIR / f"액션아이템_{datetime.now():%Y%m%d_%H%M}.csv"
    with open(path, "w", encoding="utf-8-sig", newline="") as f:  # utf-8-sig: 엑셀 한글 깨짐 방지
        w = csv.DictWriter(f, fieldnames=["담당자", "할일", "마감일", "상태", "출처"], extrasaction="ignore")
        w.writeheader()
        w.writerows(items)
    return str(path)


def items_to_markdown(items: list[dict]) -> str:
    if not items:
        return "해당 기간에 액션아이템이 없습니다."
    icon = {"기한지남": "🔴", "임박": "🟠", "예정": "🟢", "확인필요": "⚪"}
    rows = [f"| {icon.get(i.get('상태'), '')} {i.get('상태', '')} | {i.get('담당자', '')} | {i.get('할일', '')} "
            f"| {i.get('마감일', '')} | {i.get('출처', '')} |" for i in items]
    return "| 상태 | 담당자 | 할 일 | 마감일 | 출처 |\n|---|---|---|---|---|\n" + "\n".join(rows)


# ------------------------------------------------------------ ③ 보고서 질의응답
REPORT_PROMPT = """너는 마케팅 보고서를 분석하는 데이터 분석가다. 오늘은 {today}.
규칙
1. 보고서에 적힌 숫자만 사용한다. 계산이 필요하면 계산 과정을 한 줄로 보여준다.
2. 보고서끼리 비교가 가능하면 비교해서 의미를 짚어준다 (예: 전월 대비, 목표 대비).
3. 근거 문장이나 표의 행을 짧게 인용하고, 마지막 줄에 '출처: 파일명'을 적는다.
4. 보고서에 없는 내용이면 추측하지 말고 "보고서에 없는 내용입니다"라고 답한다."""


def ask_reports(question: str) -> str:
    rng = parse_date_expression(question, config.today())
    files = find_files(rng.start if rng else None, rng.end if rng else None, "보고서")
    if not files:  # 날짜 조건으로 못 찾으면 보고서 전체에서 찾기
        files = find_files(category="보고서")
    return llm.ask(REPORT_PROMPT.format(today=_today_str()),
                   f"[보고서]\n{_context_with_dates(files)}\n\n[질문]\n{question}")
