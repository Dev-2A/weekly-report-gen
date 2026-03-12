import re
from src.config import Config
from src.notion.client import NotionClient


class NotionUploader:
    """
    Markdown 리포트를 Notion 페이지로 변환하여 업로드하는 모듈.
    md-notion-bridge 경험을 바탕으로 핵심 변환 로직만 경량 구현.
    """
    
    def __init__(self, config: Config):
        self.notion = NotionClient(config)
    
    def upload(self, report_text: str, week_label: str) -> str:
        """
        Markdown 리포트를 Notion 페이지로 업로드합니다.
        
        Args:
            report_text: LLM이 생성한 Markdown 회고 리포트
            week_label: 주차 레이블 (페이지 제목으로 사용)
        
        Returns:
            생성된 Notion 페이지 URL
        """
        title = f"📋 주간 회고 — {week_label}"
        
        # Markdown 주석(<!-- -->) 제거
        clean_text = re.sub(r"<!--.*?-->", "", report_text, flags=re.DOTALL).strip()
        
        blocks = markdown_to_notion_blocks(clean_text)
        
        print(f"📤 Notion 업로드 중... (블록 수: {len(blocks)})")
        url = self.notion.create_report_page(title=title, blocks=blocks)
        print(f"✅ Notion 업로드 완료: {url}")

        return url


# ── Markdown → Notion 블록 변환 ───────────────────────────────


def markdown_to_notion_blocks(markdown: str) -> list[dict]:
    """
    Markdown 텍스트를 Notion 블록 리스트로 변환합니다.

    지원 문법:
        # ~ ###  → heading_1 ~ heading_3
        - / * / + → bulleted_list_item
        1. 2. ... → numbered_list_item
        ---       → divider
        빈 줄     → 단락 구분
        일반 텍스트 → paragraph
    """
    blocks = []
    lines = markdown.splitlines()
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 빈 줄 → 스킵
        if not stripped:
            i += 1
            continue
        
        # 구분선
        if re.match(r"^-{3,}$", stripped):
            blocks.append(_divider())
            i += 1
            continue
        
        # Heading 1
        if stripped.startswith("# ") and not stripped.startswith("## "):
            text = stripped[2:].strip()
            blocks.append(_heading(1, text))
            i += 1
            continue

        # Heading 2
        if stripped.startswith("## ") and not stripped.startswith("### "):
            text = stripped[3:].strip()
            blocks.append(_heading(2, text))
            i += 1
            continue

        # Heading 3
        if stripped.startswith("### "):
            text = stripped[4:].strip()
            blocks.append(_heading(3, text))
            i += 1
            continue

        # 번호 목록 (1. 2. ...)
        if re.match(r"^\d+\.\s", stripped):
            text = re.sub(r"^\d+\.\s+", "", stripped)
            blocks.append(_numbered_list(text))
            i += 1
            continue

        # 글머리 목록 (- * +)
        if re.match(r"^[-*+]\s", stripped):
            text = stripped[2:].strip()
            blocks.append(_bulleted_list(text))
            i += 1
            continue

        # 일반 단락
        blocks.append(_paragraph(stripped))
        i += 1

    return blocks


# ── 블록 생성 헬퍼 ────────────────────────────────────────────


def _rich_text(content: str) -> list[dict]:
    """인라인 볼드/이탤릭 마크업을 Notion rich_text로 변환합니다."""
    parts = []
    # **볼드** 처리
    segments = re.split(r"(\*\*.*?\*\*)", content)

    for seg in segments:
        if seg.startswith("**") and seg.endswith("**"):
            parts.append({
                "type": "text",
                "text": {"content": seg[2:-2]},
                "annotations": {"bold": True},
            })
        else:
            if seg:
                parts.append({
                    "type": "text",
                    "text": {"content": seg},
                    "annotations": {"bold": False},
                })

    return parts or [{"type": "text", "text": {"content": content}}]


def _heading(level: int, text: str) -> dict:
    type_map = {1: "heading_1", 2: "heading_2", 3: "heading_3"}
    return {
        "object": "block",
        "type": type_map[level],
        type_map[level]: {"rich_text": _rich_text(text)},
    }


def _paragraph(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": _rich_text(text)},
    }


def _bulleted_list(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": _rich_text(text)},
    }


def _numbered_list(text: str) -> dict:
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": _rich_text(text)},
    }


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}