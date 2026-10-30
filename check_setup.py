"""
세팅 확인 스크립트 (오리엔테이션)
실행: python check_setup.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))

ok = True
print("1) 파이썬 버전:", sys.version.split()[0], "✅" if sys.version_info >= (3, 10) else "❌ 3.10 이상 필요")

for pkg in ("openai", "dotenv", "docx", "streamlit"):
    try:
        __import__(pkg)
        print(f"2) 패키지 {pkg:<10} ✅")
    except ImportError:
        ok = False
        print(f"2) 패키지 {pkg:<10} ❌  →  pip install -r requirements.txt")

import config  # noqa: E402

print("3) 업무폴더:", config.WORK_DIR, "✅" if config.WORK_DIR.exists() else "❌ (python tools/make_sample_data.py 실행)")
print("4) 기준일(오늘):", config.today())
if not config.API_KEY:
    ok = False
    print("5) API 키 ❌  →  .env.example 을 .env 로 복사하고 OPENROUTER_API_KEY 입력")
else:
    try:
        import llm
        reply = llm.ask("한 단어로만 답해.", "준비됐으면 '준비완료'라고 말해줘.")
        print(f"5) LLM 연결 ✅ ({config.MODEL}) → {reply.strip()}")
    except Exception as e:  # noqa: BLE001
        ok = False
        print(f"5) LLM 연결 ❌ → {e}")

print("\n🎉 모든 준비 완료!" if ok else "\n⚠️ 위의 ❌ 항목을 해결해 주세요.")
