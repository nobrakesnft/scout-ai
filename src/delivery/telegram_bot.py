"""Telegram bot - Simple and friendly!"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import structlog
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from src.config import get_settings
from src.core.scanner import GitHubScanner, Repository
from src.core.filter import RepoFilter
from src.core.scorer import RepoScorer, ScoredRepository
from src.ai.analyzer import AIAnalyzer

logger = structlog.get_logger(__name__)


class ScanCache:
    """Remembers your scans so you can click on repos later."""

    def __init__(self):
        self.repos: Dict[str, Repository] = {}  # repo_id -> Repository
        self.last_scan: Optional[datetime] = None
        self.last_results: List[ScoredRepository] = []

    def save_scan(self, scored_repos: List[ScoredRepository]):
        """Save a scan so user can click repos later."""
        self.repos.clear()
        self.last_results = scored_repos
        self.last_scan = datetime.now()

        for scored in scored_repos:
            repo = scored.repository
            self.repos[repo.github_id] = repo

    def get_repo(self, repo_id: str) -> Optional[Repository]:
        """Get a repo from the cache."""
        return self.repos.get(repo_id)

    def is_fresh(self, minutes: int = 60) -> bool:
        """Check if we have a recent scan."""
        if not self.last_scan:
            return False
        return datetime.now() - self.last_scan < timedelta(minutes=minutes)


class TelegramBot:
    """GitHub Scout Bot - Find cool projects and get business ideas!"""

    def __init__(self) -> None:
        settings = get_settings()
        self.chat_id = settings.telegram_chat_id
        self.app = Application.builder().token(
            settings.telegram_bot_token.get_secret_value()
        ).build()

        # Core stuff
        self.scanner = GitHubScanner()
        self.filter = RepoFilter()
        self.scorer = RepoScorer()
        self.cache = ScanCache()

        # AI
        try:
            self.analyzer = AIAnalyzer()
            self.ai_enabled = True
        except:
            self.analyzer = None
            self.ai_enabled = False

        self._register_handlers()

    def _register_handlers(self) -> None:
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("find", self._cmd_find))
        self.app.add_handler(CommandHandler("scan", self._cmd_find))  # alias
        self.app.add_handler(CommandHandler("ideas", self._cmd_ideas))
        self.app.add_handler(CommandHandler("help", self._cmd_help))
        self.app.add_handler(CallbackQueryHandler(self._handle_button))

    # ==================== COMMANDS ====================

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Welcome message - super simple!"""

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Find Cool Projects", callback_data="action:find")],
            [InlineKeyboardButton("💡 Find Projects + Get Ideas", callback_data="action:ideas")],
        ])

        await update.message.reply_text(
            "👋 *Hi! I'm Scout Bot!*\n\n"
            "I help you find cool coding projects on GitHub.\n\n"
            "Then I can turn them into business ideas! 💰\n\n"
            "What would you like to do?",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    async def _cmd_find(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Find cool projects - show with buttons."""

        await update.message.reply_text(
            "🔍 *Looking for cool projects...*\n\n"
            "Give me a moment! ⏳",
            parse_mode="Markdown",
        )

        try:
            # Scan GitHub
            repos = self.scanner.scan_trending(min_stars=50, max_results_per_domain=5)

            if not repos:
                await update.message.reply_text("😕 Couldn't find any projects. Try again later!")
                return

            # Filter and score
            filtered = self.filter.filter_repos(repos)
            scored = self.scorer.score_repos(filtered, top_n=5)

            # Save to cache
            self.cache.save_scan(scored)

            # Send header
            await update.message.reply_text(
                f"✨ *Found {len(scored)} cool projects!*\n\n"
                "Tap any project to get business ideas for it 👇",
                parse_mode="Markdown",
            )

            # Send each repo with buttons
            for scored_repo in scored:
                await self._send_repo_card(update.message.chat_id, scored_repo)

            # Send footer
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 Get Ideas for ALL Projects", callback_data="action:ideas_cached")],
            ])

            await update.message.reply_text(
                "👆 *Tap a project above to get ideas*\n\n"
                "Or get ideas for all of them at once:",
                parse_mode="Markdown",
                reply_markup=keyboard,
            )

        except Exception as e:
            logger.exception("Find failed", error=str(e))
            await update.message.reply_text(f"😕 Something went wrong: {str(e)[:50]}")

    async def _cmd_ideas(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Find projects AND get ideas for all of them."""

        if not self.ai_enabled:
            await update.message.reply_text(
                "😕 AI is not set up yet.\n\n"
                "Ask the developer to add the AI key!",
            )
            return

        await update.message.reply_text(
            "🔍 *Looking for cool projects...*\n\n"
            "Then I'll think of business ideas! 💡\n\n"
            "This takes about 1-2 minutes ⏳",
            parse_mode="Markdown",
        )

        try:
            # Scan
            repos = self.scanner.scan_trending(min_stars=100, max_results_per_domain=3)

            if not repos:
                await update.message.reply_text("😕 Couldn't find any projects. Try again later!")
                return

            filtered = self.filter.filter_repos(repos)
            scored = self.scorer.score_repos(filtered, top_n=3)

            # Save to cache
            self.cache.save_scan(scored)

            await update.message.reply_text(
                f"✨ *Found {len(scored)} projects!*\n\n"
                "Now thinking of business ideas... 🧠",
                parse_mode="Markdown",
            )

            # Analyze each with AI
            for scored_repo in scored:
                await self._send_repo_with_ideas(update.message.chat_id, scored_repo)

            await update.message.reply_text(
                "✅ *Done!*\n\n"
                "Use /find to browse more projects\n"
                "Use /ideas to get more ideas",
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.exception("Ideas failed", error=str(e))
            await update.message.reply_text(f"😕 Something went wrong: {str(e)[:50]}")

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Help - keep it simple!"""

        await update.message.reply_text(
            "🤖 *How to use Scout Bot*\n\n"
            "*Commands:*\n"
            "🔍 /find - Find cool projects\n"
            "💡 /ideas - Find projects + get business ideas\n"
            "❓ /help - See this message\n\n"
            "*How it works:*\n"
            "1️⃣ I search GitHub for trending projects\n"
            "2️⃣ I pick the best ones\n"
            "3️⃣ You can tap any project to get ideas\n"
            "4️⃣ I use AI to think of business ideas!\n\n"
            "That's it! Super easy 🎉",
            parse_mode="Markdown",
        )

    # ==================== BUTTONS ====================

    async def _handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button clicks."""

        query = update.callback_query
        await query.answer()

        data = query.data

        # Action buttons
        if data == "action:find":
            await self._do_find(query.message.chat_id)

        elif data == "action:ideas":
            await self._do_ideas(query.message.chat_id)

        elif data == "action:ideas_cached":
            await self._do_ideas_cached(query.message.chat_id)

        # Repo buttons
        elif data.startswith("repo:"):
            repo_id = data.split(":")[1]
            await self._analyze_single_repo(query.message.chat_id, repo_id)

        elif data.startswith("github:"):
            pass  # URL button, handled by Telegram

    async def _do_find(self, chat_id: int) -> None:
        """Find projects (triggered by button)."""

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="🔍 *Looking for cool projects...*",
            parse_mode="Markdown",
        )

        try:
            repos = self.scanner.scan_trending(min_stars=50, max_results_per_domain=5)

            if not repos:
                await self.app.bot.send_message(chat_id=chat_id, text="😕 No projects found!")
                return

            filtered = self.filter.filter_repos(repos)
            scored = self.scorer.score_repos(filtered, top_n=5)
            self.cache.save_scan(scored)

            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"✨ *Found {len(scored)} cool projects!*\n\nTap any to get ideas 👇",
                parse_mode="Markdown",
            )

            for scored_repo in scored:
                await self._send_repo_card(chat_id, scored_repo)

        except Exception as e:
            await self.app.bot.send_message(chat_id=chat_id, text=f"😕 Error: {str(e)[:50]}")

    async def _do_ideas(self, chat_id: int) -> None:
        """Full ideas flow (triggered by button)."""

        if not self.ai_enabled:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 AI not available!")
            return

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="🔍 *Looking for projects + generating ideas...*\n\nThis takes 1-2 minutes ⏳",
            parse_mode="Markdown",
        )

        try:
            repos = self.scanner.scan_trending(min_stars=100, max_results_per_domain=3)

            if not repos:
                await self.app.bot.send_message(chat_id=chat_id, text="😕 No projects found!")
                return

            filtered = self.filter.filter_repos(repos)
            scored = self.scorer.score_repos(filtered, top_n=3)
            self.cache.save_scan(scored)

            for scored_repo in scored:
                await self._send_repo_with_ideas(chat_id, scored_repo)

            await self.app.bot.send_message(
                chat_id=chat_id,
                text="✅ *All done!* Use /find or /ideas anytime!",
                parse_mode="Markdown",
            )

        except Exception as e:
            await self.app.bot.send_message(chat_id=chat_id, text=f"😕 Error: {str(e)[:50]}")

    async def _do_ideas_cached(self, chat_id: int) -> None:
        """Get ideas for already-scanned repos."""

        if not self.ai_enabled:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 AI not available!")
            return

        if not self.cache.last_results:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="😕 No projects saved. Use /find first!"
            )
            return

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=f"💡 *Getting ideas for {len(self.cache.last_results)} projects...*",
            parse_mode="Markdown",
        )

        for scored_repo in self.cache.last_results:
            await self._send_repo_with_ideas(chat_id, scored_repo)

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="✅ *All done!*",
            parse_mode="Markdown",
        )

    async def _analyze_single_repo(self, chat_id: int, repo_id: str) -> None:
        """Get ideas for one specific repo."""

        if not self.ai_enabled:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 AI not available!")
            return

        repo = self.cache.get_repo(repo_id)

        if not repo:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="😕 Can't find that project. Use /find to search again!"
            )
            return

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=f"💡 *Thinking of ideas for {repo.name}...*",
            parse_mode="Markdown",
        )

        try:
            analysis, ideas = self.analyzer.analyze_and_ideate(repo)

            # Build message
            lines = [
                f"📦 *{repo.name}*",
                f"⭐ {repo.stars:,} stars",
                "",
                f"🔍 *What it does:*",
                f"{analysis.problem}",
                "",
                f"💡 *How it works:*",
                f"{analysis.solution}",
                "",
            ]

            if ideas:
                lines.append("💰 *Business Ideas:*")

                for i, idea in enumerate(ideas, 1):
                    lines.extend([
                        "",
                        f"*{i}. {idea.title}*",
                        f"{idea.description}",
                        "",
                        f"👥 Who buys it: {idea.target_market}",
                        f"💵 How to make money: {idea.monetization}",
                        f"📊 How hard to build: {idea.feasibility}/10",
                    ])

            await self.app.bot.send_message(
                chat_id=chat_id,
                text="\n".join(lines),
                parse_mode="Markdown",
            )

        except Exception as e:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"😕 Couldn't analyze: {str(e)[:50]}"
            )

    # ==================== HELPERS ====================

    async def _send_repo_card(self, chat_id: int, scored_repo: ScoredRepository) -> None:
        """Send a repo card with buttons."""

        repo = scored_repo.repository
        desc = (repo.description or "No description")[:80]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💡 Get Ideas", callback_data=f"repo:{repo.github_id}"),
                InlineKeyboardButton("🔗 Open GitHub", url=repo.url),
            ]
        ])

        text = (
            f"📦 *{repo.name}*\n"
            f"⭐ {repo.stars:,} stars | 🔤 {repo.language or 'Unknown'}\n\n"
            f"_{desc}_"
        )

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    async def _send_repo_with_ideas(self, chat_id: int, scored_repo: ScoredRepository) -> None:
        """Send repo + AI analysis + ideas."""

        repo = scored_repo.repository

        try:
            analysis, ideas = self.analyzer.analyze_and_ideate(repo)

            lines = [
                "─" * 25,
                f"📦 *{repo.name}*",
                f"⭐ {repo.stars:,} | 🔤 {repo.language or 'Unknown'}",
                "",
                f"🔍 *Problem it solves:*",
                f"{analysis.problem}",
                "",
            ]

            if ideas:
                lines.append("💰 *Business Ideas:*")

                for i, idea in enumerate(ideas, 1):
                    lines.extend([
                        "",
                        f"*{i}. {idea.title}*",
                        f"{idea.description}",
                        f"💵 {idea.monetization} | 📊 Difficulty: {idea.feasibility}/10",
                    ])

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Open GitHub", url=repo.url)]
            ])

            await self.app.bot.send_message(
                chat_id=chat_id,
                text="\n".join(lines),
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )

        except Exception as e:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"📦 *{repo.name}* - ⚠️ Couldn't analyze",
                parse_mode="Markdown",
            )

    def run_polling(self) -> None:
        """Start the bot!"""
        logger.info("Starting bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
