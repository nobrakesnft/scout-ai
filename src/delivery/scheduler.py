"""Daily digest scheduler - sends trending repos with AI ideas at scheduled times."""

import asyncio
from datetime import datetime

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.storage.database import Database
from src.core.scanner import GitHubScanner
from src.core.filter import RepoFilter
from src.core.scorer import RepoScorer
from src.ai.analyzer import AIAnalyzer

logger = structlog.get_logger(__name__)


class DigestScheduler:
    """Sends daily digests with AI-generated business ideas."""

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

        # AI analyzer
        try:
            self.analyzer = AIAnalyzer()
            self.ai_enabled = True
        except:
            self.analyzer = None
            self.ai_enabled = False

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
        """Send a digest with AI ideas. 5 regular + 5 Web3 = 10 total (only NEW repos)."""
        try:
            telegram_id = user_prefs["telegram_id"]
            domains = user_prefs.get("domains") or None
            min_stars = user_prefs.get("min_stars", 50)

            logger.info(f"Sending digest to user {telegram_id}")

            # Get repos this user has already seen
            seen_ids = await self.db.get_seen_repo_ids_for_user(telegram_id)

            # 1. Scan for regular trending repos
            regular_repos = self.scanner.scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=5,
            )

            # 2. Scan for Web3 repos
            web3_repos = self.scanner.scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=10,
            )

            # Filter out already seen repos
            regular_repos_new = [r for r in regular_repos if r.github_id not in seen_ids] if regular_repos else []
            web3_repos_new = [r for r in web3_repos if r.github_id not in seen_ids] if web3_repos else []

            # Filter and score
            regular_filtered = self.filter.filter_repos(regular_repos_new) if regular_repos_new else []
            web3_filtered = self.filter.filter_repos(web3_repos_new) if web3_repos_new else []

            regular_scored = self.scorer.score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = self.scorer.score_repos(web3_filtered_deduped, top_n=5)

            all_scored = regular_scored + web3_scored
            total_count = len(all_scored)

            if total_count == 0:
                await self.bot_app.bot.send_message(
                    chat_id=int(telegram_id),
                    text="📫 *Daily Digest*\n\nNo new projects today - you've seen all the trending ones! Check back tomorrow.",
                    parse_mode="Markdown",
                )
                return

            # Send header
            await self.bot_app.bot.send_message(
                chat_id=int(telegram_id),
                text=f"📫 *Your Daily Digest*\n\n"
                     f"Found {total_count} NEW projects with business ideas! 👇",
                parse_mode="Markdown",
            )

            # Track repos we're sending (to mark as seen)
            sent_repo_ids = []

            # Send regular repos with AI ideas
            if regular_scored:
                await self.bot_app.bot.send_message(
                    chat_id=int(telegram_id),
                    text="🔥 *Trending Projects + Ideas*",
                    parse_mode="Markdown",
                )

                for scored_repo in regular_scored:
                    await self._send_repo_with_ideas(telegram_id, scored_repo)
                    sent_repo_ids.append(scored_repo.repository.github_id)

            # Send Web3 repos with AI ideas
            if web3_scored:
                await self.bot_app.bot.send_message(
                    chat_id=int(telegram_id),
                    text="🔗 *Web3 / Crypto Projects + Ideas*",
                    parse_mode="Markdown",
                )

                for scored_repo in web3_scored:
                    await self._send_repo_with_ideas(telegram_id, scored_repo)
                    sent_repo_ids.append(scored_repo.repository.github_id)

            # Mark all sent repos as seen
            await self.db.mark_repos_as_seen(telegram_id, sent_repo_ids)

            # Send footer
            await self.bot_app.bot.send_message(
                chat_id=int(telegram_id),
                text=f"✅ *{total_count} projects with {total_count * 2} business ideas!*\n\n"
                     "Use /find to explore more, /web3 for crypto, or /settings to change preferences.",
                parse_mode="Markdown",
            )

            logger.info(f"Digest sent to user {telegram_id}", total_repos=total_count, ideas=total_count * 2)

        except Exception as e:
            logger.exception(f"Failed to send digest to user", error=str(e))

    async def _send_repo_with_ideas(self, telegram_id: str, scored_repo) -> None:
        """Send a repo with AI-generated business ideas."""
        repo = scored_repo.repository
        desc = (repo.description or "No description")[:100]

        # Try to get AI ideas
        ideas_text = ""
        if self.ai_enabled and self.analyzer:
            try:
                analysis, ideas = self.analyzer.analyze_and_ideate(repo)

                if ideas:
                    ideas_lines = []
                    for i, idea in enumerate(ideas, 1):
                        ideas_lines.append(
                            f"💡 *{i}. {idea.title}*\n"
                            f"{idea.description}\n"
                            f"💵 {idea.monetization} | 📊 Difficulty: {idea.feasibility}/10"
                        )
                    ideas_text = "\n\n".join(ideas_lines)
            except Exception as e:
                logger.warning(f"AI analysis failed for {repo.name}", error=str(e))

        # Build message
        text = (
            f"{'─' * 25}\n"
            f"📦 *{repo.name}*\n"
            f"⭐ {repo.stars:,} stars | 🔤 {repo.language or 'Unknown'}\n\n"
            f"_{desc}_\n\n"
            f"🔗 {repo.url}"
        )

        if ideas_text:
            text += f"\n\n{ideas_text}"

        await self.bot_app.bot.send_message(
            chat_id=int(telegram_id),
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
