"""Telegram bot - Simple and friendly!"""

import asyncio
import hashlib
import io
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional

import structlog
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
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
        ).concurrent_updates(True).build()  # Allow concurrent update processing

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

        # Idea cache for approval workflow (idea_id -> {repo, idea} data)
        self.idea_cache: Dict[str, dict] = {}

        # Track users who are adding notes (user_id -> idea_id)
        self.pending_notes: Dict[str, str] = {}

        self._register_handlers()

    def _generate_idea_id(self, repo_github_id: str, idea_title: str) -> str:
        """Generate a unique ID for an idea based on repo and title."""
        content = f"{repo_github_id}:{idea_title}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _cache_idea(self, idea_id: str, repo, idea) -> None:
        """Cache an idea for later approval/skip."""
        # Build assessment data if available
        build_data = None
        if idea.build_assessment:
            ba = idea.build_assessment
            build_data = {
                "difficulty_level": ba.difficulty_level,
                "difficulty_bar": ba.difficulty_bar,
                "build_time_hours": ba.build_time_hours,
                "time_estimate_display": ba.time_estimate_display,
                "complexity_score": ba.complexity_score,
                "ai_buildable": ba.ai_buildable,
                "ai_confidence": ba.ai_confidence,
                "ai_limitations": ba.ai_limitations,
                "required_skills": ba.required_skills,
                "tech_stack": ba.tech_stack,
                "integrations": ba.integrations,
                "ai_tokens_cost": ba.ai_tokens_cost,
                "hosting_monthly": ba.hosting_monthly,
                "services_monthly": ba.services_monthly,
                "total_mvp_cost": ba.total_mvp_cost,
                "needs_auth": ba.needs_auth,
                "needs_payments": ba.needs_payments,
                "needs_database": ba.needs_database,
                "needs_external_api": ba.needs_external_api,
                "num_components": ba.num_components,
            }

        self.idea_cache[idea_id] = {
            "repo": {
                "github_id": repo.github_id,
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.url,
                "stars": repo.stars,
            },
            "idea": {
                "title": idea.title,
                "one_liner": idea.one_liner,
                "description": idea.description,
                "target_market": idea.target_market,
                "market_size": idea.market_size,
                "price_point": idea.price_point,
                "monetization": idea.monetization,
                "total_score": idea.total_score,
                "problem_severity": idea.problem_severity,
                "mass_appeal": idea.mass_appeal,
                "revenue_potential": idea.revenue_potential,
                "viral_potential": idea.viral_potential,
                "moat_potential": idea.moat_potential,
                "feasibility": idea.feasibility,
                "timing_score": idea.timing_score,
                "why_now": idea.why_now,
                "competition": idea.competition,
                "first_customers": idea.first_customers,
                "build": build_data,
            }
        }

    async def _ensure_db(self) -> None:
        """Make sure database is connected."""
        if not self._db_ready:
            await self.db.connect()
            self._db_ready = True

    def _fire_and_forget(self, coro, chat_id: int = None) -> None:
        """Run a coroutine in the background without blocking.

        This allows the bot to handle other commands while long operations run.
        Errors are logged and optionally reported to the chat.
        """
        async def wrapped():
            try:
                await coro
            except Exception as e:
                logger.exception("Background task failed", error=str(e))
                if chat_id:
                    try:
                        await self.app.bot.send_message(
                            chat_id=chat_id,
                            text=f"😕 Something went wrong: {str(e)[:50]}"
                        )
                    except:
                        pass

        asyncio.create_task(wrapped())

    # ==================== ASYNC HELPERS ====================
    # These run blocking operations in threads so the bot stays responsive

    async def _scan_trending(self, **kwargs):
        """Run scanner in background thread."""
        return await asyncio.to_thread(self.scanner.scan_trending, **kwargs)

    async def _get_repo_by_id(self, repo_id: str):
        """Fetch repo by ID in background thread."""
        return await asyncio.to_thread(self.scanner.get_repo_by_id, repo_id)

    async def _filter_repos(self, repos):
        """Filter repos in background thread."""
        return await asyncio.to_thread(self.filter.filter_repos, repos)

    async def _score_repos(self, repos, top_n: int = 5):
        """Score repos in background thread."""
        return await asyncio.to_thread(self.scorer.score_repos, repos, top_n=top_n)

    async def _analyze_repo(self, repo):
        """Run AI analysis in background thread (keeps bot responsive)."""
        return await asyncio.to_thread(self.analyzer.analyze_and_ideate, repo)

    async def _generate_prd_ai(self, idea_data: dict):
        """Run PRD generation in background thread."""
        return await asyncio.to_thread(self.analyzer.generate_prd, idea_data)

    def _register_handlers(self) -> None:
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("find", self._cmd_find))
        self.app.add_handler(CommandHandler("scan", self._cmd_find))  # alias
        self.app.add_handler(CommandHandler("ideas", self._cmd_ideas))
        self.app.add_handler(CommandHandler("web3", self._cmd_web3))
        self.app.add_handler(CommandHandler("digest", self._cmd_digest))
        self.app.add_handler(CommandHandler("saved", self._cmd_saved))
        self.app.add_handler(CommandHandler("approved", self._cmd_approved))
        self.app.add_handler(CommandHandler("settings", self._cmd_settings))
        self.app.add_handler(CommandHandler("help", self._cmd_help))
        self.app.add_handler(CommandHandler("export", self._cmd_export))
        self.app.add_handler(CallbackQueryHandler(self._handle_button))
        # Message handler for capturing notes (must be last)
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    # ==================== COMMANDS ====================

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Welcome message with prominent ideas section!"""
        await self._ensure_db()
        user_id = str(update.effective_user.id)

        # Get idea stats for the user
        counts = await self.db.get_idea_counts(user_id)
        approved_count = counts.get("approved", 0)

        # Build stats text
        stats_text = ""
        if approved_count > 0:
            stats_text = f"\n\n📊 *Your Ideas:* {approved_count} approved"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💡 Find Projects + Get Ideas", callback_data="action:ideas")],
            [InlineKeyboardButton("🔍 Find Cool Projects", callback_data="action:find")],
            [InlineKeyboardButton("🔗 Web3 / Crypto / NFT", callback_data="action:web3")],
            [
                InlineKeyboardButton("✅ My Ideas", callback_data="action:approved"),
                InlineKeyboardButton("⭐ Saved", callback_data="action:saved"),
            ],
            [InlineKeyboardButton("📫 Daily Digest (NEW projects!)", callback_data="action:digest")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="action:settings")],
        ])

        await update.message.reply_text(
            "👋 *Hi! I'm Scout Bot!*\n\n"
            "I find trending GitHub projects and turn them into *business ideas!* 💰\n\n"
            "1️⃣ Tap *Find Projects + Get Ideas*\n"
            "2️⃣ ✅ Approve ideas you like\n"
            "3️⃣ Build something great! 🚀"
            f"{stats_text}",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    async def _cmd_find(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Find cool projects - runs in background."""
        await self._ensure_db()
        user_id = str(update.effective_user.id)
        chat_id = update.message.chat_id

        # Fire and forget - bot stays responsive
        self._fire_and_forget(self._do_find(chat_id, user_id), chat_id)

    async def _cmd_ideas(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Find projects AND get ideas - runs in background."""
        await self._ensure_db()
        user_id = str(update.effective_user.id)
        chat_id = update.message.chat_id

        if not self.ai_enabled:
            await update.message.reply_text(
                "😕 AI is not set up yet.\n\n"
                "Ask the developer to add the AI key!",
            )
            return

        # Fire and forget - bot stays responsive
        self._fire_and_forget(self._do_ideas(chat_id, user_id), chat_id)

    async def _cmd_web3(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Find Web3/crypto/NFT projects - runs in background."""
        await self._ensure_db()
        user_id = str(update.effective_user.id)
        chat_id = update.message.chat_id

        # Fire and forget - bot stays responsive
        self._fire_and_forget(self._do_web3(chat_id, user_id), chat_id)

    async def _cmd_digest(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manual daily digest - runs in background."""
        await self._ensure_db()
        user_id = str(update.effective_user.id)
        chat_id = update.message.chat_id

        # Fire and forget - bot stays responsive
        self._fire_and_forget(self._do_digest(chat_id, user_id), chat_id)

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

    async def _cmd_approved(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show all approved ideas - your idea backlog!"""
        await self._ensure_db()
        user_id = str(update.effective_user.id)

        # Get counts
        counts = await self.db.get_idea_counts(user_id)
        approved_ideas = await self.db.get_approved_ideas(user_id)

        if not approved_ideas:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 Find Ideas", callback_data="action:ideas")],
            ])
            await update.message.reply_text(
                "📭 *No approved ideas yet!*\n\n"
                "Use /ideas to discover projects and get business ideas.\n"
                "Then tap ✅ Approve to save ideas you like!",
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            return

        # Header with stats and export button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Export All", callback_data="action:export")]
        ])

        await update.message.reply_text(
            f"✅ *Your Approved Ideas ({len(approved_ideas)})*\n\n"
            f"📊 Stats: {counts['approved']} approved | {counts['skipped']} skipped\n\n"
            "These are ideas you want to pursue 👇",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

        # Send each approved idea as a card
        for idea in approved_ideas:
            await self._send_approved_idea_card(update.message.chat_id, idea, user_id)

    async def _send_approved_idea_card(self, chat_id: int, idea: dict, user_id: str) -> None:
        """Send an approved idea card with remove option."""

        score = idea.get("score_total", 0)
        score_emoji = "🔥🔥🔥" if score >= 80 else "🔥🔥" if score >= 70 else "🔥" if score >= 60 else "💡"

        # Note indicator
        note_indicator = " 📝" if idea.get('notes') else ""

        lines = [
            f"✅ *{idea['idea_title']}* {score_emoji} {score:.0f}/100{note_indicator}",
            f"_{idea.get('idea_one_liner', '')}_ " if idea.get('idea_one_liner') else "",
            "",
            f"📦 From: [{idea['repo_name']}]({idea['repo_url']})",
            f"💵 {idea.get('idea_price_point', 'TBD')} | 🎯 {idea.get('idea_target_market', 'TBD')[:40]}",
            "",
            f"🔥 Pain: {idea.get('score_problem_severity', 5)} | 💰 Rev: {idea.get('score_revenue_potential', 5)} | 🚀 Viral: {idea.get('score_viral_potential', 5)}",
        ]

        lines = [l for l in lines if l]

        # Show note indicator if there's a note
        has_note = bool(idea.get('notes'))
        note_btn_text = "📝 Edit Note" if has_note else "📝 Add Note"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📋 Details", callback_data=f"details:{idea['idea_id']}"),
                InlineKeyboardButton("📄 PRD", callback_data=f"prd:{idea['idea_id']}"),
            ],
            [
                InlineKeyboardButton(note_btn_text, callback_data=f"addnote:{idea['idea_id']}"),
                InlineKeyboardButton("🗑️ Remove", callback_data=f"remove:{idea['idea_id']}"),
            ],
            [
                InlineKeyboardButton("🔗 GitHub", url=idea['repo_url']),
            ]
        ])

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="\n".join(lines),
            parse_mode="Markdown",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

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

    async def _cmd_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Export approved ideas to a markdown file."""
        await self._ensure_db()
        user_id = str(update.effective_user.id)

        approved_ideas = await self.db.get_approved_ideas(user_id)

        if not approved_ideas:
            await update.message.reply_text(
                "📭 *No approved ideas to export!*\n\n"
                "Use /ideas to discover and approve some ideas first.",
                parse_mode="Markdown",
            )
            return

        await update.message.reply_text("📤 *Generating export...*", parse_mode="Markdown")

        # Generate markdown content
        lines = [
            "# My Approved Startup Ideas",
            f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            f"*Total: {len(approved_ideas)} ideas*",
            "",
            "---",
            "",
        ]

        for i, idea in enumerate(approved_ideas, 1):
            score = idea.get("score_total", 0)
            lines.extend([
                f"## {i}. {idea['idea_title']}",
                "",
                f"**Score:** {score:.0f}/100",
                f"**One-liner:** {idea.get('idea_one_liner', 'N/A')}",
                "",
                f"### Description",
                f"{idea.get('idea_description', 'N/A')}",
                "",
                f"### Business Details",
                f"- **Target Market:** {idea.get('idea_target_market', 'N/A')}",
                f"- **Market Size:** {idea.get('idea_market_size', 'N/A')}",
                f"- **Price Point:** {idea.get('idea_price_point', 'N/A')}",
                f"- **Monetization:** {idea.get('idea_monetization', 'N/A')}",
                "",
                f"### Scores",
                f"- Problem Severity: {idea.get('score_problem_severity', 5)}/10",
                f"- Mass Appeal: {idea.get('score_mass_appeal', 5)}/10",
                f"- Revenue Potential: {idea.get('score_revenue_potential', 5)}/10",
                f"- Viral Potential: {idea.get('score_viral_potential', 5)}/10",
                f"- Moat Potential: {idea.get('score_moat_potential', 5)}/10",
                f"- Feasibility: {idea.get('score_feasibility', 5)}/10",
                f"- Timing: {idea.get('score_timing', 5)}/10",
                "",
                f"### Insights",
                f"- **Why Now:** {idea.get('why_now', 'N/A')}",
                f"- **Competition:** {idea.get('competition', 'N/A')}",
                f"- **First Customers:** {idea.get('first_customers', 'N/A')}",
                "",
                f"### Source",
                f"- **Repository:** [{idea['repo_name']}]({idea['repo_url']})",
                f"- **Stars:** {idea.get('repo_stars', 0):,}",
                "",
            ])

            # Add notes if present
            if idea.get('notes'):
                lines.extend([
                    f"### My Notes",
                    f"{idea['notes']}",
                    "",
                ])

            lines.extend(["---", ""])

        # Create file
        content = "\n".join(lines)
        file_bytes = io.BytesIO(content.encode('utf-8'))
        file_bytes.name = f"approved_ideas_{datetime.now().strftime('%Y%m%d')}.md"

        await update.message.reply_document(
            document=file_bytes,
            filename=file_bytes.name,
            caption=f"✅ *Exported {len(approved_ideas)} approved ideas!*",
            parse_mode="Markdown",
        )

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Help - keep it simple!"""

        await update.message.reply_text(
            "🤖 *How to use Scout Bot*\n\n"
            "*Commands:*\n"
            "🔍 /find - Find cool projects\n"
            "💡 /ideas - Find projects + get business ideas\n"
            "🔗 /web3 - Find crypto/NFT/blockchain projects\n"
            "📫 /digest - Your daily digest (NEW projects only!)\n"
            "⭐ /saved - See your bookmarked projects\n"
            "✅ /approved - See your approved ideas\n"
            "📤 /export - Export ideas to markdown file\n"
            "⚙️ /settings - Change your preferences\n"
            "❓ /help - See this message\n\n"
            "*How it works:*\n"
            "1️⃣ Use /ideas to find projects + get AI ideas\n"
            "2️⃣ Each idea has a score (higher = better)\n"
            "3️⃣ Tap ✅ Approve to save ideas you like\n"
            "4️⃣ Tap ⏭ Skip for ideas you don't want\n"
            "5️⃣ /approved shows your idea backlog!\n\n"
            "*Daily Digest:*\n"
            "📫 /digest shows NEW projects with AI ideas\n"
            "Approve the ones worth building!\n\n"
            "That's it! Build something great 🚀",
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

        # Action buttons - fire and forget for long operations
        if data == "action:find":
            self._fire_and_forget(self._do_find(chat_id, user_id), chat_id)

        elif data == "action:ideas":
            self._fire_and_forget(self._do_ideas(chat_id, user_id), chat_id)

        elif data == "action:web3":
            self._fire_and_forget(self._do_web3(chat_id, user_id), chat_id)

        elif data == "action:digest":
            self._fire_and_forget(self._do_digest(chat_id, user_id), chat_id)

        elif data == "action:ideas_cached":
            self._fire_and_forget(self._do_ideas_cached(chat_id, user_id), chat_id)

        elif data == "action:saved":
            await self._do_saved(chat_id, user_id)

        elif data == "action:approved":
            await self._do_approved(chat_id, user_id)

        elif data == "action:export":
            await self._do_export(chat_id, user_id)

        elif data == "action:settings":
            await self._do_settings(chat_id, user_id)

        # Repo buttons - fire and forget for AI analysis
        elif data.startswith("repo:"):
            repo_id = data.split(":")[1]
            self._fire_and_forget(self._analyze_single_repo(chat_id, repo_id, user_id), chat_id)

        # Idea approval buttons (Phase 3)
        elif data.startswith("approve:"):
            idea_id = data.split(":")[1]
            await self._approve_idea(chat_id, user_id, idea_id, query)

        elif data.startswith("skip:"):
            idea_id = data.split(":")[1]
            await self._skip_idea(chat_id, user_id, idea_id, query)

        elif data.startswith("details:"):
            idea_id = data.split(":")[1]
            await self._show_idea_details(chat_id, user_id, idea_id)

        elif data.startswith("remove:"):
            idea_id = data.split(":")[1]
            await self._remove_idea(chat_id, user_id, idea_id, query)

        elif data.startswith("addnote:"):
            idea_id = data.split(":")[1]
            await self._start_add_note(chat_id, user_id, idea_id, query)

        elif data.startswith("prd:"):
            idea_id = data.split(":")[1]
            self._fire_and_forget(self._generate_prd(chat_id, user_id, idea_id, query), chat_id)

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
            regular_repos = await self._scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=5
            )

            # Scan Web3 repos (2)
            web3_repos = await self._scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=5
            )

            # Filter and score both
            regular_filtered = await self._filter_repos(regular_repos) if regular_repos else []
            web3_filtered = await self._filter_repos(web3_repos) if web3_repos else []

            regular_scored = await self._score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = await self._score_repos(web3_filtered_deduped, top_n=2)

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
            regular_repos = await self._scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=5
            )

            # Scan Web3 repos (2)
            web3_repos = await self._scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=5
            )

            # Filter and score both
            regular_filtered = await self._filter_repos(regular_repos) if regular_repos else []
            web3_filtered = await self._filter_repos(web3_repos) if web3_repos else []

            regular_scored = await self._score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = await self._score_repos(web3_filtered_deduped, top_n=2)

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
            repos = await self._scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=10,
            )

            if not repos:
                await self.app.bot.send_message(chat_id=chat_id, text="😕 No Web3 projects found!")
                return

            filtered = await self._filter_repos(repos)
            scored = await self._score_repos(filtered, top_n=5)
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

    async def _do_digest(self, chat_id: int, user_id: str) -> None:
        """Manual daily digest - 5 regular + 5 Web3 = 10 NEW projects with AI ideas."""

        if not self.ai_enabled:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 AI not available!")
            return

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="📫 *Getting your personalized digest...*\n\n"
                 "Finding NEW projects you haven't seen + generating ideas 💡\n\n"
                 "This takes 1-2 minutes ⏳",
            parse_mode="Markdown",
        )

        try:
            # Get user preferences
            prefs = await self.db.get_preferences(user_id)
            domains = prefs.get("domains") if prefs and prefs.get("domains") else None
            min_stars = prefs.get("min_stars", 50) if prefs else 50

            # Get repos this user has already seen
            seen_ids = await self.db.get_seen_repo_ids_for_user(user_id)

            # Scan regular repos
            regular_repos = await self._scan_trending(
                domains=domains,
                min_stars=min_stars,
                max_results_per_domain=5,
            )

            # Scan Web3 repos
            web3_repos = await self._scan_trending(
                domains=["web3"],
                min_stars=25,
                max_results_per_domain=10,
            )

            # Filter out already seen repos
            regular_repos_new = [r for r in regular_repos if r.github_id not in seen_ids] if regular_repos else []
            web3_repos_new = [r for r in web3_repos if r.github_id not in seen_ids] if web3_repos else []

            # Filter and score
            regular_filtered = await self._filter_repos(regular_repos_new) if regular_repos_new else []
            web3_filtered = await self._filter_repos(web3_repos_new) if web3_repos_new else []

            regular_scored = await self._score_repos(regular_filtered, top_n=5)

            # Deduplicate: remove Web3 repos already in regular results
            regular_ids = {r.repository.github_id for r in regular_scored}
            web3_filtered_deduped = [r for r in web3_filtered if r.github_id not in regular_ids]
            web3_scored = await self._score_repos(web3_filtered_deduped, top_n=5)

            all_scored = regular_scored + web3_scored
            total_count = len(all_scored)

            if total_count == 0:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text="📫 *Daily Digest*\n\n"
                         "No NEW projects today - you've seen all the trending ones!\n\n"
                         "Check back tomorrow, or use /find to browse (may show repeats).",
                    parse_mode="Markdown",
                )
                return

            # Save to cache
            self.cache.save_scan(all_scored)

            # Send header
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"📫 *Your Daily Digest*\n\n"
                     f"Found {total_count} NEW projects with business ideas! 👇",
                parse_mode="Markdown",
            )

            # Track repos we're sending
            sent_repo_ids = []

            # Send regular repos with AI ideas
            if regular_scored:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text="🔥 *Trending Projects + Ideas*",
                    parse_mode="Markdown",
                )
                for scored_repo in regular_scored:
                    await self._send_repo_with_ideas(chat_id, scored_repo, user_id)
                    sent_repo_ids.append(scored_repo.repository.github_id)

            # Send Web3 repos with AI ideas
            if web3_scored:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text="🔗 *Web3 / Crypto Projects + Ideas*",
                    parse_mode="Markdown",
                )
                for scored_repo in web3_scored:
                    await self._send_repo_with_ideas(chat_id, scored_repo, user_id)
                    sent_repo_ids.append(scored_repo.repository.github_id)

            # Mark all sent repos as seen
            await self.db.mark_repos_as_seen(user_id, sent_repo_ids)

            # Send footer
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"✅ *{total_count} projects with {total_count * 2} business ideas!*\n\n"
                     "Use /find to explore more, /web3 for crypto, or /settings to change preferences.",
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.exception("Digest failed", error=str(e))
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

    async def _do_approved(self, chat_id: int, user_id: str) -> None:
        """Show approved ideas (triggered by button)."""

        counts = await self.db.get_idea_counts(user_id)
        approved_ideas = await self.db.get_approved_ideas(user_id)

        if not approved_ideas:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 Find Ideas", callback_data="action:ideas")],
            ])
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="📭 *No approved ideas yet!*\n\n"
                     "Use /ideas to discover projects and get business ideas.\n"
                     "Then tap ✅ Approve to save ideas you like!",
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Export All", callback_data="action:export")]
        ])

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=f"✅ *Your Approved Ideas ({len(approved_ideas)})*\n\n"
                 f"📊 Stats: {counts['approved']} approved | {counts['skipped']} skipped\n\n"
                 "These are ideas you want to pursue 👇",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

        for idea in approved_ideas:
            await self._send_approved_idea_card(chat_id, idea, user_id)

    async def _do_export(self, chat_id: int, user_id: str) -> None:
        """Export approved ideas (triggered by button)."""

        approved_ideas = await self.db.get_approved_ideas(user_id)

        if not approved_ideas:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="📭 No approved ideas to export!",
            )
            return

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="📤 *Generating export...*",
            parse_mode="Markdown",
        )

        # Generate markdown content
        lines = [
            "# My Approved Startup Ideas",
            f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            f"*Total: {len(approved_ideas)} ideas*",
            "",
            "---",
            "",
        ]

        for i, idea in enumerate(approved_ideas, 1):
            score = idea.get("score_total", 0)
            lines.extend([
                f"## {i}. {idea['idea_title']}",
                "",
                f"**Score:** {score:.0f}/100",
                f"**One-liner:** {idea.get('idea_one_liner', 'N/A')}",
                "",
                f"### Description",
                f"{idea.get('idea_description', 'N/A')}",
                "",
                f"### Business Details",
                f"- **Target Market:** {idea.get('idea_target_market', 'N/A')}",
                f"- **Market Size:** {idea.get('idea_market_size', 'N/A')}",
                f"- **Price Point:** {idea.get('idea_price_point', 'N/A')}",
                f"- **Monetization:** {idea.get('idea_monetization', 'N/A')}",
                "",
                f"### Scores",
                f"- Problem Severity: {idea.get('score_problem_severity', 5)}/10",
                f"- Mass Appeal: {idea.get('score_mass_appeal', 5)}/10",
                f"- Revenue Potential: {idea.get('score_revenue_potential', 5)}/10",
                f"- Viral Potential: {idea.get('score_viral_potential', 5)}/10",
                f"- Moat Potential: {idea.get('score_moat_potential', 5)}/10",
                f"- Feasibility: {idea.get('score_feasibility', 5)}/10",
                f"- Timing: {idea.get('score_timing', 5)}/10",
                "",
                f"### Insights",
                f"- **Why Now:** {idea.get('why_now', 'N/A')}",
                f"- **Competition:** {idea.get('competition', 'N/A')}",
                f"- **First Customers:** {idea.get('first_customers', 'N/A')}",
                "",
                f"### Source",
                f"- **Repository:** [{idea['repo_name']}]({idea['repo_url']})",
                f"- **Stars:** {idea.get('repo_stars', 0):,}",
                "",
            ])

            if idea.get('notes'):
                lines.extend([
                    f"### My Notes",
                    f"{idea['notes']}",
                    "",
                ])

            lines.extend(["---", ""])

        content = "\n".join(lines)
        file_bytes = io.BytesIO(content.encode('utf-8'))
        file_bytes.name = f"approved_ideas_{datetime.now().strftime('%Y%m%d')}.md"

        await self.app.bot.send_document(
            chat_id=chat_id,
            document=file_bytes,
            filename=file_bytes.name,
            caption=f"✅ *Exported {len(approved_ideas)} approved ideas!*",
            parse_mode="Markdown",
        )

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

    async def _analyze_single_repo(self, chat_id: int, repo_id: str, user_id: str = None) -> None:
        """Get ideas for one specific repo with approval buttons."""

        if not self.ai_enabled:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 AI not available!")
            return

        await self._ensure_db()

        # Try cache first
        repo = self.cache.get_repo(repo_id)

        # If not in cache, fetch from GitHub directly
        if not repo:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="🔍 *Fetching project from GitHub...*",
                parse_mode="Markdown",
            )
            repo = await self._get_repo_by_id(repo_id)

        if not repo:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="😕 Can't find that project. It may have been deleted or made private."
            )
            return

        await self.app.bot.send_message(
            chat_id=chat_id,
            text=f"💡 *Thinking of ideas for {repo.name}...*\n_(Bot stays responsive)_",
            parse_mode="Markdown",
        )

        try:
            # Run in background thread so bot stays responsive
            analysis, ideas = await self._analyze_repo(repo)

            # Send repo analysis header
            header_lines = [
                f"📦 *{repo.name}*",
                f"⭐ {repo.stars:,} stars | 🔗 [GitHub]({repo.url})",
                "",
                f"🔥 *Problem (Pain: {analysis.problem_severity}/10):*",
                f"{analysis.problem}",
                "",
                f"👥 *Who suffers:* {analysis.who_has_problem}",
                f"⚡ *Why NOW:* {analysis.market_timing}",
            ]

            await self.app.bot.send_message(
                chat_id=chat_id,
                text="\n".join(header_lines),
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

            # Send each idea as a separate message with buttons
            if ideas:
                for i, idea in enumerate(ideas, 1):
                    await self._send_idea_card(chat_id, user_id, repo, idea, i)
            else:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text="😕 Couldn't generate ideas for this project."
                )

        except Exception as e:
            logger.error("Analysis failed", error=str(e))
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"😕 Couldn't analyze: {str(e)[:50]}"
            )

    async def _send_idea_card(self, chat_id: int, user_id: str, repo, idea, idea_num: int) -> None:
        """Send a single idea as a card with Approve/Skip buttons."""

        # Generate unique ID and cache the idea
        idea_id = self._generate_idea_id(repo.github_id, idea.title)
        self._cache_idea(idea_id, repo, idea)

        # Score emoji and hot alert
        score = idea.total_score
        is_hot = score >= 80
        score_emoji = "🔥🔥🔥" if score >= 80 else "🔥🔥" if score >= 70 else "🔥" if score >= 60 else "💡"

        # Hot idea alert banner
        if is_hot:
            lines = [
                "⚡️ *HOT IDEA ALERT!* ⚡️",
                "",
                f"💡 *IDEA {idea_num}: {idea.title}* {score_emoji}",
                f"🏆 Score: *{score:.0f}/100* - TOP TIER!",
            ]
        else:
            lines = [
                f"💡 *IDEA {idea_num}: {idea.title}* {score_emoji}",
                f"Score: *{score:.0f}/100*",
            ]

        lines.extend([
            "",
            f"_{idea.one_liner}_" if idea.one_liner else "",
            "",
            f"{idea.description[:200]}{'...' if len(idea.description) > 200 else ''}",
            "",
            f"💵 *Price:* {idea.price_point}",
            f"🎯 *Target:* {idea.target_market[:60]}",
            f"📈 *Market:* {idea.market_size}",
            "",
            f"🔥 Pain: {idea.problem_severity} | 👥 Appeal: {idea.mass_appeal} | 💰 Rev: {idea.revenue_potential} | 🚀 Viral: {idea.viral_potential}",
        ])

        # Add BUILD ASSESSMENT if available
        if idea.build_assessment:
            ba = idea.build_assessment
            ai_status = "✅ Yes" if ba.ai_buildable else "⚠️ Partial"
            lines.extend([
                "",
                "━" * 20,
                "🔨 *BUILD ASSESSMENT*",
                f"⚡ Difficulty: {ba.difficulty_bar} {ba.difficulty_level.title()}",
                f"🕐 Time: {ba.time_estimate_display}",
                f"🤖 AI Can Build: {ai_status} ({ba.ai_confidence}%)",
                f"💵 MVP Cost: ~${ba.total_mvp_cost:.0f}",
            ])

        # Add why_now for hot ideas
        if is_hot and idea.why_now:
            lines.extend(["", f"⏰ *Why NOW:* {idea.why_now[:100]}"])

        # Filter empty lines
        lines = [l for l in lines if l]

        # Buttons for approval workflow
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve:{idea_id}"),
                InlineKeyboardButton("⏭ Skip", callback_data=f"skip:{idea_id}"),
            ],
            [
                InlineKeyboardButton("📋 Details", callback_data=f"details:{idea_id}"),
            ]
        ])

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="\n".join(lines),
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    # ==================== IDEA APPROVAL HANDLERS (Phase 3) ====================

    async def _approve_idea(self, chat_id: int, user_id: str, idea_id: str, query) -> None:
        """Approve an idea - save it to the user's approved list."""

        await self._ensure_db()

        # Get from cache
        cached = self.idea_cache.get(idea_id)
        if not cached:
            await query.answer("😕 Idea expired. Generate new ideas!", show_alert=True)
            return

        # Save to database
        await self.db.save_idea(user_id, idea_id, cached["repo"], cached["idea"])
        await self.db.update_idea_status(user_id, idea_id, "approved")

        # Update the message to show it's approved
        await query.answer("✅ Idea approved!", show_alert=False)

        # Update buttons to show approved state
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ APPROVED", callback_data="noop")],
            [InlineKeyboardButton("📋 Details", callback_data=f"details:{idea_id}")]
        ])

        try:
            await query.edit_message_reply_markup(reply_markup=keyboard)
        except:
            pass  # Message might be too old to edit

    async def _skip_idea(self, chat_id: int, user_id: str, idea_id: str, query) -> None:
        """Skip an idea - mark it as not interested."""

        await self._ensure_db()

        # Get from cache
        cached = self.idea_cache.get(idea_id)
        if not cached:
            await query.answer("😕 Idea expired.", show_alert=False)
            return

        # Save to database with skipped status
        await self.db.save_idea(user_id, idea_id, cached["repo"], cached["idea"])
        await self.db.update_idea_status(user_id, idea_id, "skipped")

        await query.answer("⏭ Skipped", show_alert=False)

        # Update buttons to show skipped state
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏭ SKIPPED", callback_data="noop")]
        ])

        try:
            await query.edit_message_reply_markup(reply_markup=keyboard)
        except:
            pass

    async def _show_idea_details(self, chat_id: int, user_id: str, idea_id: str) -> None:
        """Show full details for an idea."""

        # Try cache first
        cached = self.idea_cache.get(idea_id)

        if not cached:
            # Try database
            await self._ensure_db()
            cached = await self.db.get_idea_by_id(user_id, idea_id)
            if cached:
                # Reformat from database structure
                cached = {
                    "repo": {
                        "name": cached["repo_name"],
                        "full_name": cached["repo_full_name"],
                        "url": cached["repo_url"],
                        "stars": cached["repo_stars"],
                    },
                    "idea": {
                        "title": cached["idea_title"],
                        "one_liner": cached["idea_one_liner"],
                        "description": cached["idea_description"],
                        "target_market": cached["idea_target_market"],
                        "market_size": cached["idea_market_size"],
                        "price_point": cached["idea_price_point"],
                        "monetization": cached["idea_monetization"],
                        "total_score": cached["score_total"],
                        "problem_severity": cached["score_problem_severity"],
                        "mass_appeal": cached["score_mass_appeal"],
                        "revenue_potential": cached["score_revenue_potential"],
                        "viral_potential": cached["score_viral_potential"],
                        "moat_potential": cached["score_moat_potential"],
                        "feasibility": cached["score_feasibility"],
                        "timing_score": cached["score_timing"],
                        "why_now": cached["why_now"],
                        "competition": cached["competition"],
                        "first_customers": cached["first_customers"],
                        "notes": cached.get("notes"),
                    }
                }

        if not cached:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="😕 Can't find that idea. Try generating new ideas!"
            )
            return

        repo = cached["repo"]
        idea = cached["idea"]

        lines = [
            f"📋 *FULL DETAILS: {idea['title']}*",
            "",
            f"📦 *From:* [{repo['name']}]({repo['url']})",
            f"⭐ {repo['stars']:,} stars",
            "",
            "━" * 25,
            "",
            f"💡 *{idea['one_liner']}*" if idea.get('one_liner') else "",
            "",
            f"📝 *Description:*",
            f"{idea['description']}",
            "",
            "━" * 25,
            "",
            f"💵 *Pricing:* {idea['price_point']}",
            f"💰 *Monetization:* {idea['monetization']}",
            f"🎯 *Target Market:* {idea['target_market']}",
            f"📈 *Market Size:* {idea['market_size']}",
            "",
            "━" * 25,
            "",
            "*SCORES:*",
            f"🔥 Problem Severity: {idea['problem_severity']}/10",
            f"👥 Mass Appeal: {idea['mass_appeal']}/10",
            f"💰 Revenue Potential: {idea['revenue_potential']}/10",
            f"🚀 Viral Potential: {idea['viral_potential']}/10",
            f"🏰 Moat Potential: {idea['moat_potential']}/10",
            f"🛠 Feasibility: {idea['feasibility']}/10",
            f"⏰ Timing: {idea['timing_score']}/10",
            f"",
            f"*Total Score: {idea['total_score']:.0f}/100*",
            "",
            "━" * 25,
            "",
        ]

        if idea.get('why_now'):
            lines.extend([f"⏰ *Why NOW:*", f"{idea['why_now']}", ""])

        if idea.get('competition'):
            lines.extend([f"⚔️ *Competition:*", f"{idea['competition']}", ""])

        if idea.get('first_customers'):
            lines.extend([f"🎯 *First 10 Customers:*", f"{idea['first_customers']}", ""])

        # Show BUILD ASSESSMENT if available
        build = idea.get('build')
        if build:
            ai_status = "✅ Yes" if build.get('ai_buildable') else "⚠️ Partial"
            lines.extend([
                "━" * 25,
                "",
                "🔨 *BUILD ASSESSMENT*",
                "",
                f"⚡ *Difficulty:* {build.get('difficulty_bar', '███░░')} {build.get('difficulty_level', 'intermediate').title()}",
                f"🕐 *Build Time:* {build.get('time_estimate_display', 'Unknown')}",
                f"🧩 *Complexity:* {build.get('complexity_score', 5)}/10",
                "",
                "*🤖 AI Buildability:*",
                f"• Can Build: {ai_status}",
                f"• Confidence: {build.get('ai_confidence', 50)}%",
                f"• Limitations: {build.get('ai_limitations', 'Unknown')}",
                "",
                "*💵 COST BREAKDOWN:*",
                f"• AI Tokens: ~${build.get('ai_tokens_cost', 0.10):.2f}",
                f"• Hosting: ~${build.get('hosting_monthly', 5):.0f}/mo",
                f"• Services: ~${build.get('services_monthly', 0):.0f}/mo",
                f"• *Total MVP:* ~${build.get('total_mvp_cost', 10):.0f}",
                "",
                "*🛠️ REQUIREMENTS:*",
                f"• Stack: {', '.join(build.get('tech_stack', ['Unknown']))}",
                f"• Skills: {', '.join(build.get('required_skills', ['Unknown']))}",
                f"• Integrations: {', '.join(build.get('integrations', ['None'])) or 'None'}",
                "",
                "*📦 COMPONENTS:*",
                f"• Auth: {'✅' if build.get('needs_auth') else '❌'}",
                f"• Payments: {'✅' if build.get('needs_payments') else '❌'}",
                f"• Database: {'✅' if build.get('needs_database') else '❌'}",
                f"• External APIs: {'✅' if build.get('needs_external_api') else '❌'}",
                f"• Total Components: ~{build.get('num_components', 3)}",
                "",
            ])

        # Show user's notes if they exist
        if idea.get('notes'):
            lines.extend([
                "━" * 25,
                "",
                "📝 *Your Notes:*",
                f"{idea['notes']}",
                "",
            ])

        # Filter empty lines
        lines = [l for l in lines if l or l == ""]

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="\n".join(lines),
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )

    async def _remove_idea(self, chat_id: int, user_id: str, idea_id: str, query) -> None:
        """Remove an idea from approved list."""

        await self._ensure_db()

        removed = await self.db.remove_idea(user_id, idea_id)

        if removed:
            await query.answer("🗑️ Removed from your ideas!", show_alert=False)

            # Update the message to show it's removed
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑️ REMOVED", callback_data="noop")]
            ])

            try:
                await query.edit_message_reply_markup(reply_markup=keyboard)
            except:
                pass
        else:
            await query.answer("😕 Couldn't find that idea.", show_alert=True)

    async def _start_add_note(self, chat_id: int, user_id: str, idea_id: str, query) -> None:
        """Start the add note flow."""

        # Store that this user is adding a note to this idea
        self.pending_notes[user_id] = idea_id

        await query.answer("📝 Type your note below!", show_alert=False)

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="📝 *Add a note to this idea*\n\n"
                 "Type your note and send it.\n"
                 "_(Or send /cancel to cancel)_",
            parse_mode="Markdown",
        )

    async def _generate_prd(self, chat_id: int, user_id: str, idea_id: str, query) -> None:
        """Generate a PRD for an approved idea."""

        if not self.ai_enabled:
            await self.app.bot.send_message(chat_id=chat_id, text="😕 AI not available!")
            return

        await query.answer("📄 Generating PRD...", show_alert=False)

        await self.app.bot.send_message(
            chat_id=chat_id,
            text="📄 *Generating PRD...*\n\nThis takes about 30 seconds ⏳",
            parse_mode="Markdown",
        )

        # Get idea from cache or database
        cached = self.idea_cache.get(idea_id)

        if not cached:
            await self._ensure_db()
            db_idea = await self.db.get_idea_by_id(user_id, idea_id)
            if db_idea:
                cached = {
                    "idea": {
                        "title": db_idea["idea_title"],
                        "one_liner": db_idea["idea_one_liner"],
                        "description": db_idea["idea_description"],
                        "target_market": db_idea["idea_target_market"],
                        "market_size": db_idea["idea_market_size"],
                        "price_point": db_idea["idea_price_point"],
                        "monetization": db_idea["idea_monetization"],
                        "total_score": db_idea["score_total"],
                        "problem_severity": db_idea["score_problem_severity"],
                        "mass_appeal": db_idea["score_mass_appeal"],
                        "revenue_potential": db_idea["score_revenue_potential"],
                        "viral_potential": db_idea["score_viral_potential"],
                        "moat_potential": db_idea["score_moat_potential"],
                        "feasibility": db_idea["score_feasibility"],
                        "timing_score": db_idea["score_timing"],
                        "why_now": db_idea["why_now"],
                        "competition": db_idea["competition"],
                        "first_customers": db_idea["first_customers"],
                    }
                }

        if not cached:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text="😕 Couldn't find that idea. Try generating new ideas!"
            )
            return

        idea_data = cached["idea"]

        try:
            # Generate PRD
            prd = await self._generate_prd_ai(idea_data)

            # Send PRD (split if too long for Telegram)
            title = idea_data.get('title', 'Unknown')
            header = f"📄 *PRD: {title}*\n\n"

            # Telegram max message length is 4096
            max_length = 4000 - len(header)

            if len(prd) <= max_length:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text=header + prd,
                    parse_mode="Markdown",
                )
            else:
                # Split into multiple messages
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text=header + prd[:max_length] + "...",
                    parse_mode="Markdown",
                )
                # Send rest as plain text to avoid markdown issues
                remaining = prd[max_length:]
                while remaining:
                    chunk = remaining[:4000]
                    remaining = remaining[4000:]
                    await self.app.bot.send_message(
                        chat_id=chat_id,
                        text=chunk,
                    )

            await self.app.bot.send_message(
                chat_id=chat_id,
                text="✅ *PRD generated!* Now go build it! 🚀",
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error("PRD generation failed", error=str(e))
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"😕 Failed to generate PRD: {str(e)[:50]}"
            )

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages - used for capturing notes."""

        user_id = str(update.effective_user.id)
        chat_id = update.message.chat_id
        text = update.message.text

        # Check if user is adding a note
        if user_id in self.pending_notes:
            idea_id = self.pending_notes.pop(user_id)

            # Handle cancel
            if text.lower() == "/cancel":
                await update.message.reply_text("❌ Note cancelled.")
                return

            await self._ensure_db()

            # Save the note
            updated = await self.db.update_idea_notes(user_id, idea_id, text)

            if updated:
                await update.message.reply_text(
                    "✅ *Note saved!*\n\n"
                    f"_{text[:100]}{'...' if len(text) > 100 else ''}_\n\n"
                    "View it anytime in the idea details.",
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text("😕 Couldn't save note. Idea not found.")

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
        """Send repo + AI analysis + each idea with Approve/Skip buttons."""

        repo = scored_repo.repository

        try:
            # Run in background thread so bot stays responsive
            analysis, ideas = await self._analyze_repo(repo)

            # Check if already bookmarked
            is_saved = await self.db.is_bookmarked(user_id, repo.github_id)
            save_btn = InlineKeyboardButton(
                "✅ Saved" if is_saved else "⭐ Save",
                callback_data=f"save:{repo.github_id}"
            )

            # Send repo analysis header
            header_lines = [
                "═" * 30,
                f"📦 *{repo.name}*",
                f"⭐ {repo.stars:,} | 🔤 {repo.language or 'Unknown'} | 🔗 [GitHub]({repo.url})",
                "",
                f"🔥 *Problem (Pain: {analysis.problem_severity}/10):*",
                f"{analysis.problem}",
                "",
                f"👥 *Who suffers:* {analysis.who_has_problem[:100]}..." if len(analysis.who_has_problem) > 100 else f"👥 *Who suffers:* {analysis.who_has_problem}",
                f"⚡ *Why NOW:* {analysis.market_timing[:100]}..." if len(analysis.market_timing) > 100 else f"⚡ *Why NOW:* {analysis.market_timing}",
            ]

            header_keyboard = InlineKeyboardMarkup([
                [save_btn, InlineKeyboardButton("🔗 Open GitHub", url=repo.url)]
            ])

            await self.app.bot.send_message(
                chat_id=chat_id,
                text="\n".join(header_lines),
                parse_mode="Markdown",
                reply_markup=header_keyboard,
                disable_web_page_preview=True,
            )

            # Send each idea as a separate card with Approve/Skip buttons
            if ideas:
                for i, idea in enumerate(ideas, 1):
                    await self._send_idea_card(chat_id, user_id, repo, idea, i)
            else:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text="😕 Couldn't generate ideas for this project."
                )

        except Exception as e:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"📦 *{repo.name}* - ⚠️ Couldn't analyze",
                parse_mode="Markdown",
            )

    async def post_init(self, app) -> None:
        """Called after bot starts - initialize scheduler and set commands menu."""
        from src.delivery.scheduler import DigestScheduler
        self.scheduler = DigestScheduler(app)
        self.scheduler.start()
        logger.info("Daily digest scheduler started")

        # Set bot commands for the menu button beside chat bar
        commands = [
            BotCommand("start", "🏠 Main menu"),
            BotCommand("find", "🔍 Find cool projects"),
            BotCommand("ideas", "💡 Find projects + get ideas"),
            BotCommand("web3", "🔗 Web3/crypto/NFT projects"),
            BotCommand("digest", "📫 Your daily digest (NEW only)"),
            BotCommand("saved", "⭐ Your saved projects"),
            BotCommand("approved", "✅ Your approved ideas"),
            BotCommand("export", "📤 Export ideas to file"),
            BotCommand("settings", "⚙️ Change preferences"),
            BotCommand("help", "❓ How to use this bot"),
        ]
        await app.bot.set_my_commands(commands)
        logger.info("Bot commands menu set")

    def run_polling(self) -> None:
        """Start the bot!"""
        logger.info("Starting bot...")
        self.app.post_init = self.post_init
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
