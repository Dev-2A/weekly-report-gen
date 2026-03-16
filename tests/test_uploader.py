import pytest
from src.notion.uploader import markdown_to_notion_blocks


def test_heading1():
    blocks = markdown_to_notion_blocks("# 제목")
    assert len(blocks) == 1
    assert blocks[0]["type"] == "heading_1"


def test_heading2():
    blocks = markdown_to_notion_blocks("## 소제목")
    assert blocks[0]["type"] == "heading_2"


def test_heading3():
    blocks = markdown_to_notion_blocks("### 소소제목")
    assert blocks[0]["type"] == "heading_3"


def test_bulleted_list():
    blocks = markdown_to_notion_blocks("- 항목 A\n- 항목 B")
    assert all(b["type"] == "bulleted_list_item" for b in blocks)
    assert len(blocks) == 2


def test_numbered_list():
    blocks = markdown_to_notion_blocks("1. 첫째\n2. 둘째")
    assert all(b["type"] == "numbered_list_item" for b in blocks)


def test_divider():
    blocks = markdown_to_notion_blocks("---")
    assert blocks[0]["type"] == "divider"


def test_paragraph():
    blocks = markdown_to_notion_blocks("일반 텍스트 단락입니다.")
    assert blocks[0]["type"] == "paragraph"


def test_bold_inline():
    blocks = markdown_to_notion_blocks("**볼드** 텍스트")
    rich = blocks[0]["paragraph"]["rich_text"]
    bold_parts = [r for r in rich if r.get("annotations", {}).get("bold")]
    assert len(bold_parts) > 0


def test_empty_lines_skipped():
    blocks = markdown_to_notion_blocks("제목\n\n\n본문")
    assert len(blocks) == 2


def test_html_comment_stripped():
    import re
    text = "<!-- 주석 -->\n# 제목"
    clean = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).strip()
    blocks = markdown_to_notion_blocks(clean)
    assert blocks[0]["type"] == "heading_1"