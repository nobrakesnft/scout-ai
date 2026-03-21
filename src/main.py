"""GitHub Scout AI - Main entry point."""

import asyncio
import sys

import structlog

from src.config import get_settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer() if get_settings().is_production
        else structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


async def run_scout() -> None:
    """Run the GitHub Scout AI system."""
    settings = get_settings()

    logger.info(
        "Starting GitHub Scout AI",
        env=settings.app_env,
        log_level=settings.log_level,
    )

    # TODO: Phase 1 - Initialize components
    # - Database connection
    # - GitHub scanner
    # - Telegram bot
    # - Scheduler

    # TODO: Phase 2+ - Initialize AI components
    # - CrewAI agents
    # - Cost tracker

    logger.info("GitHub Scout AI initialized successfully")

    # Keep running (scheduler will handle periodic tasks)
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Shutting down GitHub Scout AI")


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(run_scout())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")
        sys.exit(0)
    except Exception as e:
        logger.exception("Fatal error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
