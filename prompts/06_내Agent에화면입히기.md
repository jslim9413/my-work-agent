# 2부 2교시 — 내 Agent에 화면 입히기

목표: 1부에서 만든 Agent(터미널용)를 **버튼 클릭만으로 쓰는 웹 화면**으로 감싸기
만들 파일: 키트 최상위 폴더의 `my_app.py`  (실행: `streamlit run my_app.py`)
정답: `streamlit_app.py` (같은 위치)

```
my_app.py (화면)  ──부른다──▶  solution/ (1부 Agent: 날짜 해석·파일 찾기·요약·액션아이템)
```
화면 코드는 "무엇을 보여줄지"만, 실제 일은 1부 코드가 합니다. → **화면과 기능을 나누는 것**이 이번 교시의 핵심.

---

## 프롬프트 6-1. 화면 뼈대 (10분)
```
키트 최상위 폴더에 my_app.py 를 streamlit 으로 만들어줘. 1부 Agent 기능은 solution/ 폴더의 모듈을
import 해서 재사용한다 (sys.path 에 solution 폴더 추가). 이번 단계는 뼈대만 만든다.

- 페이지 제목 "내 업무 Agent", 아이콘 🗂️, layout="wide"
- 사이드바: 제목, 기준일(config.today())과 요일, 사용 모델(config.MODEL)
- 본문 맨 위: st.metric 4칸 → 오늘 일정 건수, 이번 주 회의록 수, 전체 문서 수, 미분류 문서 수
  (finder.find_files / indexed_files 사용. 일정 건수는 일정 파일 표에서 시간으로 시작하는 줄 수)
- 그 아래 탭 4개: 💬 채팅 / 📅 일정 / ✅ 액션아이템 / 📁 문서 보기 (지금은 "준비 중" 글자만)
```
✅ 확인: 숫자 카드가 3건 / 3건 / 21개 / 1개

## 프롬프트 6-2. 채팅 탭 (15분) ★핵심
```
my_app.py 의 '💬 채팅' 탭을 완성해줘.
- solution/step3_agent.py 의 Agent 를 session_state 에 한 번만 만들어 두고 계속 재사용한다.
- 대화 기록을 session_state 에 저장하고, 화면이 다시 실행될 때마다 기록을 다시 그린다.
- st.chat_input 으로 질문 → st.spinner("문서를 읽는 중...") 동안 agent.ask() 호출 → 답변 표시
- 답변 위에 접을 수 있는 '🔧 Agent가 사용한 도구' 영역 (agent.trace 내용)
```
✅ 확인: "지난주 수요일에 무슨 일정 있었지?" → 도구 영역에 resolve_date 가 보이고 10/21 일정이 답변됨
✅ 확인: 두 번째 질문을 해도 첫 번째 대화가 사라지지 않음

> 💡 강사 포인트: Agent 를 session_state 에 넣지 않으면? → 질문할 때마다 새 Agent 가 만들어져
> "그중에 박민수 것만" 같은 **이어지는 질문이 안 됩니다.** 일부러 틀리게 만들어 보여주면 효과적.

## 프롬프트 6-3. 빠른 실행 버튼 + 일정 탭 (10분)
```
1) 사이드바에 '빠른 실행' 버튼 3개를 추가해줘: 📅 오늘 일정 요약, 📅 이번 주 일정 요약, ✅ 이번 주 액션아이템.
   누르면 features.py 의 함수를 바로 호출하고 결과를 채팅 탭에 대화처럼 추가한다.
2) '📅 일정' 탭: st.date_input 으로 날짜를 고르면 그날 일정 파일 내용을 AI 없이 그대로 보여주고,
   '🤖 이 날 일정 AI 요약' 버튼을 누를 때만 summarize_schedule 을 호출한다. 파일이 없으면 st.info 로 안내.
```
> 💡 "AI 없이 보여줄 수 있는 건 AI를 안 부른다" = 빠르고, 공짜고, 정확합니다.

## 프롬프트 6-4. 액션아이템 탭 + 문서 보기 탭 (10분)
```
1) '✅ 액션아이템' 탭: 시작일·종료일 date_input 2칸(기본값 이번 주 월~일), 담당자 text_input,
   '액션아이템 추출' 버튼 → extract_action_items 결과를 st.dataframe 표로 보여주고,
   그 아래 CSV 다운로드 버튼(utf-8-sig). 결과는 session_state 에 저장해서 다른 버튼을 눌러도 유지.
   주의: session_state 의 키 이름으로 'items' 는 쓰지 마 (내장 메서드 이름과 겹침).
2) '📁 문서 보기' 탭: 종류 라디오(전체/일정/회의록/보고서/미분류) + 문서 selectbox → 내용 표시.
   .md 는 st.markdown, 나머지는 st.text 로.
```

## 프롬프트 6-5. 배포 대비 안전장치 (5분)
```
my_app.py 를 다른 사람에게 링크로 공유할 거야. 아래 안전장치를 추가해줘.
1) 비밀번호 화면: config.APP_PASSWORD 가 비어 있지 않으면, 맞는 비밀번호를 넣기 전까지 본 화면을 보여주지 않는다.
   st.form + type="password", 비교는 hmac.compare_digest, 통과하면 session_state 에 기록, 아니면 st.stop().
2) 사용 한도: AI를 부를 때마다 횟수를 세서 config.MAX_QUESTIONS 를 넘으면 경고만 보여주고 호출하지 않는다.
   사이드바에 st.progress 로 'AI 사용 n/최대회' 표시.
3) .streamlit/config.toml 의 primaryColor 를 우리 팀 색으로 바꿔줘.
```
✅ 확인: `.env` 에 `APP_PASSWORD=1234` 를 넣고 다시 실행 → 비밀번호 화면이 먼저 나옴

## 🧪 화면 점검표 (2교시 끝)
| 확인 | 기대 |
|---|---|
| 숫자 카드 | 3건 / 3건 / 21개 / 1개 |
| 이어지는 질문 | "이번 주 액션아이템" → "그중에 박민수 것만" 이 이어짐 |
| 일정 탭 | 10/21 선택 → 인플루언서 에이전시 미팅 |
| 액션아이템 탭 | 표 + CSV 다운로드, 엑셀에서 한글 정상 |
| 비밀번호 | 틀리면 "비밀번호가 틀렸습니다" |

## 🛠 막혔을 때
```
버튼을 누르면 앞에서 만든 표가 사라져. streamlit 의 rerun 때문인 것 같은데,
session_state 로 결과를 유지하도록 고쳐줘. 왜 사라졌는지도 한 줄로 설명해줘.
```
```
ValueError: DataFrame constructor not properly called! 에러가 나. 원인을 찾아서 고쳐줘.
(힌트가 필요하면: session_state.items 는 dict 의 items() 메서드와 이름이 겹친다)
```
