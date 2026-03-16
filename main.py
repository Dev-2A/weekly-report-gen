import click
from src.pipeline import WeeklyReportPipeline
from src.config import load_config
from src.report import ReportSummary, get_week_range, get_week_label


@click.group()
def cli():
    """🗒️ Weekly Report Generator — Notion 주간 회고 리포트 자동 생성기"""
    pass


# ── 1. generate: 리포트 생성 (핵심 커맨드) ─────────────────────


@cli.command
@click.option(
    "--week", "-w",
    default=1,
    show_default=True,
    help="몇 주 전 기록을 사용할지 지정. 0=이번주, 1=지난주(기본), 2=2주전...",
)
@click.option(
    "--no-markdown",
    is_flag=True,
    default=False,
    help="Markdown 파일 저장을 건너뜁니다.",
)
@click.option(
    "--no-upload",
    is_flag=True,
    default=False,
    help="Notion 업로드를 건너뜁니다.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="LLM 호출/업로드 없이 전처리 결과만 출력합니다.",
)
def generate(week, no_markdown, no_upload, dry_run):
    """Notion DB 작업 기록을 읽어 주간 회고 리포트를 생성합니다."""
    try:
        config = load_config()
        pipeline = WeeklyReportPipeline(config)
        
        pipeline.run(
            week_offset=week,
            save_markdown=not no_markdown,
            upload_notion=not no_upload,
            dry_run=dry_run,
        )
    
    except EnvironmentError as e:
        click.echo(f"\n❌ 환경 변수 오류:\n{e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"\n❌ 오류 발생: {e}", err=True)
        raise SystemExit(1)


# ── 2. list: 저장된 리포트 목록 조회 ───────────────────────────


@cli.command(name="list")
@click.option(
    "--output-dir", "-o",
    default="output",
    show_default=True,
    help="리포트가 저장된 디렉토리 경로",
)
def list_reports(output_dir):
    """저장된 Markdown 리포트 목록을 출력합니다."""
    summary = ReportSummary(output_dir)
    summary.print_list()


# ── 3. preview: 특정 주차 작업 기록 미리보기 ────────────────────


@cli.command()
@click.option(
    "--week", "-w",
    default=1,
    show_default=True,
    help="몇 주 전 기록을 미리볼지 지정.",
)
def preview(week):
    """LLLM 호출 없이 Notion 작업 기록 전처리 결과만 출력합니다. (dry-run 단축키)"""
    try:
        config = load_config()
        pipeline = WeeklyReportPipeline(config)
        
        pipeline.run(
            week_offset=week,
            save_markdown=False,
            upload_notion=False,
            dry_run=True,
        )
    
    except EnvironmentError as e:
        click.echo(f"\n❌ 환경 변수 오류:\n{e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"\n❌ 오류 발생: {e}", err=True)
        raise SystemExit(1)


# ── 4. info: 현재 설정 확인 ─────────────────────────────────────


@cli.command()
def info():
    """현재 환경 변수 설정 상태를 확인합니다."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    click.echo("\n🔧 현재 설정 상태\n")
    
    keys = [
        ("NOTION_TOKEN",            "Notion API 토큰"),
        ("NOTION_DATABASE_ID",      "작업 기록 DB ID"),
        ("NOTION_REPORT_PARENT_ID", "리포트 업로드 페이지 ID"),
        ("ANTHROPIC_API_KEY",       "Anthropic API 키"),
        ("LLM_MODEL",               "LLM 모델"),
        ("OUTPUT_DIR",              "리포트 저장 경로"),
    ]
    
    for key, label in keys:
        value = os.getenv(key)
        if value:
            # API 키는 앞 8자리만 표시
            display = value[:8] + "..." if len(value) > 8 else value
            status = click.style(f"✅ 설정됨 ({display})", fg="green")
        else:
            status = click.style("❌ 미설정", fg="red")
        
        click.echo(f"  {label:<28} {status}")
    
    # 이번 주 / 지난주 날짜 미리보기
    click.echo("\n📅 날짜 미리보기")
    for offset, label in [(0, "이번 주"), (1, "지난 주")]:
        start, end = get_week_range(offset)
        week_label = get_week_label(start)
        click.echo(f"  {label}: {week_label}  ({start} ~ {end})")
    
    click.echo()


if __name__ == "__main__":
    cli()