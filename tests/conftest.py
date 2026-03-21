"""Pytest fixtures and configuration."""

import pytest
from datetime import datetime
from pathlib import Path

from src.core.scanner import Repository


@pytest.fixture
def sample_repository() -> Repository:
    """Create a sample repository for testing."""
    return Repository(
        github_id="12345",
        name="awesome-project",
        full_name="user/awesome-project",
        description="An awesome project that does amazing things",
        url="https://github.com/user/awesome-project",
        stars=500,
        forks=50,
        language="Python",
        topics=["automation", "cli", "devtools"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2026, 3, 15),
        open_issues=10,
        watchers=100,
        has_readme=True,
    )


@pytest.fixture
def sample_repositories(sample_repository: Repository) -> list[Repository]:
    """Create a list of sample repositories."""
    repos = [sample_repository]

    # Add more varied repos
    repos.append(Repository(
        github_id="12346",
        name="cool-tool",
        full_name="org/cool-tool",
        description="A cool tool for developers",
        url="https://github.com/org/cool-tool",
        stars=1500,
        forks=200,
        language="TypeScript",
        topics=["productivity", "automation"],
        created_at=datetime(2023, 6, 1),
        updated_at=datetime(2026, 3, 18),
        open_issues=25,
        watchers=300,
        has_readme=True,
    ))

    repos.append(Repository(
        github_id="12347",
        name="data-magic",
        full_name="company/data-magic",
        description="Data processing made easy",
        url="https://github.com/company/data-magic",
        stars=200,
        forks=20,
        language="Go",
        topics=["data", "etl", "analytics"],
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2026, 3, 10),
        open_issues=5,
        watchers=50,
        has_readme=True,
    ))

    return repos


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_scout.db"
