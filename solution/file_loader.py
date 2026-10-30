"""업무폴더의 파일을 찾고, 형식별로 텍스트를 읽어오는 모듈 (1교시)"""
import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import config

SUPPORTED = {".md", ".txt", ".csv", ".docx", ".pdf"}


@dataclass
class WorkFile:
    path: Path
    category: str            # 상위 폴더 이름: 일정 / 회의록 / 보고서 / 미분류
    start: date | None = None  # 파일이 다루는 기간 (2교시에서 채움)
    end: date | None = None

    @property
    def name(self) -> str:
        return self.path.name

    def rel(self) -> str:
        return str(self.path.relative_to(config.WORK_DIR))


def list_files(root: Path | None = None) -> list[WorkFile]:
    root = Path(root or config.WORK_DIR)
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED and not p.name.startswith(("~", ".")):
            category = p.parent.name if p.parent != root else "기타"
            files.append(WorkFile(path=p, category=category))
    return files


def read_text(path: Path, max_chars: int = 6000) -> str:
    """파일 형식에 맞게 텍스트로 변환. 너무 길면 잘라서 토큰 낭비를 막음."""
    path = Path(path)
    ext = path.suffix.lower()
    if ext in (".md", ".txt"):
        text = path.read_text(encoding="utf-8", errors="ignore")
    elif ext == ".csv":
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
            rows = list(csv.reader(f))
        text = "\n".join(" | ".join(r) for r in rows)
    elif ext == ".docx":
        from docx import Document
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        for t in doc.tables:
            for r in t.rows:
                text += "\n" + " | ".join(c.text for c in r.cells)
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return "(PDF를 읽으려면 pip install pypdf 가 필요합니다)"
        text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    else:
        return ""
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n...(이하 {len(text) - max_chars}자 생략)"
    return text


def modified_date(path: Path) -> date:
    return datetime.fromtimestamp(Path(path).stat().st_mtime).date()


def build_context(files: list[WorkFile], max_total: int = 40000) -> str:
    """여러 파일을 [파일명] 머리표와 함께 하나의 텍스트로 합침 → LLM에게 전달"""
    parts, total = [], 0
    for f in files:
        body = read_text(f.path)
        block = f"### [파일: {f.rel()}]\n{body}\n"
        if total + len(block) > max_total:
            parts.append(f"(용량 제한으로 {len(files) - len(parts)}개 파일 생략)")
            break
        parts.append(block)
        total += len(block)
    return "\n".join(parts)
