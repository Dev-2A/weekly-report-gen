import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Notion
    notion_token: str
    notion_database_id: str
    notion_report_parent_id: str    # 리포트를 업로드할 Notion 페이지 ID
    
    # LLM
    anthropic_api_key: str
    llm_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    
    # Report
    report_language: str = "ko"
    output_dir: str = "output"


def load_config() -> Config:
    """환경 변수에서 설정을 불러옵니다."""
    required = [
        "NOTION_TOKEN",
        "NOTION_DATABASE_ID",
        "NOTION_REPORT_PARENT_ID",
        "ANTHROPIC_API_KEY",
    ]
    
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise EnvironmentError(
            f"필수 환경 변수가 설정되지 않았습니다: {', '.join(missing)}\n"
            f".env 파일을 확인해주세요."
        )
    
    return Config(
        notion_token=os.getenv("NOTION_TOKEN"),
        notion_database_id=os.getenv("NOTION_DATABASE_ID"),
        notion_report_parent_id=os.getenv("NOTION_REPORT_PARENT_ID"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        llm_model=os.getenv("LLM_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
        report_language=os.getenv("REPORT_LANGUAGE", "ko"),
        output_dir=os.getenv("OUTPUT_DIR", "output"),
    )