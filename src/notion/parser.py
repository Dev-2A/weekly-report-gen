from datetime import datetime


def parse_task(page: dict) -> dict | None:
    """
    Notion 페이지 객체를 작업 딕셔너리로 파싱합니다.
    DB 속성명은 본인 Notion DB에 맞게 수정할 것.
    
    Args:
        page: Notion API가 반환한 페이지 객체
    
    Returns:
        파싱된 작업 딕셔너리, 파싱 실패 시 None
    """
    try:
        props = page["properties"]
        
        # 제목
        title_prop = props.get("이름") or props.get("Name") or props.get("제목")
        title = _extract_title(title_prop)
        
        # 날짜
        date_prop = props.get("날짜") or props.get("Date")
        date = _extract_date(date_prop)
        
        # 상태
        status_prop = props.get("상태") or props.get("Status")
        status = _extract_select(status_prop)
        
        # 태그/카테고리
        tags_prop = props.get("태그") or props.get("Tags") or props.get("카테고리")
        tags = _extract_multi_select(tags_prop)
        
        # 메모
        memo_prop = props.get("메모") or props.get("Note") or props.get("내용")
        memo = _extract_rich_text(memo_prop)
        
        return {
            "id": page["id"],
            "title": title,
            "date": date,
            "status": status,
            "tags": tags,
            "memo": memo,
            "url": page.get("url", ""),
        }
    
    except Exception as e:
        print(f"⚠️  페이지 파싱 실패 ({page.get('id', 'unknown')}): {e}")
        return None


# ── 속성 추출 헬퍼 ──────────────────────────────────────────


def _extract_title(prop: dict | None) -> str:
    if not prop:
        return "제목 없음"
    texts = prop.get("title", [])
    return "".join(t.get("plain_text", "") for t in texts) or "제목 없음"


def _extract_date(prop: dict | None) -> str:
    if not prop:
        return ""
    date_obj = prop.get("date")
    if not date_obj:
        return ""
    return date_obj.get("start", "")


def _extract_select(prop: dict | None) -> str:
    if not prop:
        return ""
    select = prop.get("select")
    return select.get("name", "") if select else ""


def _extract_multi_select(prop: dict | None) -> list[str]:
    if not prop:
        return []
    return [opt.get("name", "") for opt in prop.get("multi_select", [])]


def _extract_rich_text(prop: dict | None) -> str:
    if not prop:
        return ""
    texts = prop.get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in texts)