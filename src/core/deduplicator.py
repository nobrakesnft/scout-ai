"""Deduplication logic to prevent resurfacing seen repositories."""

import structlog

from src.core.scanner import Repository

logger = structlog.get_logger(__name__)


class Deduplicator:
    """Prevents duplicate repositories from being shown again."""

    def __init__(self, seen_repo_ids: set[str] | None = None) -> None:
        """
        Initialize deduplicator.

        Args:
            seen_repo_ids: Set of previously seen GitHub repo IDs
        """
        self.seen_ids: set[str] = seen_repo_ids or set()

    def deduplicate(self, repos: list[Repository]) -> list[Repository]:
        """
        Remove repositories that have already been seen.

        Args:
            repos: List of repositories to deduplicate

        Returns:
            List of new (unseen) repositories
        """
        new_repos = []
        duplicates = 0

        for repo in repos:
            if repo.github_id not in self.seen_ids:
                new_repos.append(repo)
            else:
                duplicates += 1

        logger.info(
            "Deduplication complete",
            input_count=len(repos),
            new_count=len(new_repos),
            duplicates_removed=duplicates,
        )
        return new_repos

    def mark_seen(self, repos: list[Repository]) -> None:
        """
        Mark repositories as seen.

        Args:
            repos: List of repositories to mark as seen
        """
        for repo in repos:
            self.seen_ids.add(repo.github_id)

        logger.debug("Marked repos as seen", count=len(repos))

    def load_seen_ids(self, repo_ids: set[str]) -> None:
        """Load previously seen repo IDs (e.g., from database)."""
        self.seen_ids = repo_ids
        logger.info("Loaded seen repo IDs", count=len(repo_ids))
