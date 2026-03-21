"""Composite scoring algorithm for repository ranking."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import log10

import structlog

from src.core.scanner import Repository

logger = structlog.get_logger(__name__)


@dataclass
class ScoringWeights:
    """Weights for different scoring factors."""

    stars: float = 0.25
    velocity: float = 0.20  # Recent activity/growth
    engagement: float = 0.20  # Forks, watchers, issues
    freshness: float = 0.15  # How recently updated
    completeness: float = 0.10  # Has description, topics, etc.
    language_popularity: float = 0.10  # Popular languages score higher


@dataclass
class ScoredRepository:
    """Repository with computed score."""

    repository: Repository
    score: float
    score_breakdown: dict[str, float]


class RepoScorer:
    """Computes composite scores for repositories."""

    # Popular languages get a boost
    LANGUAGE_SCORES: dict[str, float] = {
        "python": 1.0,
        "typescript": 1.0,
        "javascript": 0.95,
        "rust": 0.95,
        "go": 0.90,
        "java": 0.85,
        "kotlin": 0.85,
        "swift": 0.85,
        "c#": 0.80,
        "ruby": 0.75,
    }

    def __init__(self, weights: ScoringWeights | None = None) -> None:
        """Initialize scorer with weights."""
        self.weights = weights or ScoringWeights()

    def score_repos(
        self,
        repos: list[Repository],
        top_n: int | None = None,
    ) -> list[ScoredRepository]:
        """
        Score and rank repositories.

        Args:
            repos: List of repositories to score
            top_n: Return only top N repos (optional)

        Returns:
            List of ScoredRepository sorted by score (highest first)
        """
        scored = [self._score_repo(repo) for repo in repos]
        scored.sort(key=lambda x: x.score, reverse=True)

        if top_n:
            scored = scored[:top_n]

        logger.info(
            "Scoring complete",
            total_repos=len(repos),
            returned=len(scored),
        )
        return scored

    def _score_repo(self, repo: Repository) -> ScoredRepository:
        """Compute composite score for a single repository."""
        breakdown = {
            "stars": self._score_stars(repo) * self.weights.stars,
            "velocity": self._score_velocity(repo) * self.weights.velocity,
            "engagement": self._score_engagement(repo) * self.weights.engagement,
            "freshness": self._score_freshness(repo) * self.weights.freshness,
            "completeness": self._score_completeness(repo) * self.weights.completeness,
            "language": self._score_language(repo) * self.weights.language_popularity,
        }

        total_score = sum(breakdown.values())

        return ScoredRepository(
            repository=repo,
            score=round(total_score, 3),
            score_breakdown=breakdown,
        )

    def _score_stars(self, repo: Repository) -> float:
        """Score based on star count (logarithmic scale)."""
        if repo.stars <= 0:
            return 0.0
        # Log scale: 100 stars = 0.5, 1000 = 0.75, 10000 = 1.0
        return min(1.0, log10(repo.stars) / 4)

    def _score_velocity(self, repo: Repository) -> float:
        """Score based on recent activity/growth."""
        # TODO: Implement with historical data
        # For now, use simple heuristic based on issues and recent activity
        if repo.open_issues > 50:
            return 0.8
        elif repo.open_issues > 20:
            return 0.6
        elif repo.open_issues > 5:
            return 0.4
        return 0.2

    def _score_engagement(self, repo: Repository) -> float:
        """Score based on community engagement."""
        fork_ratio = min(1.0, repo.forks / max(repo.stars, 1) * 10)
        watcher_ratio = min(1.0, repo.watchers / max(repo.stars, 1) * 5)
        issue_activity = min(1.0, repo.open_issues / 100)

        return (fork_ratio + watcher_ratio + issue_activity) / 3

    def _score_freshness(self, repo: Repository) -> float:
        """Score based on how recently updated."""
        now = datetime.now(timezone.utc)
        updated = repo.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)

        days_old = (now - updated).days

        if days_old <= 1:
            return 1.0
        elif days_old <= 7:
            return 0.9
        elif days_old <= 14:
            return 0.7
        elif days_old <= 30:
            return 0.5
        else:
            return 0.2

    def _score_completeness(self, repo: Repository) -> float:
        """Score based on repo metadata completeness."""
        score = 0.0

        if repo.description and len(repo.description) > 50:
            score += 0.4
        elif repo.description:
            score += 0.2

        if len(repo.topics) >= 3:
            score += 0.3
        elif len(repo.topics) >= 1:
            score += 0.15

        if repo.has_readme:
            score += 0.3

        return score

    def _score_language(self, repo: Repository) -> float:
        """Score based on programming language popularity."""
        if not repo.language:
            return 0.5
        return self.LANGUAGE_SCORES.get(repo.language.lower(), 0.5)
