# 내 Agent에 화면 입히고 링크로 공유하기 — 2부 실습 키트
(1부 "내 파일을 읽는 AI Agent" 키트 + 웹 화면·배포 실습 추가)

## 2부 빠른 시작
```bash
pip install -r requirements-dev.txt
cp .env.example .env            # Windows: copy .env.example .env  → OPENROUTER_API_KEY 입력
python check_setup.py
streamlit run streamlit_app.py  # 완성본 미리 보기
streamlit run my_app.py         # 내 화면 뼈대 (상단 숫자 4칸 + 탭 4개)
```

| 교시 | 프롬프트 | 내가 만드는 것 | 정답·예제 |
|---|---|---|---|
| 1 | `prompts/05_Streamlit기초.md` | 미니 과제 (my_agent/) | `basics/01~07` |
| 2 | `prompts/06_내Agent에화면입히기.md` | `my_app.py` | `streamlit_app.py` |
| 3 | `prompts/07_링크로공유하기.md` | GitHub 저장소 + 배포 링크 | `.streamlit/secrets.toml.example` |
| 4 | `prompts/08_핵심개념정리_QnA.md` | — | `streamlit_치트시트.png` |

배포용 파일: `requirements.txt`(서버 설치 목록) · `.gitignore`(.env 제외) · `.streamlit/config.toml`(테마)
자동 테스트: `python -m pytest tests -q` (API 키 없이 웹 앱 버튼·비밀번호·사용 한도까지 확인)

---
# (참고) 1부 안내

## 0. 세팅 (오리엔테이션 20분)
```bash
pip install -r requirements-dev.txt
cp .env.example .env          # Windows: copy .env.example .env
# .env 를 열어 OPENROUTER_API_KEY 입력
python check_setup.py         # 모두 ✅ 이면 준비 완료
```
- 강의 날짜와 상관없이 `.env` 의 `AGENT_TODAY=2026-10-30` 을 그대로 두세요. 질문테스트시트의 기대 답이 이 날짜 기준입니다.
  (`--base` 로 기준일을 바꾸면 보고서의 월·분기 표기와 테스트시트 정답이 맞지 않게 됩니다)
- 압축을 풀었더니 `미분류` 파일 날짜가 이상하면 `python tools/make_sample_data.py` 를 한 번 다시 실행

## 1. 실습 순서
| 교시 | 프롬프트 | 내가 만드는 파일 (`my_agent/`) | 정답 실행 |
|---|---|---|---|
| 1 | `prompts/01_내파일을읽는AI.md` | config, llm, file_loader, step1 | `python solution/step1_file_reader.py` |
| 2 | `prompts/02_날짜별파일자동인식.md` | date_utils, finder, step2 | `python solution/step2_date_finder.py` |
| 3 | `prompts/03_Agent핵심기능.md` | features, step3_agent | `python solution/step3_agent.py` |
| 4 | `prompts/04_통합과미션.md` | step4_app | `streamlit run solution/step4_app.py` |

- 시스템 프롬프트 원문: `prompts/agent_system_prompts.md`
- 검증용 20문항: `질문테스트시트.md`
- 자동 테스트 (API 키 없이 동작): `python -m pytest tests -q`

## 2. 업무폴더 (가상 회사: 그린팜 마케팅팀, 기준일 2026-10-30 금)
```
업무폴더/
├── 일정/     2026-10-19 ~ 2026-11-02 평일 일정 11개 (박민수 대리)
├── 회의록/   주간회의 ×2, 캠페인기획회의, 마케팅회의, 고객사미팅(.docx)
├── 보고서/   2026-09 월간, 2026-Q3 분기, 주간성과, 10월 채널별 일일성과(.csv)
└── 미분류/   회의메모_최종_진짜최종.txt  ← 이름 규칙을 안 지킨 파일 (토론용)
```
파일명 날짜 규칙: `YYYY-MM-DD_제목` · `YYYY-MM_제목` · `YYYY-Q3_제목`

## 3. 자주 나는 문제
| 증상 | 해결 |
|---|---|
| `401` / `No auth credentials` | `.env` 파일 이름 확인(.env.txt 아님), 키 앞뒤 공백 제거 |
| `402` / 크레딧 부족 | OpenRouter 크레딧 충전 또는 `LLM_MODEL` 을 무료 모델로 변경 (단, 도구 호출 지원 여부 확인) |
| Agent가 도구를 안 씀 | 도구 호출(tools) 지원 모델인지 확인. `openai/gpt-4o-mini` 권장 |
| "오늘 일정"이 엉뚱함 | `.env` 의 `AGENT_TODAY` 와 업무폴더 기준일이 같은지 확인 |
| 엑셀에서 CSV 한글 깨짐 | `utf-8-sig` 로 저장했는지 확인 |
| `ModuleNotFoundError` | 키트 최상위 폴더에서 실행했는지 확인 |
