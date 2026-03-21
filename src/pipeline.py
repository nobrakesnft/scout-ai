"""Main pipeline orchestration - coordinates all components."""

from datetime import datetime

import structlog

from src.config import get_settings
from src.core import GitHubScanner, RepoFilter, RepoScorer, Deduplicator
from src.storage import Database
from src.delivery.formatter import DigestFormatter
from src.delivery.telegram_bot import TelegramBot

logger = structlog.get_logger(__name__)


class ScoutPipeline:
    """Orchestrates the GitHub Scout AI pipeline."""

    def __init__(self) -> None:
        """Initialize pipeline components."""
        self.settings = get_settings()
        self.scanner = GitHubScanner()
        self.filter = RepoFilter()
        self.scorer = RepoScorer()
        self.deduplicator = Deduplicator()
        self.formatter = DigestFormatter()
        self.db: Database | None = None
        self.bot: TelegramBot | None = None

    async def initialize(self) -> None:
        """Initialize async components."""
        self.db = Database()
        await self.db.connect()

        # Load seen repos from database
        seen_ids = await self.db.get_seen_repo_ids()
        self.deduplicator.load_seen_ids(seen_ids)

        self.bot = TelegramBot()
        logger.info("Pipeline initialized")

    async def shutdown(self) -> None:
        """Clean up resources."""
        if self.db:
            await self.db.close()
        logger.info("Pipeline shutdown complete")

    async def run(self) -> dict:
        """
        Execute the full pipeline.

        Returns:
            Dictionary with run statistics
        """
        run_id = await self.db.create_run()
        logger.info("Starting pipeline run", run_id=run_id)

        try:
            # Phase 1: Scan GitHub
            repos = await self.scanner.scan_trending(
                max_results_per_domain=self.settings.max_repos_per_run * 4
            )
            await self.db.update_run(run_id, repos_scanned=len(repos))

            # Phase 1: Filter
            filtered = self.filter.filter_repos(repos)
            await self.db.update_run(run_id, repos_filtered=len(filtered))

            # Phase 1: Deduplicate
            new_repos = self.deduplicator.deduplicate(filtered)

            # Phase 1: Score and rank
            scored = self.scorer.score_repos(
                new_repos,
                top_n=self.settings.max_repos_per_run
            )

            # Mark as seen
            self.deduplicator.mark_seen([s.repository for s in scored])

            # TODO: Phase 2 - AI Analysis
            # TODO: Phase 2 - Idea Generation

            # Save to database
            for scored_repo in scored:
                await self.db.save_repository(scored_repo.repository)

            # Format and send digest
            if scored:
                run_date = datetime.now().strftime("%Y-%m-%d")
                digest = self.formatter.format_simple_digest(scored, run_date)
                await self.bot.send_digest(digest)

            # Update run status
            stats = {
                "scanned": len(repos),
                "filtered": len(filtered),
                "new": len(new_repos),
                "top": len(scored),
            }
            await self.db.update_run(
                run_id,
                completed_at=datetime.utcnow().isoformat(),
                status="completed",
                repos_analyzed=len(scored),
            )

            logger.info("Pipeline run completed", run_id=run_id, stats=stats)
            return stats

        except Exception as e:
            logger.exception("Pipeline run failed", run_id=run_id)
            await self.db.update_run(
                run_id,
                status="failed",
                error_message=str(e),
            )
            raise
