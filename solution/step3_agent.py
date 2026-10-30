"""
3교시 완성본: 도구(tool)를 골라 쓰는 업무 Agent
  - LLM이 질문을 보고 어떤 도구를 쓸지 '스스로' 결정 (function calling)
  - 날짜 계산은 LLM 대신 resolve_date 도구가 정확하게 처리
실행: python solution/step3_agent.py
"""
import json
from datetime import date

import config
import llm
from date_utils import WEEKDAYS, parse_date_expression
from features import (ask_reports, extract_action_items, items_to_markdown,
                      save_action_items_csv, summarize_schedule)
from file_loader import read_text
from finder import find_files, indexed_files

SYSTEM = """너는 '{user}'의 업무 폴더를 관리하는 AI 업무 비서 Agent다. 오늘은 {today}.

업무 폴더 구조: 일정/ (하루 1파일), 회의록/, 보고서/, 미분류/
도구 사용 원칙
1. 질문에 날짜 표현(오늘, 어제, 지난주 수요일, 이번 달…)이 있으면 **먼저 resolve_date 로 정확한 날짜를 얻는다.** 날짜를 직접 계산하지 않는다.
2. 일정 정리/요약 → summarize_schedule
3. 할 일·액션아이템·담당자·마감 → extract_action_items
4. 매출·광고비·성과 등 보고서 내용 → ask_reports
5. 그 외 특정 문서 내용 → find_files 로 찾고 read_file 로 읽어서 답한다.
6. 도구 결과에 없는 내용은 지어내지 않는다. 답변 끝에 근거 파일명을 적는다.
7. 한국어로, 표·목록을 활용해 핵심부터 답한다."""

TOOLS = [
    {"type": "function", "function": {
        "name": "resolve_date",
        "description": "'오늘', '지난주 수요일', '이번 주', '지난달' 같은 날짜 표현을 실제 날짜 범위(YYYY-MM-DD)로 바꾼다.",
        "parameters": {"type": "object", "properties": {
            "expression": {"type": "string", "description": "사용자 질문 속 날짜 표현"}},
            "required": ["expression"]}}},
    {"type": "function", "function": {
        "name": "find_files",
        "description": "기간과 문서 종류로 업무 폴더의 파일 목록을 찾는다.",
        "parameters": {"type": "object", "properties": {
            "start": {"type": "string", "description": "YYYY-MM-DD (생략 시 전체 기간)"},
            "end": {"type": "string", "description": "YYYY-MM-DD"},
            "category": {"type": "string", "enum": ["일정", "회의록", "보고서", "미분류"]}}}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "파일 이름으로 파일 내용을 읽는다.",
        "parameters": {"type": "object", "properties": {
            "filename": {"type": "string"}}, "required": ["filename"]}}},
    {"type": "function", "function": {
        "name": "summarize_schedule",
        "description": "기간 내 일정 파일을 읽어 날짜별 일정, 챙길 것, 중요 일정 3개로 요약한다.",
        "parameters": {"type": "object", "properties": {
            "start": {"type": "string"}, "end": {"type": "string"}}, "required": ["start", "end"]}}},
    {"type": "function", "function": {
        "name": "extract_action_items",
        "description": "기간 내 회의록에서 담당자/할일/마감일 액션아이템을 추출해 표로 만들고 CSV로 저장한다.",
        "parameters": {"type": "object", "properties": {
            "start": {"type": "string"}, "end": {"type": "string"},
            "assignee": {"type": "string", "description": "특정 담당자 이름만 보고 싶을 때"}},
            "required": ["start", "end"]}}},
    {"type": "function", "function": {
        "name": "ask_reports",
        "description": "보고서(월간/분기/주간 성과, 채널별 데이터)를 읽고 질문에 숫자 근거와 함께 답한다.",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string"}}, "required": ["question"]}}},
]


def _d(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


def run_tool(name: str, args: dict) -> str:
    """LLM이 고른 도구를 실제 파이썬 함수로 실행"""
    if name == "resolve_date":
        r = parse_date_expression(args["expression"], config.today())
        if not r:
            return "날짜 표현을 해석하지 못했습니다. 전체 기간으로 진행하세요."
        return json.dumps({"start": r.start.isoformat(), "end": r.end.isoformat(), "설명": str(r)}, ensure_ascii=False)
    if name == "find_files":
        files = find_files(_d(args.get("start")), _d(args.get("end")), args.get("category"))
        return "\n".join(f"{f.name} ({f.category}, {f.start}~{f.end})" for f in files) or "파일 없음"
    if name == "read_file":
        for f in indexed_files():
            if f.name == args["filename"] or args["filename"] in f.name:
                return read_text(f.path)
        return "파일을 찾을 수 없습니다."
    if name == "summarize_schedule":
        return summarize_schedule(_d(args["start"]), _d(args["end"]))
    if name == "extract_action_items":
        items = extract_action_items(_d(args["start"]), _d(args["end"]), args.get("assignee"))
        path = save_action_items_csv(items) if items else None
        return items_to_markdown(items) + (f"\n\n(CSV 저장: {path})" if path else "")
    if name == "ask_reports":
        return ask_reports(args["question"])
    return f"알 수 없는 도구: {name}"


class Agent:
    def __init__(self, user: str = "박민수 대리", verbose: bool = True):
        t = config.today()
        today = f"{t.isoformat()} ({WEEKDAYS[t.weekday()]}요일)"
        self.messages = [{"role": "system", "content": SYSTEM.format(user=user, today=today)}]
        self.verbose = verbose
        self.trace: list[str] = []   # 화면에 보여줄 도구 사용 기록

    def ask(self, question: str, max_steps: int = 6) -> str:
        self.messages.append({"role": "user", "content": question})
        self.trace = []
        for _ in range(max_steps):
            msg = llm.chat(self.messages, TOOLS)
            if not msg.tool_calls:                       # 도구가 더 필요 없으면 최종 답변
                self.messages.append({"role": "assistant", "content": msg.content or ""})
                return msg.content or ""
            self.messages.append({"role": "assistant", "content": msg.content or "",
                                  "tool_calls": [tc.model_dump() for tc in msg.tool_calls]})
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments or "{}")
                log = f"🔧 {tc.function.name}({', '.join(f'{k}={v}' for k, v in args.items())})"
                self.trace.append(log)
                if self.verbose:
                    print("   " + log)
                result = run_tool(tc.function.name, args)
                self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        return "도구를 너무 많이 호출해서 멈췄습니다. 질문을 조금 더 구체적으로 해주세요."


def main():
    agent = Agent()
    t = config.today()
    print(f"🤖 업무 Agent 시작 (오늘: {t} {WEEKDAYS[t.weekday()]}요일, 모델: {config.MODEL})  종료: q")
    print("예) 오늘 일정 요약해줘 / 이번 주 회의 액션아이템 정리해줘 / 9월 네이버 ROAS가 얼마야?")
    while True:
        q = input("\n🙋 > ").strip()
        if q.lower() in ("q", "quit", "exit", "종료"):
            break
        if q:
            print(f"\n🤖 {agent.ask(q)}")


if __name__ == "__main__":
    main()
