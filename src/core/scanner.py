"""GitHub repository scanner using REST and GraphQL APIs."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog
from github import Github, Auth
from github.GithubException import GithubException

from src.config import get_settings

logger = structlog.get_logger(__name__)


@dataclass
class Repository:
    """Represents a discovered GitHub repository."""

    github_id: str
    name: str
    full_name: str
    description: str | None
    url: str
    stars: int
    forks: int
    language: str | None
    topics: list[str]
    created_at: datetime
    updated_at: datetime
    open_issues: int
    watchers: int
    has_readme: bool = True


class GitHubScanner:
    """Scans GitHub for trending repositories across multiple domains."""

    # Domain search terms for discovering repos
    DOMAIN_SEARCHES: dict[str, list[str]] = {
        "developer-tools": ["cli", "devtools", "developer-tools"],
        "productivity": ["productivity", "automation", "workflow"],
        "ai-ml": ["machine-learning", "llm", "ai", "gpt"],
        "data": ["data-analysis", "analytics", "database"],
        "infrastructure": ["devops", "kubernetes", "docker"],
        "automation": ["automation", "bot", "scraping"],
    }

    def __init__(self) -> None:
        """Initialize the scanner with GitHub credentials."""
        settings = get_settings()
        auth = Auth.Token(settings.github_token.get_secret_value())
        self.github = Github(auth=auth)

    def scan_trending(
        self,
        domains: list[str] | None = None,
        min_stars: int = 50,
        max_results_per_domain: int = 10,
        days_back: int = 30,
    ) -> list[Repository]:
        """
        Scan GitHub for trending repositories.

        Args:
            domains: List of domain keys to search (defaults to all)
            min_stars: Minimum star count filter
            max_results_per_domain: Max repos per domain
            days_back: Only repos updated within this many days

        Returns:
            List of discovered Repository objects
        """
        domains_to_search = domains or list(self.DOMAIN_SEARCHES.keys())
        all_repos: list[Repository] = []
        seen_ids: set[str] = set()

        logger.info(
            "Starting GitHub scan",
            domains=domains_to_search,
            min_stars=min_stars,
        )

        for domain in domains_to_search:
            search_terms = self.DOMAIN_SEARCHES.get(domain, [])

            for term in search_terms[:2]:  # Limit terms per domain to avoid rate limits
                try:
                    repos = self._search_repos(
                        term=term,
                        min_stars=min_stars,
                        days_back=days_back,
                        limit=max_results_per_domain,
                    )

                    for repo in repos:
                        if repo.github_id not in seen_ids:
                            seen_ids.add(repo.github_id)
                            all_repos.append(repo)

                except GithubException as e:
                    logger.warning(
                        "GitHub API error during search",
                        term=term,
                        error=str(e),
                    )
                except Exception as e:
                    logger.error(
                        "Unexpected error during search",
                        term=term,
                        error=str(e),
                    )

        logger.info(
            "GitHub scan complete",
            total_repos=len(all_repos),
            domains_searched=len(domains_to_search),
        )

        return all_repos

    def _search_repos(
        self,
        term: str,
        min_stars: int,
        days_back: int,
        limit: int,
    ) -> list[Repository]:
        """Search for repositories matching a term."""

        # Calculate date threshold
        date_threshold = datetime.now(timezone.utc) - timedelta(days=days_back)
        date_str = date_threshold.strftime("%Y-%m-%d")

        # Build search query
        query = f"topic:{term} stars:>={min_stars} pushed:>={date_str}"

        logger.debug("Searching GitHub", query=query)

        results = self.github.search_repositories(
            query=query,
            sort="stars",
            order="desc",
        )

        repos: list[Repository] = []

        for repo in results[:limit]:
            try:
                # Check if repo has README
                has_readme = True
                try:
                    repo.get_readme()
                except:
                    has_readme = False

                repos.append(Repository(
                    github_id=str(repo.id),
                    name=repo.name,
                    full_name=repo.full_name,
                    description=repo.description,
                    url=repo.html_url,
                    stars=repo.stargazers_count,
                    forks=repo.forks_count,
                    language=repo.language,
                    topics=repo.get_topics() if repo.get_topics() else [],
                    created_at=repo.created_at,
                    updated_at=repo.updated_at,
                    open_issues=repo.open_issues_count,
                    watchers=repo.watchers_count,
                    has_readme=has_readme,
                ))
            except Exception as e:
                logger.warning(
                    "Failed to process repo",
                    repo=repo.full_name,
                    error=str(e),
                )
                continue

        logger.debug(
            "Search complete",
            term=term,
            found=len(repos),
        )

        return repos

    def get_rate_limit_status(self) -> dict[str, Any]:
        """Get current GitHub API rate limit status."""
        rate_limit = self.github.get_rate_limit()
        return {
            "remaining": rate_limit.core.remaining,
            "limit": rate_limit.core.limit,
            "reset_at": rate_limit.core.reset.isoformat(),
        }
