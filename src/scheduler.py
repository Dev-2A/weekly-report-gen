import schedule
import time
import logging
from datetime import datetime
from src.pipeline import WeeklyReportPipeline
from src.config import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_weekly_report(week_offset: int = 1):
    """스케줄러에서 호출되는 리포트 생성 함수"""
    logger.info("⏰ 스케줄러 실행: 주간 회고 리포트 생성 시작")
    try:
        config = load_config()
        pipeline = WeeklyReportPipeline(config)
        result = pipeline.run(week_offset=week_offset)
        logger.info(f"✅ 완료: {result['week_label']} ({result['task_count']}개 작업)")
        if result["notion_url"]:
            logger.info(f"🔗 Notion: {result['notion_url']}")
    except Exception as e:
        logger.error(f"❌ 리포트 생성 실패: {e}")


def start_scheduler(
    weekday: str = "monday",
    hour: int = 9,
    minute: int = 0,
):
    """
    스케줄러를 시작합니다.
    
    Args:
        weekday: 실행 요일 (monday ~ sunday)
        hour:    실행 시각 (0~23)
        minute:  실행 분 (0~59)
    """
    time_str = f"{hour:02d}:{minute:02d}"
    weekday_kr = {
        "monday": "월요일", "tuesday": "화요일", "wednesday": "수요일",
        "thursday": "목요일", "friday": "금요일",
        "saturday": "토요일", "sunday": "일요일",
    }

    getattr(schedule.every(), weekday).at(time_str).do(run_weekly_report)

    logger.info("🗓️  Weekly Report Generator 스케줄러 시작")
    logger.info(f"   실행 주기: 매주 {weekday_kr.get(weekday, weekday)} {time_str}")
    logger.info("   종료하려면 Ctrl+C 를 누르세요.\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("\n👋 스케줄러가 종료되었습니다.")