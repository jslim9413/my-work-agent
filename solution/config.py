"""공통 설정: .env 를 읽어서 API 키, 모델, 업무폴더 경로, '오늘' 날짜를 제공합니다."""
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

KIT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(KIT_ROOT / ".env")                      # 내 PC: .env 파일에서 읽기


def _load_streamlit_secrets():
    """배포 서버: Streamlit Cloud 의 Secrets 값을 환경변수로 옮겨 담기 (없으면 조용히 넘어감)"""
    try:
        import streamlit as st
        for key, value in st.secrets.items():
            if isinstance(value, (str, int, float)):
                os.environ.setdefault(key, str(value))
    except Exception:  # noqa: BLE001  secrets.toml 이 없으면 여기로 옴
        pass


_load_streamlit_secrets()

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

WORK_DIR = Path(os.getenv("WORK_DIR", KIT_ROOT / "업무폴더"))
OUTPUT_DIR = KIT_ROOT / "output"

# 실습 데이터가 특정 날짜 기준으로 만들어져 있으므로 '오늘'을 고정할 수 있게 함
# 기본값은 실습 데이터 기준일. AGENT_TODAY= (빈 값) 으로 두면 실제 오늘 날짜 사용
_today = os.getenv("AGENT_TODAY", "2026-10-30").strip()


# 배포용 설정 (Streamlit Cloud 의 Secrets 에 적으면 환경변수로도 읽힘)
APP_PASSWORD = os.getenv("APP_PASSWORD", "")          # 비워두면 비밀번호 없이 입장
MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS", "20"))  # 접속 1회당 질문 수 제한 (API 비용 보호)


def today() -> date:
    return date.fromisoformat(_today) if _today else date.today()
