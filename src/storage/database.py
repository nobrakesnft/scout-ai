"""SQLite database wrapper with async support."""

import json
from pathlib import Path
from typing import Any

import aiosqlite
import structlog

from src.config import get_settings
from src.storage.models import RepoRecord, AnalysisRecord, IdeaRecord, RunRecord

logger = structlog.get_logger(__name__)


class Database:
    """Async SQLite database wrapper."""

    def __init__(self, db_path: Path | None = None) -> None:
        """Initialize database connection."""
        self.db_path = db_path or get_settings().database_path
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Establish database connection."""
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row

        # Enable WAL mode for better concurrency
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")

        await self._create_tables()
        logger.info("Database connected", path=str(self.db_path))

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                description TEXT,
                url TEXT NOT NULL,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                language TEXT,
                topics TEXT DEFAULT '[]',
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                composite_score REAL DEFAULT 0.0,
                domain TEXT
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repository_id INTEGER NOT NULL,
                problem TEXT NOT NULL,
                solution TEXT NOT NULL,
                tech_stack TEXT DEFAULT '[]',
                use_cases TEXT DEFAULT '[]',
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_used TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                FOREIGN KEY (repository_id) REFERENCES repositories(id)
            );

            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                target_market TEXT,
                monetization TEXT,
                feasibility INTEGER DEFAULT 5,
                uniqueness INTEGER DEFAULT 5,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_used TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            );

            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'running',
                repos_scanned INTEGER DEFAULT 0,
                repos_filtered INTEGER DEFAULT 0,
                repos_analyzed INTEGER DEFAULT 0,
                ideas_generated INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT UNIQUE NOT NULL,
                domains TEXT DEFAULT '[]',
                min_stars INTEGER DEFAULT 100,
                digest_time TEXT DEFAULT '08:00',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_repos_github_id ON repositories(github_id);
            CREATE INDEX IF NOT EXISTS idx_repos_discovered ON repositories(discovered_at);
            CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);
            CREATE INDEX IF NOT EXISTS idx_runs_started ON runs(started_at);
        """)
        await self._connection.commit()

    async def save_repository(self, repo: RepoRecord) -> int:
        """Save a repository record, returning its ID."""
        cursor = await self._connection.execute(
            """
            INSERT INTO repositories (
                github_id, name, full_name, description, url, stars, forks,
                language, topics, created_at, updated_at, discovered_at,
                composite_score, domain
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(github_id) DO UPDATE SET
                stars = excluded.stars,
                forks = excluded.forks,
                updated_at = excluded.updated_at,
                composite_score = excluded.composite_score
            RETURNING id
            """,
            (
                repo.github_id,
                repo.name,
                repo.full_name,
                repo.description,
                repo.url,
                repo.stars,
                repo.forks,
                repo.language,
                json.dumps(repo.topics),
                repo.created_at.isoformat(),
                repo.updated_at.isoformat(),
                repo.discovered_at.isoformat(),
                repo.composite_score,
                repo.domain,
            ),
        )
        row = await cursor.fetchone()
        await self._connection.commit()
        return row["id"]

    async def get_seen_repo_ids(self) -> set[str]:
        """Get all previously seen repository GitHub IDs."""
        cursor = await self._connection.execute("SELECT github_id FROM repositories")
        rows = await cursor.fetchall()
        return {row["github_id"] for row in rows}

    async def create_run(self) -> int:
        """Create a new run record, returning its ID."""
        cursor = await self._connection.execute(
            "INSERT INTO runs DEFAULT VALUES RETURNING id"
        )
        row = await cursor.fetchone()
        await self._connection.commit()
        return row["id"]

    async def update_run(self, run_id: int, **updates: Any) -> None:
        """Update a run record with the given fields."""
        set_clauses = ", ".join(f"{k} = ?" for k in updates.keys())
        await self._connection.execute(
            f"UPDATE runs SET {set_clauses} WHERE id = ?",
            (*updates.values(), run_id),
        )
        await self._connection.commit()
