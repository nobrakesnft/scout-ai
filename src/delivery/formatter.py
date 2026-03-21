"""Digest and message formatting using Jinja2 templates."""

from pathlib import Path

import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core.scorer import ScoredRepository

logger = structlog.get_logger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"


class DigestFormatter:
    """Formats digests and messages using templates."""

    def __init__(self) -> None:
        """Initialize Jinja2 environment."""
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def format_daily_digest(
        self,
        repos: list[ScoredRepository],
        run_date: str,
        run_stats: dict | None = None,
    ) -> str:
        """
        Format the daily digest message.

        Args:
            repos: List of scored repositories to include
            run_date: Date string for the digest
            run_stats: Optional statistics about the run

        Returns:
            Formatted markdown message
        """
        template = self.env.get_template("digest.md.j2")
        return template.render(
            repos=repos,
            run_date=run_date,
            stats=run_stats or {},
        )

    def format_idea_card(
        self,
        title: str,
        description: str,
        target_market: str,
        feasibility: int,
        uniqueness: int,
    ) -> str:
        """Format a single idea card."""
        template = self.env.get_template("idea_card.md.j2")
        return template.render(
            title=title,
            description=description,
            target_market=target_market,
            feasibility=feasibility,
            uniqueness=uniqueness,
        )

    def format_simple_digest(self, repos: list[ScoredRepository], run_date: str) -> str:
        """
        Format a simple digest without templates (fallback).

        Args:
            repos: List of scored repositories
            run_date: Date string

        Returns:
            Formatted markdown message
        """
        lines = [
            f"🔭 *GitHub Scout Daily Digest*",
            f"📅 {run_date}",
            "",
            f"Found *{len(repos)}* interesting repositories today:",
            "",
        ]

        for i, scored in enumerate(repos, 1):
            repo = scored.repository
            lines.extend([
                f"*{i}. [{repo.name}]({repo.url})*",
                f"⭐ {repo.stars:,} | 🍴 {repo.forks:,} | 📊 Score: {scored.score:.2f}",
                f"_{repo.description[:100]}..._" if repo.description and len(repo.description) > 100 else f"_{repo.description}_",
                "",
            ])

        lines.append("─" * 30)
        lines.append("_Reply /digest for latest or /help for commands_")

        return "\n".join(lines)
