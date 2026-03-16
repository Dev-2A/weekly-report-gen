from datetime import datetime, timedelta
from collections import defaultdict


def get_week_range(offset: int = 0) -> tuple[str, str]:
    """
    이번 주(또는 n주 전)의 월요일~일요일 날짜를 반환합니다.
    
    Args:
        offset: 0 = 이번 주, 1 = 지난주, 2 = 2주 전 ...
    
    Returns:
        (start_date, end_date) 형식의 YYYY-MM-DD 문자열 튜플
    """
    today = datetime.today()
    monday = today - timedelta(days=today.weekday()) - timedelta(weeks=offset)
    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


def get_week_label(start_date: str) -> str:
    """
    주차 레이블을 생성합니다.
    예: '2026년 10주차 (03/02 ~ 03/08)'
    
    Args:
        start_date: 주의 시작일 (YYYY-MM-DD)
    
    Returns:
        주차 레이블 문자열
    """
    dt = datetime.strptime(start_date, "%Y-%m-%d")
    week_num = dt.isocalendar()[1]
    end_dt = dt + timedelta(days=6)
    return (
        f"{dt.year}년 {week_num}주차 "
        f"({dt.strftime('%m/%d')} ~ {end_dt.strftime('%m/%d')})"
    )


def preprocess_tasks(raw_pages: list[dict], parser_fn) -> list[dict]:
    """
    Notion 페이지 목록을 파싱 + 필터링합니다.
    
    Args:
        raw_pages: Notion API 응답의 페이지 객체 리스트
        parse_fn: 페이지 객체 → 작업 딕셔너리 변환 함수
    
    Returns:
        유효한 작업 딕셔너리 리스트
    """
    tasks = [parser_fn(page) for page in raw_pages]
    tasks = [t for t in tasks if t is not None]
    tasks = [t for t in tasks if t.get("title") != "제목 없음"]
    tasks.sort(key=lambda t: t.get("date") or "")
    return tasks


def normalize_tasks(tasks: list[dict]) -> dict:
    """"
    작업 리스트를 LLM 프롬프트에 활용하기 좋은 구조로 정규화합니다.
    
    Returns:
        {
            "total": int,
            "by_status": {"완료": [...], "진행중": [...], ...},
            "by_tag": {"개발": [...], "회의": [...], ...},
            "by_date": {"2026-03-02": [...], ...},
            "summary_text": str ← LLM에 넘길 텍스트 요약
        }
    """
    by_status = defaultdict(list)
    by_tag = defaultdict(list)
    by_date = defaultdict(list)
    
    for task in tasks:
        status = task.get("status") or "미분류"
        by_status[status].append(task)
        
        for tag in task.get("tags") or ["태그없음"]:
            by_tag[tag].append(task)
        
        date = task.get("date") or "날짜없음"
        by_date[date].append(task)
    
    return {
        "total": len(tasks),
        "by_status": dict(by_status),
        "by_tag": dict(by_tag),
        "by_date": dict(by_date),
        "summary_text": _build_summary_text(tasks, by_status, by_tag),
    }


def _build_summary_text(
    tasks: list[dict],
    by_status: dict,
    by_tag: dict,
) -> str:
    """
    LLM 프롬프트에 삽입할 작업 요약 텍스트를 생성합니다.
    """
    lines = []
    
    lines.append(f"## 전체 작업 수: {len(tasks)}개\n")
    
    # 상태별 요약
    lines.append("### 상태별 현황")
    for status, items in by_status.items():
        lines.append(f"- {status}: {len(items)}개")
    lines.append("")
    
    # 태그별 요약
    lines.append("### 태그별 현황")
    for tag, items in by_tag.items():
        lines.append(f"- {tag}: {len(items)}개")
    lines.append("")
    
    # 작업 목록 (날짜순)
    lines.append("### 작업 목록")
    for task in tasks:
        date = task.get("date") or ""
        title = task.get("title") or ""
        status = task.get("status") or ""
        tags = ", ".join(task.get("tags") or [])
        memo = task.get("memo") or ""
        
        line = f"- [{date}] {title}"
        if status:
            line += f" | 상태: {status}"
        if tags:
            line += f" | 태그: {tags}"
        if memo:
            line += f"\n 메모: {memo}"
        lines.append(line)
    
    return "\n".join(lines)