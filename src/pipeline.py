from src.config import Config, load_config
from src.notion import NotionClient, NotionUploader, parse_task
from src.llm import ReportGenerator
from src.report import (
    get_week_range,
    get_week_label,
    preprocess_tasks,
    normalize_tasks,
    MarkdownRenderer,
    ReportSummary,
)


class WeeklyReportPipeline:
    """
    Notion DB 읽기 → 전처리 → LLM 생성 → Markdown 저장 → Notion 업로드
    전체 파이프라인을 조율하는 클래스
    """
    
    def __init__(self, config: Config | None = None):
        self.config = config or load_config()
        self.notion_client = NotionClient(self.config)
        self.generator = ReportGenerator(self.config)
        self.renderer = MarkdownRenderer(self.config.output_dir)
        self.uploader = NotionUploader(self.config)
    
    def run(
        self,
        week_offset: int = 1,
        save_markdown: bool = True,
        upload_notion: bool = True,
        dry_run: bool = False,
    ) -> dict:
        """
        파이프라인을 실행합니다.

        Args:
            week_offset:    0 = 이번 주, 1 = 지난주 (기본값), 2 = 2주 전 ...
            save_markdown:  Markdown 파일 저장 여부 (기본 True)
            upload_notion:  Notion 업로드 여부 (기본 True)
            dry_run:        True면 LLM 호출 / 업로드 없이 전처리 결과만 출력

        Returns:
            {
                "week_label": str,
                "task_count": int,
                "markdown_path": str | None,
                "notion_url": str | None,
                "report_text": str | None,
            }
        """
        result = {
            "week_label": None,
            "task_count": 0,
            "markdown_path": None,
            "notion_url": None,
            "report_text": None,
        }
        
        # ── Step 1. 날짜 계산 ──────────────────────────────────
        start_date, end_date = get_week_range(offset=week_offset)
        week_label = get_week_label(start_date)
        result["week_label"] = week_label
        
        print(f"\n{'='*60}")
        print(f"  📅 대상 주차: {week_label}")
        print(f"  📆 기간: {start_date} ~ {end_date}")
        print(f"{'='*60}\n")
        
        # ── Step 2. Notion DB에서 작업 기록 수집 ────────────────
        print("📥 Notion DB에서 작업 기록 수집 중...")
        raw_pages = self.notion_client.fetch_weekly_tasks(start_date, end_date)
        
        if not raw_pages:
            print(f"⚠️  {week_label} 기간에 작업 기록이 없습니다. 파이프라인을 종료합니다.")
            return result

        # ── Step 3. 전처리 + 정규화 ────────────────────────────
        print("⚙️  작업 기록 전처리 중...")
        tasks = preprocess_tasks(raw_pages, parse_task)
        normalized = normalize_tasks(tasks)
        result["task_count"] = normalized["total"]
        
        print(f"✅ 작업 기록 수집 완료: 총 {normalized['total']}개")
        print(f"   상태별: {', '.join(f'{k}({len(v)})' for k, v in normalized['by_status'].items())}")
        print(f"   태그별: {', '.join(f'{k}({len(v)})' for k, v in normalized['by_tag'].items())}")

        if dry_run:
            print("\n🔍 [Dry Run] 전처리 결과만 출력합니다.")
            print("\n" + normalized["summary_text"])
            return result
        
        # ── Step 4. LLM 회고 리포트 생성 ───────────────────────
        print("\n🤖 회고 리포트 생성 중...")
        report_text = self.generator.generate_with_retry(
            week_label=week_label,
            summary_text=normalized["summary_text"],
        )
        result["report_text"] = report_text
        
        # ── Step 5. Markdown 파일 저장 ──────────────────────────
        if save_markdown:
            filepath = self.renderer.save(
                report_text=report_text,
                week_label=week_label,
                start_date=start_date,
            )
            result["markdown_path"] = str(filepath)
        
        # ── Step 6. Notion 업로드 ───────────────────────────────
        if upload_notion:
            url = self.uploader.upload(
                report_text=report_text,
                week_label=week_label,
            )
            result["notion_url"] = url
        
        # ── 완료 요약 ───────────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"  🎉 파이프라인 완료!")
        print(f"  📋 주차: {week_label}")
        print(f"  📝 작업 수: {normalized['total']}개")
        if result["markdown_path"]:
            print(f"  📄 저장 경로: {result['markdown_path']}")
        if result["notion_url"]:
            print(f"  🔗 Notion URL: {result['notion_url']}")
        print(f"{'='*60}\n")

        return result