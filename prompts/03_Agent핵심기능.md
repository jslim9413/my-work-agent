# 3교시 — Agent 핵심 기능 완성하기

목표: 일정 요약 · 회의록 액션아이템 추출 · 보고서 질의응답 3가지 기능을 만들고,
AI가 질문을 보고 **어떤 기능(도구)을 쓸지 스스로 고르는** Agent로 묶기
정답 코드: `solution/features.py`, `step3_agent.py`

```
          ┌─ resolve_date ─────── 날짜 계산 (코드)
질문 ─▶ Agent(LLM) ─┼─ summarize_schedule ─ 일정 요약
          │  스스로 선택   ├─ extract_action_items ─ 액션아이템 표 + CSV
          │              ├─ ask_reports ───────── 보고서 Q&A
          └─ 결과 종합 ◀──┴─ find_files / read_file ─ 그 외 문서
```

---

## 프롬프트 3-1. 일정 요약 기능
```
my_agent/features.py 에 summarize_schedule(start, end) 를 만들어줘.
find_files 로 해당 기간 '일정' 파일만 모아서 LLM에게 아래 시스템 프롬프트로 요약을 받는다.
각 파일 머리표에 [문서 날짜: 2026-10-30 (금)] 처럼 날짜와 요일을 붙여서 넘겨줘.

[시스템 프롬프트]
prompts/agent_system_prompts.md 의 '① 일정 요약' 을 그대로 사용

테스트: 이번 주(2026-10-26~11-01) 요약을 출력해줘.
```
✅ 확인: 날짜별 정리 + 외부 일정(성수, 판교) 이동 주의 + 중요 일정 3개

## 프롬프트 3-2. 회의록 액션아이템 추출 ★핵심
```
features.py 에 extract_action_items(start, end, assignee=None) 를 추가해줘.
1. 해당 기간의 '회의록'과 '미분류' 파일을 읽는다 (문서 날짜 머리표 포함).
2. 시스템 프롬프트는 prompts/agent_system_prompts.md 의 '② 액션아이템 추출' 을 사용하고,
   결과는 JSON 배열로 받는다. temperature=0.
3. ```json 코드블록이 섞여 와도 파싱되게 해줘. 파싱 실패 시 프로그램이 죽지 않게 한다.
4. assignee 가 주어지면 그 사람 것만 남기고, 마감일 순으로 정렬한다.
5. save_action_items_csv(items) 로 output/액션아이템_날짜시각.csv 에 utf-8-sig 로 저장한다.
6. items_to_markdown(items) 로 상태 아이콘(🔴기한지남 🟠임박 🟢예정 ⚪확인필요)이 붙은 표를 만든다.
```
✅ 확인: 이번 주 회의록에서 10개 이상 추출, 마케팅회의의 "금요일까지" → 2026-10-30,
고객사미팅의 "일정 미정" → 미정/확인필요, 미분류 메모의 쿠폰 코드 요청도 잡히는지

> 💡 강사 포인트: 회의록 5개의 형식이 전부 다릅니다 (체크박스 / 본문 문장 / 표 / 대괄호 섹션 / Word).
> 사람이 정리하던 "형식이 제각각인 문서"를 AI가 **하나의 표**로 만드는 게 이 기능의 가치입니다.
> "다음 주 화요일까지" 같은 상대 마감일이 **회의 날짜 기준**으로 계산되는지 꼭 확인시키세요.

## 프롬프트 3-3. 보고서 질의응답
```
features.py 에 ask_reports(question) 를 추가해줘.
질문에 날짜 표현이 있으면 그 기간의 보고서만, 없거나 못 찾으면 보고서 전체를 읽는다.
시스템 프롬프트는 prompts/agent_system_prompts.md 의 '③ 보고서 Q&A' 를 사용한다.
테스트: "9월 채널별 ROAS를 높은 순으로 비교하고, 예산을 옮긴다면 어디로 옮길지 근거와 함께 말해줘"
```

## 프롬프트 3-4. 도구를 고르는 Agent로 묶기
```
my_agent/step3_agent.py 를 만들어줘. OpenAI function calling(tools) 방식을 쓴다.

도구 6개: resolve_date(expression), find_files(start,end,category), read_file(filename),
summarize_schedule(start,end), extract_action_items(start,end,assignee), ask_reports(question)
- 각 도구의 description 은 한국어로, LLM이 언제 써야 할지 알 수 있게 구체적으로.
- Agent 클래스: messages 기록을 유지하고 ask(question) 에서
  LLM 호출 → tool_calls 가 있으면 실행해서 결과를 role=tool 로 붙이고 다시 호출 → 없으면 최종 답변.
  최대 6번 반복.
- 도구를 쓸 때마다 '🔧 도구이름(인자)'를 화면에 출력해서 Agent의 생각 과정을 보이게 한다.
- 시스템 프롬프트는 prompts/agent_system_prompts.md 의 '④ Agent 총괄' 을 사용한다.
```

## 🧪 테스트 질문 (3교시)
| 질문 | Agent가 써야 할 도구 | 기대 결과 |
|---|---|---|
| 오늘 일정 요약해줘 | resolve_date → summarize_schedule | 10/30 일정 3개, 시음회 샘플 50병 |
| 이번 주 회의 액션아이템 정리해줘 | resolve_date → extract_action_items | 표 + CSV 저장 경로 |
| 이번 주 내 할 일만 보여줘 (박민수) | extract_action_items(assignee=박민수) | 박민수 항목만 |
| 기한 지난 할 일 있어? | extract_action_items | 🔴 항목 목록 |
| 3분기 매출 목표 달성했어? | ask_reports | 5억 2,300만 / 105% 달성 |
| 인스타 CPC 왜 올랐대? | ask_reports 또는 find_files+read_file | 소재 피로도, 610→820원 |

## 🛠 막혔을 때
```
모델이 도구를 호출하지 않고 바로 대답해버려. 시스템 프롬프트와 도구 description 을 어떻게 고치면
'날짜 표현이 있으면 반드시 resolve_date 를 먼저 쓰게' 만들 수 있는지 고치고 다시 테스트해줘.
```
```
"Invalid parameter: messages with role 'tool' must be a response to a preceding message with
'tool_calls'" 에러가 나. assistant 메시지에 tool_calls 를 같이 저장하도록 고쳐줘.
```
```
액션아이템 JSON 파싱이 자주 실패해. 실패한 원문을 출력해서 원인을 보여주고,
프롬프트와 파싱 코드 둘 다 보강해줘.
```
