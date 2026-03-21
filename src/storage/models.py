"""Pydantic models for database records."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IdeaStatus(str, Enum):
    """Status of a generated idea."""

    PENDING = "pending"
    APPROVED = "approved"
    SKIPPED = "skipped"
    BUILDING = "building"
    BUILT = "built"


class RepoRecord(BaseModel):
    """Database record for a discovered repository."""

    id: int | None = None
    github_id: str
    name: str
    full_name: str
    description: str | None = None
    url: str
    stars: int
    forks: int
    language: str | None = None
    topics: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    composite_score: float = 0.0
    domain: str | None = None


class AnalysisRecord(BaseModel):
    """Database record for AI analysis of a repository."""

    id: int | None = None
    repository_id: int
    problem: str
    solution: str
    tech_stack: list[str] = Field(default_factory=list)
    use_cases: list[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str
    tokens_used: int = 0


class IdeaRecord(BaseModel):
    """Database record for a generated product idea."""

    id: int | None = None
    analysis_id: int
    title: str
    description: str
    target_market: str | None = None
    monetization: str | None = None
    feasibility: int = Field(ge=1, le=10, default=5)
    uniqueness: int = Field(ge=1, le=10, default=5)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str
    status: IdeaStatus = IdeaStatus.PENDING


class RunRecord(BaseModel):
    """Database record for a pipeline run."""

    id: int | None = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    status: str = "running"
    repos_scanned: int = 0
    repos_filtered: int = 0
    repos_analyzed: int = 0
    ideas_generated: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    error_message: str | None = None


class UserPreferences(BaseModel):
    """User preferences for digest customization."""

    id: int | None = None
    telegram_id: str
    domains: list[str] = Field(default_factory=list)
    min_stars: int = 100
    digest_time: str = "08:00"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
