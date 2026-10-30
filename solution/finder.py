"""2교시: 날짜/종류 조건으로 업무 파일 찾기 (Agent 의 '도구'로도 재사용)"""
from datetime import date

from date_utils import file_date_range, overlaps
from file_loader import WorkFile, list_files, modified_date


def indexed_files() -> list[WorkFile]:
    """모든 파일에 기간(start~end)을 붙임. 파일명에 날짜가 없으면 수정일로 대체."""
    files = list_files()
    for f in files:
        rng = file_date_range(f.name)
        if rng is None:
            d = modified_date(f.path)
            rng = (d, d)
        f.start, f.end = rng
    return files


def find_files(start: date | None = None, end: date | None = None,
               category: str | None = None) -> list[WorkFile]:
    result = []
    for f in indexed_files():
        if category and f.category != category:
            continue
        if start and end and not overlaps(f.start, f.end, start, end):
            continue
        result.append(f)
    return result
