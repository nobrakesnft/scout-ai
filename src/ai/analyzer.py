"""AI-powered repository analysis and idea generation."""

import json
from dataclasses import dataclass

import structlog
from openai import OpenAI

from src.config import get_settings
from src.core.scanner import Repository

logger = structlog.get_logger(__name__)


@dataclass
class RepoAnalysis:
    """Analysis of a repository."""
    problem: str
    solution: str
    tech_stack: list[str]
    use_cases: list[str]
    target_audience: str


@dataclass
class ProductIdea:
    """A product idea generated from a repository."""
    title: str
    description: str
    target_market: str
    monetization: str
    feasibility: int  # 1-10
    uniqueness: int   # 1-10


class AIAnalyzer:
    """Analyzes repositories and generates product ideas using AI."""

    def __init__(self) -> None:
        """Initialize the AI analyzer with API clients."""
        settings = get_settings()

        # Try DeepSeek first (cheaper), fallback to OpenAI
        if settings.deepseek_api_key:
            self.client = OpenAI(
                api_key=settings.deepseek_api_key.get_secret_value(),
                base_url="https://api.deepseek.com/v1",
            )
            self.model = "deepseek-chat"
            self.provider = "DeepSeek"
            logger.info("Using DeepSeek for AI analysis")
        elif settings.openai_api_key:
            self.client = OpenAI(
                api_key=settings.openai_api_key.get_secret_value(),
            )
            self.model = "gpt-4o-mini"  # Cheaper than gpt-4
            self.provider = "OpenAI"
            logger.info("Using OpenAI for AI analysis")
        else:
            raise ValueError("No AI API key configured (need DeepSeek or OpenAI)")

    def analyze_repo(self, repo: Repository) -> RepoAnalysis:
        """
        Analyze a repository to extract problem/solution.

        Args:
            repo: Repository to analyze

        Returns:
            RepoAnalysis with extracted insights
        """
        prompt = f"""Analyze this GitHub repository and extract key insights.

Repository: {repo.full_name}
Description: {repo.description or 'No description'}
Language: {repo.language or 'Unknown'}
Topics: {', '.join(repo.topics) if repo.topics else 'None'}
Stars: {repo.stars}

Respond in JSON format:
{{
    "problem": "What problem does this repo solve? (1-2 sentences)",
    "solution": "How does it solve the problem? (1-2 sentences)",
    "tech_stack": ["list", "of", "technologies"],
    "use_cases": ["use case 1", "use case 2", "use case 3"],
    "target_audience": "Who would use this? (developers, businesses, etc)"
}}

Be concise and specific. JSON only, no markdown."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical analyst. Respond only in valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON (handle markdown code blocks if present)
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            data = json.loads(content)

            return RepoAnalysis(
                problem=data.get("problem", "Unknown"),
                solution=data.get("solution", "Unknown"),
                tech_stack=data.get("tech_stack", []),
                use_cases=data.get("use_cases", []),
                target_audience=data.get("target_audience", "Developers"),
            )

        except Exception as e:
            logger.warning("AI analysis failed", repo=repo.full_name, error=str(e))
            return RepoAnalysis(
                problem="Could not analyze",
                solution="Could not analyze",
                tech_stack=[repo.language] if repo.language else [],
                use_cases=[],
                target_audience="Developers",
            )

    def generate_ideas(self, repo: Repository, analysis: RepoAnalysis) -> list[ProductIdea]:
        """
        Generate product ideas from a repository analysis.

        Args:
            repo: The source repository
            analysis: Analysis of the repository

        Returns:
            List of ProductIdea objects (2-3 ideas)
        """
        prompt = f"""Based on this open-source repository, generate 2 product ideas that could be built.

Repository: {repo.full_name}
Problem it solves: {analysis.problem}
Solution approach: {analysis.solution}
Tech stack: {', '.join(analysis.tech_stack)}
Target audience: {analysis.target_audience}
Stars: {repo.stars}

Generate 2 REALISTIC product ideas that:
1. Build on this repo's capabilities
2. Could be monetized
3. Are feasible for a solo developer

Respond in JSON format:
{{
    "ideas": [
        {{
            "title": "Product Name",
            "description": "What it does (2 sentences max)",
            "target_market": "Who pays for it",
            "monetization": "How it makes money (SaaS, one-time, freemium)",
            "feasibility": 8,
            "uniqueness": 7
        }}
    ]
}}

Feasibility: 1=very hard, 10=easy to build
Uniqueness: 1=many competitors, 10=novel idea

JSON only, no markdown."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a startup ideation expert. Respond only in valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=800,
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            data = json.loads(content)

            ideas = []
            for idea_data in data.get("ideas", [])[:2]:
                ideas.append(ProductIdea(
                    title=idea_data.get("title", "Unnamed Idea"),
                    description=idea_data.get("description", "No description"),
                    target_market=idea_data.get("target_market", "Businesses"),
                    monetization=idea_data.get("monetization", "SaaS"),
                    feasibility=min(10, max(1, idea_data.get("feasibility", 5))),
                    uniqueness=min(10, max(1, idea_data.get("uniqueness", 5))),
                ))

            return ideas

        except Exception as e:
            logger.warning("Idea generation failed", repo=repo.full_name, error=str(e))
            return []

    def analyze_and_ideate(self, repo: Repository) -> tuple[RepoAnalysis, list[ProductIdea]]:
        """
        Full pipeline: analyze repo and generate ideas.

        Args:
            repo: Repository to process

        Returns:
            Tuple of (analysis, list of ideas)
        """
        logger.info("Analyzing repo with AI", repo=repo.full_name, provider=self.provider)

        analysis = self.analyze_repo(repo)
        ideas = self.generate_ideas(repo, analysis)

        logger.info(
            "AI analysis complete",
            repo=repo.full_name,
            ideas_generated=len(ideas),
        )

        return analysis, ideas
