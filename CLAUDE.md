# 프로젝트: 내 파일을 읽는 AI 업무 Agent

## 목적
`업무폴더/`의 일정·회의록·보고서를 읽고 질문에 답하는 개인 업무 Agent를 만든다.
사용자는 코딩 초보자다. 코드는 짧고 읽기 쉽게, 주석은 한국어로 쓴다.

## 기술 스택
- Python 3.10+, 표준 라이브러리 우선
- LLM: OpenRouter (OpenAI 호환) → `openai` 패키지, `base_url=https://openrouter.ai/api/v1`
- 설정: `.env` (OPENROUTER_API_KEY, LLM_MODEL, AGENT_TODAY, WORK_DIR) → `python-dotenv`
- Word 읽기: `python-docx` / 웹 화면: `streamlit`

## 폴더 규칙 (반드시 지킬 것)
- 업무폴더 구조: `업무폴더/일정/`, `업무폴더/회의록/`, `업무폴더/보고서/`, `업무폴더/미분류/`
- 파일명 날짜 규칙: `YYYY-MM-DD_제목` (하루), `YYYY-MM_제목` (한 달), `YYYY-Q1_제목` (분기)
- 날짜가 없는 파일은 수정일을 날짜로 사용한다.
- 내가 만드는 코드는 `my_agent/` 폴더에 둔다.
- `solution/` 은 실습 정답 코드다. 사용자가 직접 요청하기 전에는 읽지도, 참고하지도, 복사하지도 않는다.
- `my_agent/` 의 프로그램은 키트 최상위 폴더에서 `python my_agent/파일명.py` 로 실행된다.
- 결과 파일(CSV 등)은 `output/` 에 저장하고 엑셀 호환을 위해 `utf-8-sig` 로 저장한다.

## 코딩 원칙
- 날짜 계산은 LLM에게 맡기지 않고 파이썬 코드(`date_utils.py`)로 한다.
- LLM에게는 "문서에 있는 내용만 근거로 답하고, 출처 파일명을 적어라"를 항상 지시한다.
- '오늘'은 `AGENT_TODAY` 환경변수가 있으면 그 날짜, 없으면 실제 오늘.
- 한 파일은 150줄 이내. 함수마다 한 줄 설명 주석.
- 새 기능을 만들면 실행 방법을 README에 한 줄 추가한다.

## 2부: 웹 화면·배포 규칙
- 웹 앱은 키트 최상위의 `my_app.py` (정답: `streamlit_app.py`). solution/ 모듈을 sys.path 로 import 해서 재사용한다.
- 설정값은 config.py 를 통해서만 읽는다 (로컬은 .env, 배포 서버는 Streamlit Secrets → 환경변수).
- API 키·비밀번호를 코드, 문서, 커밋에 절대 적지 않는다. 커밋 전에 git status 로 .env 가 없는지 확인한다.
- 서버는 리눅스다. 경로는 pathlib 로 만들고 윈도우 전용 경로(C:\, 역슬래시)를 쓰지 않는다.
- session_state 키 이름으로 items, keys, values, get 처럼 dict 메서드와 같은 이름을 쓰지 않는다.
- AI 없이 보여줄 수 있는 정보(파일 내용, 개수)는 AI를 호출하지 않는다.

- `streamlit_app.py` 는 2부 정답 파일이다. 사용자가 직접 요청하기 전에는 읽지도, 참고하지도, 복사하지도 않는다.