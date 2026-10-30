"""
질문테스트시트.md 의 20문항을 Agent에 자동으로 넣고, 결과를 한 파일로 모아 줍니다.
실행: python tools/run_test_sheet.py            (전체)
      python tools/run_test_sheet.py 5 11 15    (특정 번호만)
결과: output/테스트결과_날짜시각.md  → 기대 답과 나란히 보면서 O/X 채점
"""
import re
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "solution"))

import config  # noqa: E402
from step3_agent import Agent  # noqa: E402


def load_questions():
    rows = []
    for line in (ROOT / "질문테스트시트.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", line)
        if m:
            rows.append({"no": int(m[1]), "area": m[2], "q": m[3], "expected": m[4]})
    return rows


def main():
    only = {int(a) for a in sys.argv[1:] if a.isdigit()}
    questions = [q for q in load_questions() if not only or q["no"] in only]
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    out = config.OUTPUT_DIR / f"테스트결과_{datetime.now():%Y%m%d_%H%M}.md"
    lines = [f"# 테스트 결과 ({config.MODEL}, 기준일 {config.today()})\n"]

    for i, q in enumerate(questions, 1):
        print(f"[{i:>2}/{len(questions)}] {q['no']}번 {q['q']}", flush=True)
        agent = Agent(verbose=False)          # 문항끼리 섞이지 않게 매번 새 Agent
        t0 = time.time()
        try:
            answer = agent.ask(q["q"])
        except Exception as e:  # noqa: BLE001
            answer = f"❌ 에러: {e}"
        sec = time.time() - t0
        tools = " → ".join(t.replace("🔧 ", "") for t in agent.trace) or "(도구 사용 없음)"
        lines += [f"## {q['no']}. [{q['area']}] {q['q']}",
                  f"- **기대 답**: {q['expected']}",
                  f"- **사용 도구**: {tools}",
                  f"- **소요**: {sec:.1f}초",
                  f"- **채점**: ☐ O  ☐ X\n",
                  answer.strip(), "\n---\n"]
        out.write_text("\n".join(lines), encoding="utf-8")   # 중간에 끊겨도 저장되도록 매번 기록

    print(f"\n✅ 완료: {out}")


if __name__ == "__main__":
    main()
