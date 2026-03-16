from notion_client import Client
from src.config import Config


class NotionClient:
    """Notion API 클라이언트 래퍼"""
    
    def __init__(self, config: Config):
        self.client = Client(auth=config.notion_token)
        self.database_id = config.notion_database_id
        self.report_parent_id = config.notion_report_parent_id
    
    def fetch_weekly_tasks(self, start_date: str, end_date: str) -> list[dict]:
        """
        지정된 기간의 작업 기록을 Notion DB에서 가져옵니다.
        
        Args:
            start_date: 조회 시작일 (YYYY-MM-DD)
            end_date: 조회 종료일 (YYYY-MM-DD)
        
        Returns:
            작업 기록 딕셔너리 리스트
        """
        results = []
        has_more = True
        next_cursor = None
        
        while has_more:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "and": [
                        {
                            "property": "Date",
                            "date": {"on_or_after": start_date},
                        },
                        {
                            "property": "Date",
                            "date": {"on_or_before": end_date},
                        },
                    ]
                },
                sorts=[{"property": "Date", "direction": "ascending"}],
                start_cursor=next_cursor,
            )
            
            results.extend(response["results"])
            has_more = response["has_more"]
            next_cursor = response.get("next_cursor")
        
        return results
    
    def create_report_page(self, title: str, blocks: list[dict]) -> str:
        """
        Notion에 리포트 페이지를 생성합니다.
        
        Args:
            title: 페이지 제목
            blocks: Notion 블록 리스트
        
        Returns:
            생성된 페이지 URL
        """
        response = self.client.pages.create(
            parent={"page_id": self.report_parent_id},
            properties={
                "title": {
                    "title": [{"type": "text", "text": {"content": title}}]
                }
            },
            children=blocks[:100],  # Notion API 1회 최대 100블록 제한
        )
        
        page_id = response["id"]
        
        # 100블록 초과 시 추가 append
        if len(blocks) > 100:
            for i in range(100, len(blocks), 100):
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=blocks[i:i + 100],
                )
        
        return response["url"]