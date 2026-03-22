"""Daily digest scheduler - sends trending repos at scheduled times."""

import asyncio
from datetime import datetime

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.storage.database import Database
from src.core.scanner import GitHubScanner
from src.core.filter import RepoFilter
from src.core.scorer import RepoScorer

logger = structlog.get_logger(__name__)


class DigestScheduler:
    """Sends daily digests to users at their preferred times."""

    def __init__(self, bot_app):
        """
        Initialize scheduler.

        Args:
            bot_app: The telegram Application instance to send messages through
        """
        self.bot_app = bot_app
        self.db = Database()
        self.scanner = GitHubScanner()
        self.filter = RepoFilter()
        self.scorer = RepoScorer()
        self.scheduler = AsyncIOScheduler()
        self._db_ready = False

    async def _ensure_db(self) -> None:
        """Make sure database is connected."""
        if not self._db_ready:
            await self.db.connect()
            self._db_ready = True

    def start(self) -> None:
        """Start the scheduler."""
        # Check every minute for users who need digests
        self.scheduler.add_job(
            self._check_and_send_digests,
            CronTrigger(minute="*"),  # Every minute
            id="digest_checker",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("Digest scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Digest scheduler stopped")

    async def _check_and_send_digests(self) -> None:
        """Check if any users need digests right now."""
        try:
            await self._ensure_db()

            # Get current time in HH:MM format
            current_time = datetime.now().strftime("%H:%M")

            # Get users who want digest at this time
            users = await self.db.get_users_for_digest(current_time)

            if not users:
                return

            logger.info(f"Sending digests to {len(users)} users at {current_time}")

            for user in users:
                await self._send_digest_to_user(user)

        except Exception as e:
            logger.exception("Digest check failed", error=str(e))

    async def _send_digest_to_user(self, user_prefs: dict) -> None:
        """Send a digest to a specific user. 5 regular repos + 5 Web3 = 10 total."""
        try:
            telegram_id = user_prefs["telegram_id"]
            domains = user_prefs.get("domains") or None
            min_stars = user_prefs.get("min_stars", 50)

            logger.info(f"Sending digest to user {telegram_id}")

            # 1. Scan for regular trending repos (5)
            regular_repos = self.scanner.scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=3,
            )

            # 2. Scan for Web3 repos (2) - always included!
            web3_repos = self.scanner.scan_trending(
                domains=["web3"],
                min_stars=25,  # Lower threshold for web3
                max_results_per_domain=5,
            )

            # Filter and score both sets
            regular_filtered = self.filter.filter_repos(regular_repos) if regular_repos else []
            web3_filtered = self.filter.filter_repos(web3_repos) if web3_repos else []

            regular_scored = self.scorer.score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = self.scorer.score_repos(web3_filtered_deduped, top_n=5)

            total_count = len(regular_scored) + len(web3_scored)

            if total_count == 0:
                await self.bot_app.bot.send_message(
                    chat_id=int(telegram_id),
                    text="📫 *Daily Digest*\n\nNo new trending projects today. Check back tomorrow!",
                    parse_mode="Markdown",
                )
                return

            # Send header
            await self.bot_app.bot.send_message(
                chat_id=int(telegram_id),
                text=f"📫 *Your Daily Digest*\n\n"
                     f"Found {total_count} trending projects for you! 👇",
                parse_mode="Markdown",
            )

            # Send regular repos
            if regular_scored:
                await self.bot_app.bot.send_message(
                    chat_id=int(telegram_id),
                    text="🔥 *Trending Projects*",
                    parse_mode="Markdown",
                )

                for scored_repo in regular_scored:
                    await self._send_repo_message(telegram_id, scored_repo)

            # Send Web3 repos
            if web3_scored:
                await self.bot_app.bot.send_message(
                    chat_id=int(telegram_id),
                    text="🔗 *Web3 / Crypto Projects*",
                    parse_mode="Markdown",
                )

                for scored_repo in web3_scored:
                    await self._send_repo_message(telegram_id, scored_repo)

            # Send footer
            await self.bot_app.bot.send_message(
                chat_id=int(telegram_id),
                text="Use /find to explore more, /web3 for crypto, or /settings to change digest time.",
            )

            logger.info(f"Digest sent to user {telegram_id}", total_repos=total_count)

        except Exception as e:
            logger.exception(f"Failed to send digest to user", error=str(e))

    async def _send_repo_message(self, telegram_id: str, scored_repo) -> None:
        """Send a single repo message."""
        repo = scored_repo.repository
        desc = (repo.description or "No description")[:80]

        text = (
            f"📦 *{repo.name}*\n"
            f"⭐ {repo.stars:,} stars | 🔤 {repo.language or 'Unknown'}\n\n"
            f"_{desc}_\n\n"
            f"🔗 {repo.url}"
        )

        await self.bot_app.bot.send_message(
            chat_id=int(telegram_id),
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
