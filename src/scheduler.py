"""APScheduler configuration for scheduled pipeline runs."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog

from src.config import get_settings
from src.pipeline import ScoutPipeline

logger = structlog.get_logger(__name__)


class PipelineScheduler:
    """Manages scheduled pipeline runs."""

    def __init__(self, pipeline: ScoutPipeline) -> None:
        """Initialize scheduler with pipeline."""
        self.pipeline = pipeline
        self.scheduler = AsyncIOScheduler()
        self.settings = get_settings()

    def setup(self) -> None:
        """Configure scheduled jobs."""
        # Parse cron expression from settings
        cron_parts = self.settings.digest_schedule.split()
        if len(cron_parts) == 5:
            minute, hour, day, month, day_of_week = cron_parts
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
            )
        else:
            # Default to 8 AM UTC
            trigger = CronTrigger(hour=8, minute=0)

        self.scheduler.add_job(
            self._run_pipeline,
            trigger=trigger,
            id="daily_digest",
            name="Daily GitHub Scout Digest",
            replace_existing=True,
        )

        logger.info(
            "Scheduler configured",
            schedule=self.settings.digest_schedule,
        )

    async def _run_pipeline(self) -> None:
        """Execute the pipeline (called by scheduler)."""
        logger.info("Scheduled pipeline run starting")
        try:
            stats = await self.pipeline.run()
            logger.info("Scheduled pipeline run completed", stats=stats)
        except Exception as e:
            logger.exception("Scheduled pipeline run failed", error=str(e))

    def start(self) -> None:
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")
