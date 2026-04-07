"""AI-powered repository analysis and idea generation - UPGRADED for lucrative ideas."""

import json
from dataclasses import dataclass

import structlog
from openai import OpenAI

from src.config import get_settings
from src.core.scanner import Repository

logger = structlog.get_logger(__name__)


@dataclass
class BuildAssessment:
    """Assessment of how feasible it is to build this idea."""
    # Difficulty
    difficulty_level: str        # "beginner", "intermediate", "advanced", "expert"
    build_time_hours: int        # Estimated hours to build MVP
    complexity_score: int        # 1-10: Overall complexity

    # AI Buildability
    ai_buildable: bool           # Can our bot realistically build this?
    ai_confidence: int           # 1-100: How confident the AI can build it
    ai_limitations: str          # What the AI might struggle with

    # Requirements
    required_skills: list[str]   # Skills needed (e.g., "backend", "auth", "payments")
    tech_stack: list[str]        # Recommended stack (e.g., ["Python", "FastAPI", "SQLite"])
    integrations: list[str]      # External services (e.g., ["Stripe", "SendGrid"])

    # Cost Breakdown
    ai_tokens_cost: float        # Cost in $ to build with AI
    hosting_monthly: float       # Monthly hosting cost
    services_monthly: float      # Third-party services cost
    total_mvp_cost: float        # Total to get MVP running

    # Complexity Factors
    needs_auth: bool
    needs_payments: bool
    needs_database: bool
    needs_external_api: bool
    num_components: int          # Rough number of major components

    @property
    def difficulty_bar(self) -> str:
        """Visual difficulty indicator."""
        levels = {"beginner": "██░░░", "intermediate": "███░░", "advanced": "████░", "expert": "█████"}
        return levels.get(self.difficulty_level, "░░░░░")

    @property
    def time_estimate_display(self) -> str:
        """Human-readable time estimate."""
        if self.build_time_hours <= 8:
            return f"{self.build_time_hours} hours"
        elif self.build_time_hours <= 40:
            days = self.build_time_hours // 8
            return f"{days}-{days + 1} days"
        else:
            weeks = self.build_time_hours // 40
            return f"{weeks}-{weeks + 1} weeks"


@dataclass
class RepoAnalysis:
    """Deep analysis of a repository's business potential."""
    problem: str
    problem_severity: int  # 1-10: How painful is this problem?
    who_has_problem: str   # Who suffers from this?
    current_solutions: str # What do people use now?
    solution_gap: str      # What's missing in current solutions?
    solution: str
    tech_stack: list[str]
    use_cases: list[str]
    target_audience: str
    market_timing: str     # Why is NOW the right time?


@dataclass
class ProductIdea:
    """A high-potential product idea with comprehensive scoring."""
    title: str
    one_liner: str           # Elevator pitch in one line
    description: str
    target_market: str
    market_size: str         # "Millions", "Billions", etc.
    monetization: str
    price_point: str         # "$10/mo", "$99/mo", "$999/year"

    # Scoring (all 1-10)
    problem_severity: int    # How painful is the problem?
    mass_appeal: int         # How many people need this?
    viral_potential: int     # Can it spread organically?
    moat_potential: int      # Hard to copy?
    feasibility: int         # Can you build it?
    revenue_potential: int   # How much can it make?
    timing_score: int        # Is NOW the right time?

    why_now: str             # Why this idea NOW
    competition: str         # Who else does this?
    unfair_advantage: str    # What would make YOU win?
    first_customers: str     # Who are the first 10 customers?

    # Build Assessment (optional - populated when requested)
    build_assessment: BuildAssessment | None = None

    @property
    def total_score(self) -> float:
        """Calculate weighted score prioritizing lucrative potential."""
        weights = {
            'problem_severity': 2.0,   # Most important - real pain
            'mass_appeal': 1.8,        # Big market
            'revenue_potential': 1.5,  # Can make money
            'viral_potential': 1.3,    # Can grow fast
            'moat_potential': 1.2,     # Defensible
            'timing_score': 1.1,       # Right moment
            'feasibility': 1.0,        # Can build it
        }

        total = (
            self.problem_severity * weights['problem_severity'] +
            self.mass_appeal * weights['mass_appeal'] +
            self.revenue_potential * weights['revenue_potential'] +
            self.viral_potential * weights['viral_potential'] +
            self.moat_potential * weights['moat_potential'] +
            self.timing_score * weights['timing_score'] +
            self.feasibility * weights['feasibility']
        )

        max_score = sum(10 * w for w in weights.values())
        return round((total / max_score) * 100, 1)


class AIAnalyzer:
    """Analyzes repositories and generates HIGH-VALUE product ideas using AI."""

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
            self.model = "gpt-4o-mini"
            self.provider = "OpenAI"
            logger.info("Using OpenAI for AI analysis")
        else:
            raise ValueError("No AI API key configured (need DeepSeek or OpenAI)")

    def analyze_repo(self, repo: Repository) -> RepoAnalysis:
        """
        Deep analysis of a repository's business potential.
        Focus on PAIN POINTS and MARKET GAPS.
        """
        prompt = f"""You are a Y Combinator partner evaluating startup opportunities.

Analyze this GitHub repository to find BUSINESS OPPORTUNITIES, not just technical features.

Repository: {repo.full_name}
Description: {repo.description or 'No description'}
Language: {repo.language or 'Unknown'}
Topics: {', '.join(repo.topics) if repo.topics else 'None'}
Stars: {repo.stars} (indicates developer interest)
URL: {repo.url}

Think like an investor. Ask yourself:
- What PAINFUL problem does this solve?
- Who DESPERATELY needs this solved?
- What are people currently doing (and hating)?
- Why do current solutions SUCK?
- Why is NOW the perfect time for this?

Respond in JSON:
{{
    "problem": "The core problem in ONE clear sentence (not technical jargon)",
    "problem_severity": 8,  // 1-10: Would someone pay $100/mo to solve this? 10=absolutely
    "who_has_problem": "Specific people who suffer (not 'developers' - be specific like 'startup founders drowning in customer support')",
    "current_solutions": "What do people use today? What sucks about it?",
    "solution_gap": "What's MISSING that this repo could enable?",
    "solution": "How this repo approaches the problem",
    "tech_stack": ["key", "technologies"],
    "use_cases": ["real world use case 1", "use case 2", "use case 3"],
    "target_audience": "The BUYER (person with budget), not just user",
    "market_timing": "Why NOW is the right time (AI boom? Remote work? Regulation? Cost pressure?)"
}}

Be specific and commercial-minded. Think REVENUE, not just cool tech.
JSON only, no markdown."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sharp Y Combinator partner who spots billion-dollar opportunities. You think commercially, not technically. Respond only in valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=800,
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
                problem_severity=min(10, max(1, data.get("problem_severity", 5))),
                who_has_problem=data.get("who_has_problem", "Unknown"),
                current_solutions=data.get("current_solutions", "Unknown"),
                solution_gap=data.get("solution_gap", "Unknown"),
                solution=data.get("solution", "Unknown"),
                tech_stack=data.get("tech_stack", []),
                use_cases=data.get("use_cases", []),
                target_audience=data.get("target_audience", "Businesses"),
                market_timing=data.get("market_timing", "Unknown"),
            )

        except Exception as e:
            logger.warning("AI analysis failed", repo=repo.full_name, error=str(e))
            return RepoAnalysis(
                problem="Could not analyze",
                problem_severity=5,
                who_has_problem="Unknown",
                current_solutions="Unknown",
                solution_gap="Unknown",
                solution="Could not analyze",
                tech_stack=[repo.language] if repo.language else [],
                use_cases=[],
                target_audience="Developers",
                market_timing="Unknown",
            )

    def generate_ideas(self, repo: Repository, analysis: RepoAnalysis) -> list[ProductIdea]:
        """
        Generate HIGH-VALUE product ideas that solve REAL problems.
        Focus on ideas that could make $10K+ MRR.
        Includes BUILD ASSESSMENT for each idea.
        """
        prompt = f"""You are a serial entrepreneur AND technical architect who has built multiple $1M+ ARR products.

Based on this repository and analysis, generate 2 LUCRATIVE product ideas.
For each idea, also assess HOW FEASIBLE it is to build (cost, time, difficulty).

Repository: {repo.full_name}
Problem: {analysis.problem}
Problem Severity: {analysis.problem_severity}/10
Who has this problem: {analysis.who_has_problem}
Current solutions (and their gaps): {analysis.current_solutions}
What's missing: {analysis.solution_gap}
Why now: {analysis.market_timing}
Stars: {repo.stars}

RULES FOR GREAT IDEAS:
1. Solve a PAINFUL problem people ALREADY pay to solve
2. Target people with MONEY and AUTHORITY to buy
3. Must have a clear path to $10K MRR within 6 months
4. Prefer B2B or prosumer over pure consumer

For each idea, think:
- "Would I personally pay $50-500/mo for this?"
- "Can I charge from day 1?"

BUILD ASSESSMENT GUIDELINES:
- difficulty_level: "beginner" (weekend project), "intermediate" (1-2 weeks), "advanced" (1 month), "expert" (2+ months)
- build_time_hours: Realistic hours for a solo developer
- ai_buildable: Can an AI coding agent (like Cursor/Aider) build 80%+ of this?
- ai_confidence: 1-100, how confident an AI can build it autonomously
- Cost estimates should be realistic (hosting: Railway=$5, Vercel=$0-20; services: Stripe=2.9%, Auth=$0-25, etc.)

Respond in JSON:
{{
    "ideas": [
        {{
            "title": "Product Name",
            "one_liner": "X for Y that does Z",
            "description": "What it does and WHY (2-3 sentences)",
            "target_market": "Specific buyer persona",
            "market_size": "e.g., '50M freelancers worldwide'",
            "monetization": "SaaS, usage-based, etc.",
            "price_point": "$49/mo Pro, $149/mo Team",

            "problem_severity": 8,
            "mass_appeal": 7,
            "viral_potential": 6,
            "moat_potential": 7,
            "feasibility": 8,
            "revenue_potential": 8,
            "timing_score": 8,

            "why_now": "Why TODAY",
            "competition": "Competitors and weaknesses",
            "unfair_advantage": "Your edge",
            "first_customers": "First 10 customers",

            "build": {{
                "difficulty_level": "intermediate",
                "build_time_hours": 40,
                "complexity_score": 6,

                "ai_buildable": true,
                "ai_confidence": 85,
                "ai_limitations": "May need manual tweaks for payment integration",

                "required_skills": ["backend", "database", "basic frontend"],
                "tech_stack": ["Python", "FastAPI", "SQLite", "HTMX"],
                "integrations": ["Stripe", "SendGrid"],

                "ai_tokens_cost": 0.15,
                "hosting_monthly": 5,
                "services_monthly": 0,
                "total_mvp_cost": 10,

                "needs_auth": true,
                "needs_payments": true,
                "needs_database": true,
                "needs_external_api": false,
                "num_components": 5
            }}
        }}
    ]
}}

Be realistic about build complexity. Simple CRUD = beginner. Auth + payments + 3rd party APIs = advanced.
JSON only, no markdown."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a successful serial entrepreneur AND technical architect with 3 exits. You only pursue ideas with clear paths to revenue. You accurately estimate build complexity, costs, and whether AI tools can automate the build. Respond only in valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2500,
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
                # Parse build assessment if present
                build_data = idea_data.get("build", {})
                build_assessment = None
                if build_data:
                    build_assessment = BuildAssessment(
                        difficulty_level=build_data.get("difficulty_level", "intermediate"),
                        build_time_hours=build_data.get("build_time_hours", 40),
                        complexity_score=min(10, max(1, build_data.get("complexity_score", 5))),
                        ai_buildable=build_data.get("ai_buildable", False),
                        ai_confidence=min(100, max(0, build_data.get("ai_confidence", 50))),
                        ai_limitations=build_data.get("ai_limitations", "Unknown"),
                        required_skills=build_data.get("required_skills", []),
                        tech_stack=build_data.get("tech_stack", []),
                        integrations=build_data.get("integrations", []),
                        ai_tokens_cost=float(build_data.get("ai_tokens_cost", 0.10)),
                        hosting_monthly=float(build_data.get("hosting_monthly", 5)),
                        services_monthly=float(build_data.get("services_monthly", 0)),
                        total_mvp_cost=float(build_data.get("total_mvp_cost", 10)),
                        needs_auth=build_data.get("needs_auth", False),
                        needs_payments=build_data.get("needs_payments", False),
                        needs_database=build_data.get("needs_database", True),
                        needs_external_api=build_data.get("needs_external_api", False),
                        num_components=build_data.get("num_components", 3),
                    )

                idea = ProductIdea(
                    title=idea_data.get("title", "Unnamed Idea"),
                    one_liner=idea_data.get("one_liner", ""),
                    description=idea_data.get("description", "No description"),
                    target_market=idea_data.get("target_market", "Businesses"),
                    market_size=idea_data.get("market_size", "Unknown"),
                    monetization=idea_data.get("monetization", "SaaS"),
                    price_point=idea_data.get("price_point", "TBD"),
                    problem_severity=min(10, max(1, idea_data.get("problem_severity", 5))),
                    mass_appeal=min(10, max(1, idea_data.get("mass_appeal", 5))),
                    viral_potential=min(10, max(1, idea_data.get("viral_potential", 5))),
                    moat_potential=min(10, max(1, idea_data.get("moat_potential", 5))),
                    feasibility=min(10, max(1, idea_data.get("feasibility", 5))),
                    revenue_potential=min(10, max(1, idea_data.get("revenue_potential", 5))),
                    timing_score=min(10, max(1, idea_data.get("timing_score", 5))),
                    why_now=idea_data.get("why_now", ""),
                    competition=idea_data.get("competition", "Unknown"),
                    unfair_advantage=idea_data.get("unfair_advantage", ""),
                    first_customers=idea_data.get("first_customers", ""),
                    build_assessment=build_assessment,
                )
                ideas.append(idea)

            # Sort by total score (best ideas first)
            ideas.sort(key=lambda x: x.total_score, reverse=True)

            return ideas

        except Exception as e:
            logger.warning("Idea generation failed", repo=repo.full_name, error=str(e))
            return []

    def analyze_and_ideate(self, repo: Repository) -> tuple[RepoAnalysis, list[ProductIdea]]:
        """
        Full pipeline: analyze repo and generate high-value ideas.
        """
        logger.info("Analyzing repo with AI", repo=repo.full_name, provider=self.provider)

        analysis = self.analyze_repo(repo)
        ideas = self.generate_ideas(repo, analysis)

        logger.info(
            "AI analysis complete",
            repo=repo.full_name,
            ideas_generated=len(ideas),
            top_score=ideas[0].total_score if ideas else 0,
        )

        return analysis, ideas

    def filter_best_ideas(self, all_ideas: list[ProductIdea], top_n: int = 5) -> list[ProductIdea]:
        """
        Filter to only the best ideas across all repos.

        Args:
            all_ideas: All generated ideas
            top_n: Number of top ideas to return

        Returns:
            Top N ideas sorted by total score
        """
        # Sort by total weighted score
        sorted_ideas = sorted(all_ideas, key=lambda x: x.total_score, reverse=True)

        # Filter out low-quality ideas (below 60% score)
        quality_ideas = [i for i in sorted_ideas if i.total_score >= 60]

        return quality_ideas[:top_n]

    def generate_prd(self, idea_data: dict) -> str:
        """
        Generate a Product Requirements Document from an idea.

        Args:
            idea_data: Dictionary with idea details

        Returns:
            PRD as formatted text
        """
        prompt = f"""You are a senior product manager at a top tech company.

Create a concise but actionable PRD (Product Requirements Document) for this startup idea.

IDEA DETAILS:
- Title: {idea_data.get('title', 'Unknown')}
- One-liner: {idea_data.get('one_liner', '')}
- Description: {idea_data.get('description', '')}
- Target Market: {idea_data.get('target_market', '')}
- Market Size: {idea_data.get('market_size', '')}
- Monetization: {idea_data.get('monetization', '')}
- Price Point: {idea_data.get('price_point', '')}
- Why Now: {idea_data.get('why_now', '')}
- Competition: {idea_data.get('competition', '')}
- First Customers: {idea_data.get('first_customers', '')}

SCORES (1-10):
- Problem Severity: {idea_data.get('problem_severity', 5)}
- Mass Appeal: {idea_data.get('mass_appeal', 5)}
- Revenue Potential: {idea_data.get('revenue_potential', 5)}
- Viral Potential: {idea_data.get('viral_potential', 5)}
- Moat Potential: {idea_data.get('moat_potential', 5)}
- Feasibility: {idea_data.get('feasibility', 5)}

Create a PRD with these sections (keep each section focused and actionable):

1. **EXECUTIVE SUMMARY** (2-3 sentences)

2. **PROBLEM STATEMENT**
   - What specific problem are we solving?
   - Who experiences this pain?
   - How do they currently solve it?

3. **SOLUTION OVERVIEW**
   - Core value proposition
   - Key differentiators

4. **TARGET USERS**
   - Primary persona (specific description)
   - Secondary personas

5. **MVP FEATURES** (prioritized list of 5-7 features)
   - Feature name: Brief description
   - Mark as P0 (must have) or P1 (should have)

6. **SUCCESS METRICS**
   - 3-5 key metrics to track
   - Target values for launch

7. **GO-TO-MARKET**
   - Launch strategy (first 30 days)
   - Customer acquisition channels
   - Pricing strategy

8. **TECHNICAL CONSIDERATIONS**
   - Suggested tech stack
   - Key integrations needed
   - Potential technical risks

9. **TIMELINE**
   - MVP: X weeks
   - Beta: X weeks
   - Launch: X weeks

10. **NEXT STEPS** (immediate action items)

Keep it practical and focused on getting to launch fast. No fluff."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior PM who writes clear, actionable PRDs. Focus on what's needed to launch fast."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=2500,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning("PRD generation failed", error=str(e))
            return f"Failed to generate PRD: {str(e)}"
