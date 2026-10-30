"""
1교시 완성본: 내 업무폴더 파일을 읽고 질문에 답하는 AI
실행: python solution/step1_file_reader.py
"""
import llm
from file_loader import build_context, list_files

SYSTEM = """너는 사용자의 업무 폴더 문서를 읽고 질문에 답하는 업무 비서다.
규칙:
1. 반드시 아래 [업무 문서]에 있는 내용만 근거로 답한다. 문서에 없으면 "문서에서 찾을 수 없습니다"라고 말한다.
2. 질문의 표현이 문서와 조금 달라도 같은 대상이면 찾아서 답한다. (예: '네이버 검색광고' = 표의 '네이버 검색')
   표 안의 숫자도 근거로 사용한다.
3. 답변 끝에 근거가 된 파일명을 '출처:' 로 적는다.
4. 한국어로, 핵심부터 짧게 답한다."""


def main():
    files = list_files()
    print(f"📂 업무폴더에서 {len(files)}개 파일을 읽었습니다.")
    for f in files:
        print("   -", f.rel())
    context = build_context(files)

    print("\n질문을 입력하세요 (종료: q)")
    while True:
        q = input("\n🙋 질문> ").strip()
        if q.lower() in ("q", "quit", "exit", "종료"):
            break
        if not q:
            continue
        answer = llm.ask(SYSTEM, f"[업무 문서]\n{context}\n\n[질문]\n{q}")
        print(f"\n🤖 {answer}")


if __name__ == "__main__":
    main()
