"""Telegram bot - Simple and friendly!"""

import asyncio
from datetime import datetime, timedelta, time
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
from src.storage.database import Database

logger = structlog.get_logger(__name__)

# Available domains for scanning
AVAILABLE_DOMAINS = [
    "ai-ml",
    "developer-tools",
    "productivity",
    "web-dev",
    "data",
    "security",
    "mobile",
    "devops",
    "web3",
]


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

        # Database
        self.db = Database()
        self._db_ready = False

        # AI
        try:
            self.analyzer = AIAnalyzer()
            self.ai_enabled = True
        except:
            self.analyzer = None
            self.ai_enabled = False

        self._register_handlers()

    async def _ensure_db(self) -> None:
        """Make sure database is connected."""
        if not self._db_ready:
            await self.db.connect()
            self._db_ready = True

    def _register_handlers(self) -> None:
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("find", self._cmd_find))
        self.app.add_handler(CommandHandler("scan", self._cmd_find))  # alias
        self.app.add_handler(CommandHandler("ideas", self._cmd_ideas))
        self.app.add_handler(CommandHandler("web3", self._cmd_web3))
        self.app.add_handler(CommandHandler("saved", self._cmd_saved))
        self.app.add_handler(CommandHandler("settings", self._cmd_settings))
        self.app.add_handler(CommandHandler("help", self._cmd_help))
        self.app.add_handler(CallbackQueryHandler(self._handle_button))

    # ==================== COMMANDS ====================

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Welcome message - super simple!"""
        await self._ensure_db()

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Find Cool Projects", callback_data="action:find")],
            [InlineKeyboardButton("💡 Find Projects + Get Ideas", callback_data="action:ideas")],
            [InlineKeyboardButton("🔗 Web3 / Crypto / NFT", callback_data="action:web3")],
            [InlineKeyboardButton("⭐ My Saved Projects", callback_data="action:saved")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="action:settings")],
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
        await self._ensure_db()
        user_id = str(update.effective_user.id)

        await update.message.reply_text(
            "🔍 *Looking for cool projects...*\n\n"
            "Give me a moment! ⏳",
            parse_mode="Markdown",
        )

        try:
            # Check user preferences for domains
            prefs = await self.db.get_preferences(user_id)
            domains = prefs.get("domains") if prefs and prefs.get("domains") else None
            min_stars = prefs.get("min_stars", 50) if prefs else 50

            # Scan regular repos (5)
            regular_repos = self.scanner.scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=5
            )

            # Scan Web3 repos (2) - always included!
            web3_repos = self.scanner.scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=5
            )

            # Filter and score both
            regular_filtered = self.filter.filter_repos(regular_repos) if regular_repos else []
            web3_filtered = self.filter.filter_repos(web3_repos) if web3_repos else []

            regular_scored = self.scorer.score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = self.scorer.score_repos(web3_filtered_deduped, top_n=2)

            # Combine all results
            all_scored = regular_scored + web3_scored
            total_count = len(all_scored)

            if total_count == 0:
                await update.message.reply_text("😕 Couldn't find any projects. Try again later!")
                return

            # Save to cache
            self.cache.save_scan(all_scored)

            # Send header
            await update.message.reply_text(
                f"✨ *Found {total_count} cool projects!*\n\n"
                "Tap any project to get business ideas for it 👇",
                parse_mode="Markdown",
            )

            # Send regular repos
            if regular_scored:
                for scored_repo in regular_scored:
                    await self._send_repo_card(update.message.chat_id, scored_repo, user_id)

            # Send Web3 repos with header
            if web3_scored:
                await update.message.reply_text(
                    "🔗 *Web3 / Crypto Projects:*",
                    parse_mode="Markdown",
                )
                for scored_repo in web3_scored:
                    await self._send_repo_card(update.message.chat_id, scored_repo, user_id)

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
        await self._ensure_db()

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
            # Check user preferences
            user_id = str(update.effective_user.id)
            prefs = await self.db.get_preferences(user_id)
            domains = prefs.get("domains") if prefs and prefs.get("domains") else None
            min_stars = prefs.get("min_stars", 50) if prefs else 50

            # Scan regular repos (5)
            regular_repos = self.scanner.scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=5
            )

            # Scan Web3 repos (2)
            web3_repos = self.scanner.scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=5
            )

            # Filter and score both
            regular_filtered = self.filter.filter_repos(regular_repos) if regular_repos else []
            web3_filtered = self.filter.filter_repos(web3_repos) if web3_repos else []

            regular_scored = self.scorer.score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = self.scorer.score_repos(web3_filtered_deduped, top_n=2)

            # Combine all results
            all_scored = regular_scored + web3_scored
            total_count = len(all_scored)

            if total_count == 0:
                await update.message.reply_text("😕 Couldn't find any projects. Try again later!")
                return

            # Save to cache
            self.cache.save_scan(all_scored)

            await update.message.reply_text(
                f"✨ *Found {total_count} cool projects!*\n\n"
                "Now thinking of business ideas... 🧠",
                parse_mode="Markdown",
            )

            # Analyze regular repos
            if regular_scored:
                for scored_repo in regular_scored:
                    await self._send_repo_with_ideas(update.message.chat_id, scored_repo, user_id)

            # Analyze Web3 repos with header
            if web3_scored:
                await update.message.reply_text(
                    "🔗 *Web3 / Crypto Ideas:*",
                    parse_mode="Markdown",
                )
                for scored_repo in web3_scored:
                    await self._send_repo_with_ideas(update.message.chat_id, scored_repo, user_id)

            await update.message.reply_text(
                "✅ *Done!*\n\n"
                "Use /find to browse more projects\n"
                "Use /ideas to get more ideas\n"
                "Use /saved to see your bookmarks",
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.exception("Ideas failed", error=str(e))
            await update.message.reply_text(f"😕 Something went wrong: {str(e)[:50]}")

    async def _cmd_web3(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Find Web3/crypto/NFT projects."""
        await self._ensure_db()
        user_id = str(update.effective_user.id)

        await update.message.reply_text(
            "🔗 *Looking for Web3 projects...*\n\n"
            "Searching blockchain, crypto, NFT, DeFi... ⏳",
            parse_mode="Markdown",
        )

        try:
            # Scan ONLY web3 domain with lower star threshold
            repos = self.scanner.scan_trending(
                domains=["web3"],
                min_stars=25,  # Lower threshold for web3
                max_results_per_domain=10,
            )

            if not repos:
                await update.message.reply_text("😕 No Web3 projects found. Try again later!")
                return

            # Filter and score
            filtered = self.filter.filter_repos(repos)
            scored = self.scorer.score_repos(filtered, top_n=5)

            # Save to cache
            self.cache.save_scan(scored)

            await update.message.reply_text(
                f"🔗 *Found {len(scored)} Web3 projects!*\n\n"
                "Tap any project to get business ideas 👇",
                parse_mode="Markdown",
            )

            # Send each repo with buttons
            for scored_repo in scored:
                await self._send_repo_card(update.message.chat_id, scored_repo, user_id)

            # Send footer
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 Get Ideas for ALL", callback_data="action:ideas_cached")],
            ])

            await update.message.reply_text(
                "👆 *Tap a project above to get ideas*\n\n"
                "Or get ideas for all of them:",
                parse_mode="Markdown",
                reply_markup=keyboard,
            )

        except Exception as e:
            logger.exception("Web3 scan failed", error=str(e))
            await update.message.reply_text(f"😕 Something went wrong: {str(e)[:50]}")

    async def _cmd_saved(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show saved/bookmarked projects."""
        await self._ensure_db()
        user_id = str(update.effective_user.id)

        bookmarks = await self.db.get_bookmarks(user_id)

        if not bookmarks:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Find Projects", callback_data="action:find")],
            ])
            await update.message.reply_text(
                "📭 *No saved projects yet!*\n\n"
                "Use /find to discover projects, then tap ⭐ to save them.",
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            return

        await update.message.reply_text(
            f"⭐ *Your Saved Projects ({len(bookmarks)})*\n\n"
            "Here are the projects you bookmarked 👇",
            parse_mode="Markdown",
        )

        for bookmark in bookmarks:
            await self._send_bookmark_card(update.message.chat_id, bookmark, user_id)

    async def _cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show settings menu."""
        await self._ensure_db()
        user_id = str(update.effective_user.id)

        prefs = await self.db.get_preferences(user_id)

        # Current settings display
        if prefs:
            domains = prefs.get("domains", [])
            domains_text = ", ".join(domains) if domains else "All domains"
            min_stars = prefs.get("min_stars", 50)
            digest_time = prefs.get("digest_time", "Off")
        else:
            domains_text = "All domains"
            min_stars = 50
            digest_time = "Off"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 Choose Domains", callback_data="settings:domains")],
            [InlineKeyboardButton("⭐ Min Stars", callback_data="settings:stars")],
            [InlineKeyboardButton("⏰ Daily Digest", callback_data="settings:digest")],
        ])

        await update.message.reply_text(
            "⚙️ *Your Settings*\n\n"
            f"🎯 *Domains:* {domains_text}\n"
            f"⭐ *Min stars:* {min_stars}\n"
            f"⏰ *Daily digest:* {digest_time}\n\n"
            "Tap to change:",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Help - keep it simple!"""

        await update.message.reply_text(
            "🤖 *How to use Scout Bot*\n\n"
            "*Commands:*\n"
            "🔍 /find - Find cool projects\n"
            "💡 /ideas - Find projects + get business ideas\n"
            "🔗 /web3 - Find crypto/NFT/blockchain projects\n"
            "⭐ /saved - See your bookmarked projects\n"
            "⚙️ /settings - Change your preferences\n"
            "❓ /help - See this message\n\n"
            "*How it works:*\n"
            "1️⃣ I search GitHub for trending projects\n"
            "2️⃣ I pick the best ones\n"
            "3️⃣ You can tap ⭐ to save any project\n"
            "4️⃣ Tap 💡 to get business ideas!\n\n"
            "That's it! Super easy 🎉",
            parse_mode="Markdown",
        )

    # ==================== BUTTONS ====================

    async def _handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button clicks."""
        await self._ensure_db()

        query = update.callback_query
        await query.answer()

        data = query.data
        user_id = str(update.effective_user.id)
        chat_id = query.message.chat_id

        # Action buttons
        if data == "action:find":
            await self._do_find(chat_id, user_id)

        elif data == "action:ideas":
            await self._do_ideas(chat_id, user_id)

        elif data == "action:web3":
            await self._do_web3(chat_id, user_id)

        elif data == "action:ideas_cached":
            await self._do_ideas_cached(chat_id, user_id)

        elif data == "action:saved":
            await self._do_saved(chat_id, user_id)

        elif data == "action:settings":
            await self._do_settings(chat_id, user_id)

        # Repo buttons
        elif data.startswith("repo:"):
            repo_id = data.split(":")[1]
            await self._analyze_single_repo(chat_id, repo_id)

        elif data.startswith("save:"):
            repo_id = data.split(":")[1]
            await self._save_repo(chat_id, user_id, repo_id, query)

        elif data.startswith("unsave:"):
            repo_id = data.split(":")[1]
            await self._unsave_repo(chat_id, user_id, repo_id)

        # Settings buttons
        elif data == "settings:domains":
            await self._show_domain_picker(chat_id, user_id)

        elif data.startswith("domain:"):
            domain = data.split(":")[1]
            await self._toggle_domain(chat_id, user_id, domain)

        elif data == "settings:stars":
            await self._show_stars_picker(chat_id)

        elif data.startswith("stars:"):
            stars = int(data.split(":")[1])
            await self._set_min_stars(chat_id, user_id, stars)

        elif data == "settings:digest":
            await self._show_digest_picker(chat_id)

        elif data.startswith("digest:"):
            time_str = data.split(":")[1]
            await self._set_digest_time(chat_id, user_id, time_str)

    # ==================== ACTION HANDLERS ====================

    async def _do_find(self, chat_id: int, user_id: str) -> None:
        """Find projects (triggered by button). 5 regular + 2 Web3 = 7 total."""

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="🔍 *Looking for cool projects...*",
            parse_mode="Markdown",
        )

        try:
            prefs = await self.db.get_preferences(user_id)
            domains = prefs.get("domains") if prefs and prefs.get("domains") else None
            min_stars = prefs.get("min_stars", 50) if prefs else 50

            # Scan regular repos (5)
            regular_repos = self.scanner.scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=5
            )

            # Scan Web3 repos (2)
            web3_repos = self.scanner.scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=5
            )

            # Filter and score both
            regular_filtered = self.filter.filter_repos(regular_repos) if regular_repos else []
            web3_filtered = self.filter.filter_repos(web3_repos) if web3_repos else []

            regular_scored = self.scorer.score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = self.scorer.score_repos(web3_filtered_deduped, top_n=2)

            all_scored = regular_scored + web3_scored
            total_count = len(all_scored)

            if total_count == 0:
                await self.app.bot.send_message(chat_id=chat_id, text="😕 No projects found!")
                return

            self.cache.save_scan(all_scored)

            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"✨ *Found {total_count} cool projects!*\n\nTap any to get ideas 👇",
                parse_mode="Markdown",
            )

            for scored_repo in regular_scored:
                await self._send_repo_card(chat_id, scored_repo, user_id)

            if web3_scored:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text="🔗 *Web3 / Crypto Projects:*",
                    parse_mode="Markdown",
                )
                for scored_repo in web3_scored:
                    await self._send_repo_card(chat_id, scored_repo, user_id)

        except Exception as e:
            await self.app.bot.send_message(chat_id=chat_id, text=f"😕 Error: {str(e)[:50]}")

    async def _do_ideas(self, chat_id: int, user_id: str) -> None:
        """Full ideas flow (triggered by button). 5 regular + 2 Web3 = 7 total."""

        if not self.ai_enabled:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 AI not available!")
            return

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="🔍 *Looking for projects + generating ideas...*\n\nThis takes 1-2 minutes ⏳",
            parse_mode="Markdown",
        )

        try:
            prefs = await self.db.get_preferences(user_id)
            domains = prefs.get("domains") if prefs and prefs.get("domains") else None
            min_stars = prefs.get("min_stars", 50) if prefs else 50

            # Scan regular repos (5)
            regular_repos = self.scanner.scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=5
            )

            # Scan Web3 repos (2)
            web3_repos = self.scanner.scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=5
            )

            # Filter and score both
            regular_filtered = self.filter.filter_repos(regular_repos) if regular_repos else []
            web3_filtered = self.filter.filter_repos(web3_repos) if web3_repos else []

            regular_scored = self.scorer.score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = self.scorer.score_repos(web3_filtered_deduped, top_n=2)

            all_scored = regular_scored + web3_scored
            total_count = len(all_scored)

            if total_count == 0:
                await self.app.bot.send_message(chat_id=chat_id, text="😕 No projects found!")
                return

            self.cache.save_scan(all_scored)

            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"✨ *Found {total_count} cool projects!*\n\nNow thinking of business ideas... 🧠",
                parse_mode="Markdown",
            )

            for scored_repo in regular_scored:
                await self._send_repo_with_ideas(chat_id, scored_repo, user_id)

            if web3_scored:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text="🔗 *Web3 / Crypto Ideas:*",
                    parse_mode="Markdown",
                )
                for scored_repo in web3_scored:
                    await self._send_repo_with_ideas(chat_id, scored_repo, user_id)

            await self.app.bot.send_message(
                chat_id=chat_id,
                text="✅ *All done!* Use /find or /ideas anytime!",
                parse_mode="Markdown",
            )

        except Exception as e:
            await self.app.bot.send_message(chat_id=chat_id, text=f"😕 Error: {str(e)[:50]}")

    async def _do_web3(self, chat_id: int, user_id: str) -> None:
        """Find Web3 projects (triggered by button)."""

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="🔗 *Looking for Web3 projects...*",
            parse_mode="Markdown",
        )

        try:
            repos = self.scanner.scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=10,
            )

            if not repos:
                await self.app.bot.send_message(chat_id=chat_id, text="😕 No Web3 projects found!")
                return

            filtered = self.filter.filter_repos(repos)
            scored = self.scorer.score_repos(filtered, top_n=5)
            self.cache.save_scan(scored)

            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"🔗 *Found {len(scored)} Web3 projects!*\n\nTap any to get ideas 👇",
                parse_mode="Markdown",
            )

            for scored_repo in scored:
                await self._send_repo_card(chat_id, scored_repo, user_id)

        except Exception as e:
            await self.app.bot.send_message(chat_id=chat_id, text=f"😕 Error: {str(e)[:50]}")

    async def _do_ideas_cached(self, chat_id: int, user_id: str) -> None:
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
            await self._send_repo_with_ideas(chat_id, scored_repo, user_id)

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="✅ *All done!*",
            parse_mode="Markdown",
        )

    async def _do_saved(self, chat_id: int, user_id: str) -> None:
        """Show saved projects (triggered by button)."""

        bookmarks = await self.db.get_bookmarks(user_id)

        if not bookmarks:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Find Projects", callback_data="action:find")],
            ])
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="📭 *No saved projects yet!*\n\nUse /find to discover projects, then tap ⭐ to save them.",
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            return

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=f"⭐ *Your Saved Projects ({len(bookmarks)})*",
            parse_mode="Markdown",
        )

        for bookmark in bookmarks:
            await self._send_bookmark_card(chat_id, bookmark, user_id)

    async def _do_settings(self, chat_id: int, user_id: str) -> None:
        """Show settings (triggered by button)."""

        prefs = await self.db.get_preferences(user_id)

        if prefs:
            domains = prefs.get("domains", [])
            domains_text = ", ".join(domains) if domains else "All domains"
            min_stars = prefs.get("min_stars", 50)
            digest_time = prefs.get("digest_time", "Off")
        else:
            domains_text = "All domains"
            min_stars = 50
            digest_time = "Off"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 Choose Domains", callback_data="settings:domains")],
            [InlineKeyboardButton("⭐ Min Stars", callback_data="settings:stars")],
            [InlineKeyboardButton("⏰ Daily Digest", callback_data="settings:digest")],
        ])

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=f"⚙️ *Your Settings*\n\n"
                 f"🎯 *Domains:* {domains_text}\n"
                 f"⭐ *Min stars:* {min_stars}\n"
                 f"⏰ *Daily digest:* {digest_time}\n\n"
                 "Tap to change:",
            parse_mode="Markdown",
            reply_markup=keyboard,
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

    # ==================== BOOKMARK HANDLERS ====================

    async def _save_repo(self, chat_id: int, user_id: str, repo_id: str, query) -> None:
        """Save a repo to bookmarks."""

        repo = self.cache.get_repo(repo_id)
        if not repo:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 Can't find that project!")
            return

        saved = await self.db.save_bookmark(
            telegram_id=user_id,
            github_id=repo.github_id,
            name=repo.name,
            full_name=repo.full_name,
            description=repo.description,
            url=repo.url,
            stars=repo.stars,
            language=repo.language,
        )

        if saved:
            await query.answer("⭐ Saved!", show_alert=False)
        else:
            await query.answer("Already saved!", show_alert=False)

    async def _unsave_repo(self, chat_id: int, user_id: str, repo_id: str) -> None:
        """Remove a repo from bookmarks."""

        removed = await self.db.remove_bookmark(user_id, repo_id)

        if removed:
            await self.app.bot.send_message(chat_id=chat_id, text="🗑️ Removed from saved!")
        else:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 Wasn't saved!")

    # ==================== SETTINGS HANDLERS ====================

    async def _show_domain_picker(self, chat_id: int, user_id: str) -> None:
        """Show domain selection."""

        prefs = await self.db.get_preferences(user_id)
        current_domains = prefs.get("domains", []) if prefs else []

        buttons = []
        for domain in AVAILABLE_DOMAINS:
            check = "✅" if domain in current_domains else "⬜"
            buttons.append([
                InlineKeyboardButton(f"{check} {domain}", callback_data=f"domain:{domain}")
            ])

        buttons.append([InlineKeyboardButton("✔️ Done", callback_data="action:settings")])

        keyboard = InlineKeyboardMarkup(buttons)

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="🎯 *Choose domains to scan*\n\n"
                 "Tap to select/deselect.\n"
                 "Leave all unchecked to scan everything.",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    async def _toggle_domain(self, chat_id: int, user_id: str, domain: str) -> None:
        """Toggle a domain on/off."""

        prefs = await self.db.get_preferences(user_id)
        current_domains = prefs.get("domains", []) if prefs else []

        if domain in current_domains:
            current_domains.remove(domain)
        else:
            current_domains.append(domain)

        await self.db.save_preferences(user_id, domains=current_domains)

        # Refresh the picker
        await self._show_domain_picker(chat_id, user_id)

    async def _show_stars_picker(self, chat_id: int) -> None:
        """Show minimum stars selection."""

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("25+", callback_data="stars:25"),
                InlineKeyboardButton("50+", callback_data="stars:50"),
            ],
            [
                InlineKeyboardButton("100+", callback_data="stars:100"),
                InlineKeyboardButton("500+", callback_data="stars:500"),
            ],
            [
                InlineKeyboardButton("1000+", callback_data="stars:1000"),
            ],
        ])

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="⭐ *Minimum stars for projects*\n\n"
                 "Higher = more popular projects\n"
                 "Lower = newer discoveries",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    async def _set_min_stars(self, chat_id: int, user_id: str, stars: int) -> None:
        """Set minimum stars preference."""

        await self.db.save_preferences(user_id, min_stars=stars)

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Set to {stars}+ stars!",
        )

    async def _show_digest_picker(self, chat_id: int) -> None:
        """Show daily digest time selection."""

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌅 8:00 AM", callback_data="digest:08:00"),
                InlineKeyboardButton("☀️ 12:00 PM", callback_data="digest:12:00"),
            ],
            [
                InlineKeyboardButton("🌆 6:00 PM", callback_data="digest:18:00"),
                InlineKeyboardButton("🌙 9:00 PM", callback_data="digest:21:00"),
            ],
            [
                InlineKeyboardButton("🚫 Turn Off", callback_data="digest:off"),
            ],
        ])

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="⏰ *Daily Digest Time*\n\n"
                 "I'll send you trending projects automatically!\n\n"
                 "Pick a time (or turn off):",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    async def _set_digest_time(self, chat_id: int, user_id: str, time_str: str) -> None:
        """Set daily digest time."""

        if time_str == "off":
            await self.db.save_preferences(user_id, digest_time="off")
            await self.app.bot.send_message(chat_id=chat_id, text="🚫 Daily digest turned off!")
        else:
            await self.db.save_preferences(user_id, digest_time=time_str)
            await self.app.bot.send_message(chat_id=chat_id, text=f"✅ Daily digest set for {time_str}!")

    # ==================== HELPERS ====================

    async def _send_repo_card(self, chat_id: int, scored_repo: ScoredRepository, user_id: str) -> None:
        """Send a repo card with buttons."""

        repo = scored_repo.repository
        desc = (repo.description or "No description")[:80]

        # Check if already bookmarked
        is_saved = await self.db.is_bookmarked(user_id, repo.github_id)
        save_btn = InlineKeyboardButton(
            "✅ Saved" if is_saved else "⭐ Save",
            callback_data=f"save:{repo.github_id}"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💡 Get Ideas", callback_data=f"repo:{repo.github_id}"),
                save_btn,
            ],
            [
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

    async def _send_bookmark_card(self, chat_id: int, bookmark: dict, user_id: str) -> None:
        """Send a bookmark card with buttons."""

        desc = (bookmark.get("description") or "No description")[:80]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🗑️ Remove", callback_data=f"unsave:{bookmark['github_id']}"),
                InlineKeyboardButton("🔗 Open GitHub", url=bookmark["url"]),
            ]
        ])

        text = (
            f"📦 *{bookmark['name']}*\n"
            f"⭐ {bookmark['stars']:,} stars | 🔤 {bookmark.get('language') or 'Unknown'}\n\n"
            f"_{desc}_"
        )

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    async def _send_repo_with_ideas(self, chat_id: int, scored_repo: ScoredRepository, user_id: str) -> None:
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

            # Check if already bookmarked
            is_saved = await self.db.is_bookmarked(user_id, repo.github_id)
            save_btn = InlineKeyboardButton(
                "✅ Saved" if is_saved else "⭐ Save",
                callback_data=f"save:{repo.github_id}"
            )

            keyboard = InlineKeyboardMarkup([
                [save_btn, InlineKeyboardButton("🔗 Open GitHub", url=repo.url)]
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

    async def post_init(self, app) -> None:
        """Called after bot starts - initialize scheduler."""
        from src.delivery.scheduler import DigestScheduler
        self.scheduler = DigestScheduler(app)
        self.scheduler.start()
        logger.info("Daily digest scheduler started")

    def run_polling(self) -> None:
        """Start the bot!"""
        logger.info("Starting bot...")
        self.app.post_init = self.post_init
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
