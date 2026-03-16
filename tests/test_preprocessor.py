import pytest
from src.report.preprocessor import (
    get_week_range,
    get_week_label,
    preprocess_tasks,
    normalize_tasks,
)


# ── get_week_range ────────────────────────────────────────────


def test_get_week_range_returns_monday_to_sunday():
    start, end = get_week_range(offset=0)
    from datetime import datetime
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    assert start_dt.weekday() == 0       # 월요일
    assert end_dt.weekday() == 6         # 일요일
    assert (end_dt - start_dt).days == 6


def test_get_week_range_offset():
    start_this, _ = get_week_range(offset=0)
    start_last, _ = get_week_range(offset=1)
    from datetime import datetime, timedelta
    diff = datetime.strptime(start_this, "%Y-%m-%d") - \
           datetime.strptime(start_last, "%Y-%m-%d")
    assert diff.days == 7


# ── get_week_label ────────────────────────────────────────────


def test_get_week_label_format():
    label = get_week_label("2026-03-09")
    assert "2026년" in label
    assert "주차" in label
    assert "03/09" in label
    assert "03/15" in label


# ── preprocess_tasks ──────────────────────────────────────────


def _dummy_parser(page):
    return page  # 테스트용 패스스루 파서


def test_preprocess_tasks_filters_none():
    pages = [
        {"title": "작업 A", "date": "2026-03-09"},
        None,
        {"title": "제목 없음", "date": "2026-03-10"},
        {"title": "작업 B", "date": "2026-03-11"},
    ]

    def parser(p):
        return p  # None은 그대로 None 반환

    result = preprocess_tasks(pages, parser)
    titles = [t["title"] for t in result]

    assert None not in result
    assert "제목 없음" not in titles
    assert "작업 A" in titles
    assert "작업 B" in titles


def test_preprocess_tasks_sorted_by_date():
    pages = [
        {"title": "C", "date": "2026-03-11"},
        {"title": "A", "date": "2026-03-09"},
        {"title": "B", "date": "2026-03-10"},
    ]
    result = preprocess_tasks(pages, _dummy_parser)
    dates = [t["date"] for t in result]
    assert dates == sorted(dates)


# ── normalize_tasks ───────────────────────────────────────────


def test_normalize_tasks_structure():
    tasks = [
        {"title": "작업 A", "date": "2026-03-09", "status": "완료",
         "tags": ["개발"], "memo": ""},
        {"title": "작업 B", "date": "2026-03-10", "status": "완료",
         "tags": ["개발", "회의"], "memo": "메모"},
        {"title": "작업 C", "date": "2026-03-11", "status": "진행중",
         "tags": [], "memo": ""},
    ]
    result = normalize_tasks(tasks)

    assert result["total"] == 3
    assert "완료" in result["by_status"]
    assert "진행중" in result["by_status"]
    assert "개발" in result["by_tag"]
    assert "회의" in result["by_tag"]
    assert "태그없음" in result["by_tag"]
    assert isinstance(result["summary_text"], str)
    assert len(result["summary_text"]) > 0