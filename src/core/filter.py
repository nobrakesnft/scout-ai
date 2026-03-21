"""Rule-based repository filtering."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import structlog

from src.core.scanner import Repository

logger = structlog.get_logger(__name__)


@dataclass
class FilterConfig:
    """Configuration for repository filtering rules."""

    min_stars: int = 100
    max_days_since_update: int = 30
    min_description_length: int = 10
    require_readme: bool = True
    excluded_languages: list[str] | None = None
    excluded_topics: list[str] | None = None


class RepoFilter:
    """Filters repositories based on quality rules."""

    def __init__(self, config: FilterConfig | None = None) -> None:
        """Initialize filter with configuration."""
        self.config = config or FilterConfig()

    def filter_repos(self, repos: list[Repository]) -> list[Repository]:
        """
        Filter repositories based on quality criteria.

        Args:
            repos: List of repositories to filter

        Returns:
            Filtered list of repositories that pass all criteria
        """
        filtered = []
        for repo in repos:
            if self._passes_all_rules(repo):
                filtered.append(repo)
            else:
                logger.debug("Repository filtered out", repo=repo.full_name)

        logger.info(
            "Filtering complete",
            input_count=len(repos),
            output_count=len(filtered),
        )
        return filtered

    def _passes_all_rules(self, repo: Repository) -> bool:
        """Check if repository passes all filter rules."""
        return (
            self._check_stars(repo)
            and self._check_recency(repo)
            and self._check_description(repo)
            and self._check_readme(repo)
            and self._check_language(repo)
            and self._check_topics(repo)
        )

    def _check_stars(self, repo: Repository) -> bool:
        """Check minimum star count."""
        return repo.stars >= self.config.min_stars

    def _check_recency(self, repo: Repository) -> bool:
        """Check if repo was updated recently."""
        cutoff = datetime.now(timezone.utc) - timedelta(
            days=self.config.max_days_since_update
        )
        # Handle timezone-naive datetimes
        updated = repo.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        return updated >= cutoff

    def _check_description(self, repo: Repository) -> bool:
        """Check description quality."""
        if not repo.description:
            return False
        return len(repo.description) >= self.config.min_description_length

    def _check_readme(self, repo: Repository) -> bool:
        """Check if repo has a README."""
        if not self.config.require_readme:
            return True
        return repo.has_readme

    def _check_language(self, repo: Repository) -> bool:
        """Check if language is not excluded."""
        if not self.config.excluded_languages:
            return True
        if not repo.language:
            return True
        return repo.language.lower() not in [
            lang.lower() for lang in self.config.excluded_languages
        ]

    def _check_topics(self, repo: Repository) -> bool:
        """Check if repo doesn't have excluded topics."""
        if not self.config.excluded_topics:
            return True
        excluded = {topic.lower() for topic in self.config.excluded_topics}
        repo_topics = {topic.lower() for topic in repo.topics}
        return not bool(excluded & repo_topics)
