"""LLM 호출을 한 곳에 모은 모듈 (OpenRouter = OpenAI 호환 API)"""
import json
import re

from openai import OpenAI

import config

_client = None


def client() -> OpenAI:
    global _client
    if _client is None:
        if not config.API_KEY:
            raise RuntimeError(".env 파일에 OPENROUTER_API_KEY 를 넣어주세요.")
        _client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)
    return _client


def ask(system: str, user: str, temperature: float = 0.2) -> str:
    """시스템 프롬프트 + 사용자 메시지 한 번으로 답을 받는 가장 단순한 호출"""
    res = client().chat.completions.create(
        model=config.MODEL,
        temperature=temperature,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
    )
    return res.choices[0].message.content or ""


def chat(messages: list, tools: list | None = None):
    """Agent 용: 대화 기록 + 도구 목록을 넘기고 message 객체를 그대로 돌려줌"""
    kwargs = dict(model=config.MODEL, temperature=0.2, messages=messages)
    if tools:
        kwargs["tools"] = tools
    return client().chat.completions.create(**kwargs).choices[0].message


def parse_json(text: str):
    """LLM 답변에서 JSON 부분만 꺼내기 (```json 코드블록 등 제거)"""
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    start = min([i for i in (text.find("["), text.find("{")) if i != -1], default=0)
    return json.loads(text[start:].strip())
