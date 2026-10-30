"""
2교시 완성본: 질문 속 날짜를 알아듣고, 해당 날짜 파일만 골라 읽어서 답하는 AI
실행: python solution/step2_date_finder.py
"""
import config
import llm
from date_utils import WEEKDAYS, guess_category, parse_date_expression
from file_loader import build_context
from finder import find_files

SYSTEM = """너는 사용자의 업무 폴더 문서를 읽고 질문에 답하는 업무 비서다.
- 오늘은 {today} 이다. '오늘/어제/지난주' 같은 표현은 이 날짜 기준으로 해석한다.
- 아래 [업무 문서]는 질문의 날짜 조건에 맞춰 미리 골라낸 파일들이다.
- 질문의 표현이 문서와 조금 달라도 같은 대상이면 찾아서 답한다. 표 안의 숫자도 근거로 사용한다.
- 문서에 있는 내용만 근거로 답하고, 없으면 "해당 날짜의 문서에서 찾을 수 없습니다"라고 말한다.
- 답변 끝에 '출처:' 와 파일명을 적는다."""


def answer(question: str) -> str:
    today = config.today()
    rng = parse_date_expression(question, today)
    category = guess_category(question)
    files = find_files(rng.start if rng else None, rng.end if rng else None, category)

    print(f"   🗓  날짜 해석: {rng or '날짜 표현 없음 → 전체 기간'}")
    print(f"   🗂  문서 종류: {category or '전체'}")
    print(f"   📄 선택된 파일 {len(files)}개: {', '.join(f.name for f in files) or '없음'}")
    if not files:
        return "조건에 맞는 파일이 없습니다. 날짜나 문서 종류를 바꿔서 물어봐 주세요."

    system = SYSTEM.format(today=f"{today.isoformat()} ({WEEKDAYS[today.weekday()]}요일)")
    return llm.ask(system, f"[업무 문서]\n{build_context(files)}\n\n[질문]\n{question}")


def main():
    t = config.today()
    print(f"📅 기준일(오늘): {t} ({WEEKDAYS[t.weekday()]}요일)   종료: q")
    while True:
        q = input("\n🙋 질문> ").strip()
        if q.lower() in ("q", "quit", "exit", "종료"):
            break
        if q:
            print(f"\n🤖 {answer(q)}")


if __name__ == "__main__":
    main()
