# 2부 1교시 — Streamlit 기초

목표: "파이썬 한 줄 = 화면 요소 하나" 감각 익히기, 그리고 **다시 실행(rerun)과 session_state** 이해하기
예제: `basics/01 ~ 07` (모두 `streamlit run basics/파일명.py` 로 실행, 종료는 터미널에서 Ctrl+C)

| 순서 | 예제 | 배우는 것 | 시간 |
|---|---|---|---|
| 1 | 01_hello.py | title, header, write, markdown, info/success/warning | 5분 |
| 2 | 02_input.py | text_input, selectbox, date_input, slider, button | 7분 |
| 3 | 03_rerun_state.py ★ | 버튼 누르면 파일 전체가 다시 실행됨 → session_state | 10분 |
| 4 | 04_layout.py | set_page_config, sidebar, columns, metric, tabs, expander | 7분 |
| 5 | 05_data.py | dataframe, line_chart, download_button | 6분 |
| 6 | 06_chat.py | chat_message, chat_input, 대화 기록 | 5분 |
| 7 | 07_llm_chat.py | 1부의 llm.py 연결 → 진짜 AI 채팅 | 5분 |

> 💡 꿀팁: 실행 중에 코드를 고치고 저장하면 브라우저 오른쪽 위에 **Rerun** 버튼이 뜹니다.
> **Always rerun** 을 누르면 저장할 때마다 화면이 자동으로 바뀝니다.

---

## 프롬프트 5-1. 예제 이해하기 (Claude Code)
```
basics/03_rerun_state.py 를 읽고, 비전공자에게 설명하듯이 알려줘.
1. 일반 변수 count 가 왜 1 이상 안 올라가는지 '파일이 위에서부터 다시 실행된다'는 말로 설명
2. session_state 를 일상생활 비유 하나로 설명
3. 이 원리를 모르면 채팅 앱을 만들 때 어떤 문제가 생기는지 한 줄로
```

## 미니 과제 (각 5분, 하나 골라서)
과제 A — 인사 카드
```
basics/02_input.py 를 복사해서 my_agent/a_greeting.py 를 만들어줘.
'인사하기' 버튼을 누르면 st.success 상자 안에 인사말을 보여주고,
선택한 팀이 '마케팅팀'이면 st.balloons() 도 터지게 해줘.
```
과제 B — 방문 카운터
```
my_agent/b_counter.py 를 만들어줘. '좋아요' 버튼을 누를 때마다 숫자가 1씩 올라가고,
10이 넘으면 "인기 폭발!" 경고 상자를 보여줘. 숫자는 session_state 로 기억해.
'초기화' 버튼도 만들어줘.
```
과제 C — 채널 대시보드
```
basics/05_data.py 를 참고해서 my_agent/c_dashboard.py 를 만들어줘.
업무폴더/보고서/2026-10_채널별일일성과.csv 를 읽어서
위에는 채널별 총 광고비·총 클릭·총 전환을 st.metric 3칸으로,
아래에는 채널별 일일 전환 수를 st.bar_chart 로 보여줘.
```

## 🛠 막혔을 때
```
streamlit run 을 했는데 브라우저에 아무것도 안 떠. 터미널 메시지는 아래와 같아. 원인과 해결 방법을 알려줘.
(터미널 메시지 붙여넣기)
```
