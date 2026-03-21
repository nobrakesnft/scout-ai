# GitHub Scout AI - Master Product Requirements Document

**Version:** 2.0
**Date:** March 8, 2026
**Status:** Complete Vision
**Author:** AI Systems Architect

---

## Document Purpose

This is the **single source of truth** for the complete GitHub Scout AI system. It covers the full vision from discovery to autonomous building, organized into implementation phases.

**How to use this document:**
- Read fully to understand the complete vision
- Build phase by phase (don't skip ahead)
- Reference specific sections when implementing
- Update as decisions evolve

---

## Table of Contents

### Part I: Vision & Strategy
1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Target Market](#3-target-market)
4. [Solution Overview](#4-solution-overview)

### Part II: System Architecture
5. [Complete System Architecture](#5-complete-system-architecture)
6. [Agent Specifications](#6-agent-specifications)
7. [Data Architecture](#7-data-architecture)
8. [Integration Architecture](#8-integration-architecture)

### Part III: Feature Specifications
9. [Phase 1: Discovery System](#9-phase-1-discovery-system)
10. [Phase 2: Analysis System](#10-phase-2-analysis-system)
11. [Phase 3: Interaction System](#11-phase-3-interaction-system)
12. [Phase 4: Architect System](#12-phase-4-architect-system)
13. [Phase 5: Builder System](#13-phase-5-builder-system)
14. [Phase 6: Testing System](#14-phase-6-testing-system)
15. [Phase 7: Learning System](#15-phase-7-learning-system)

### Part IV: Operations
16. [Deployment Architecture](#16-deployment-architecture)
17. [Security & Compliance](#17-security--compliance)
18. [Cost Management](#18-cost-management)
19. [Monitoring & Observability](#19-monitoring--observability)

### Part V: Business & Launch
20. [Business Model](#20-business-model)
21. [Go-To-Market Strategy](#21-go-to-market-strategy)
22. [Success Metrics](#22-success-metrics)
23. [Risks & Mitigations](#23-risks--mitigations)

### Part VI: Implementation
24. [Implementation Timeline](#24-implementation-timeline)
25. [Technical Specifications](#25-technical-specifications)
26. [Appendix](#26-appendix)

---

# PART I: VISION & STRATEGY

---

## 1. Executive Summary

### 1.1 Vision Statement

**GitHub Scout AI** is an autonomous AI research assistant and builder team that works while you sleep. It continuously discovers valuable open-source repositories, analyzes them for product opportunities, and upon your approval, can prototype and test solutions automatically.

### 1.2 The Complete System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GITHUB SCOUT AI - COMPLETE VISION                    │
│                     "Your Autonomous Product Discovery Team"                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│   │  SCOUT  │───▶│ ANALYST │───▶│ IDEATOR │───▶│ARCHITECT│───▶│ BUILDER │  │
│   │         │    │         │    │         │    │         │    │         │  │
│   │ Discover│    │ Analyze │    │ Ideate  │    │ Design  │    │  Build  │  │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └────┬────┘  │
│                                                                     │       │
│                                                                     ▼       │
│   ┌─────────┐                                               ┌─────────┐    │
│   │MESSENGER│◀──────────────────────────────────────────────│ TESTER  │    │
│   │         │                                               │         │    │
│   │ Notify  │                                               │  Test   │    │
│   └─────────┘                                               └─────────┘    │
│                                                                             │
│   ════════════════════════════════════════════════════════════════════════ │
│                                                                             │
│   PHASE 1-2: Discover → Analyze → Ideate → Notify (MVP)                    │
│   PHASE 3: Add approval workflow and user interaction                      │
│   PHASE 4-6: Add Architect → Builder → Tester (Full Autonomy)              │
│   PHASE 7: Learning and continuous improvement                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Core Capabilities

| Capability | Description | Phase |
|------------|-------------|-------|
| **Discovery** | Scan GitHub daily for trending repos across 10+ domains | 1 |
| **Analysis** | Extract problems, solutions, tech stacks from repositories | 2 |
| **Ideation** | Generate actionable product ideas with market context | 2 |
| **Notification** | Deliver curated digests via Telegram | 1 |
| **Interaction** | Approve/reject ideas, configure preferences | 3 |
| **Architecture** | Design system architecture for approved ideas | 4 |
| **Building** | Clone, modify, extend repositories automatically | 5 |
| **Testing** | Run tests, verify builds, report results | 6 |
| **Learning** | Improve recommendations based on feedback | 7 |

### 1.4 PMF Validation Summary

| Dimension | Score | Notes |
|-----------|-------|-------|
| Problem Clarity | 7/10 | Clear discovery + building problem |
| Market Size | 7/10 | $100M+ TAM in founder tools |
| Uniqueness | 9/10 | Discovery → Build pipeline is novel |
| Feasibility | 6/10 | Phases 1-3 easy, 4-6 challenging |
| Monetization | 6/10 | Freemium + usage-based for building |
| Timing | 9/10 | AI agents + open source boom |
| Virality | 6/10 | Shareable ideas + built projects |
| Defensibility | 7/10 | Data moat + learned preferences + build history |
| Team Fit | 7/10 | Phases 1-3 indie-friendly |
| Ralph Factor | 9/10 | This is genuinely exciting |

**Average Score: 7.3/10**

---

## 2. Problem Statement

### 2.1 The Discovery Problem

Every day, thousands of repositories are created on GitHub. Hidden within this noise are solutions to real-world problems that could become successful products. But:

- **Information overload**: Impossible to manually track
- **Generic trending**: GitHub trending is AI-focused, not opportunity-focused
- **No ideation layer**: Existing tools show repos, not product opportunities
- **No action path**: Even when you find a good repo, what do you do with it?

### 2.2 The Building Problem

Even when founders identify opportunities:

- **Prototyping takes too long**: Days/weeks to validate an idea
- **Technical barriers**: Not everyone can build quickly
- **Context switching**: Research → Build requires mental shift
- **Testing overhead**: Setting up CI/CD for experiments is tedious

### 2.3 The Complete Problem Statement

> "Founders and builders spend too much time discovering opportunities and too much time prototyping solutions. They need an autonomous system that handles both—surfacing the best opportunities AND helping bring them to life."

### 2.4 Quantified Pain Points

| Pain Point | Current State | With GitHub Scout AI |
|------------|---------------|---------------------|
| Research time | 5-10 hrs/week | 5 mins/day (digest) |
| Idea validation | Days of research | AI analysis included |
| Time to prototype | 1-2 weeks | Hours (automated) |
| Missed opportunities | Unknown (high) | Systematic coverage |
| Context switching | Constant | Seamless pipeline |

---

## 3. Target Market

### 3.1 Market Sizing

```
TAM (Total Addressable Market): $2.5B
└── Developer tools + productivity + AI assistants market
└── 30M+ developers worldwide

SAM (Serviceable Addressable Market): $250M
└── Founders, indie hackers, product managers, agencies
└── ~5M potential users globally
└── $50/year average on research/productivity tools

SOM (Serviceable Obtainable Market): $2.5M (Year 1)
└── 1% of SAM
└── ~50,000 users (free + paid)
└── Focus: English-speaking technical founders
```

### 3.2 Primary Persona: "Indie Ian"

**Demographics:**
- Age: 25-40
- Role: Solo founder, indie hacker, side-project builder
- Technical skill: High (can code, understands systems)
- Time: Limited (job + side projects)

**Goals:**
- Find underserved markets before saturation
- Build products that solve real problems
- Validate ideas quickly with minimal effort
- Stay ahead of trends without active monitoring

**Frustrations:**
- "By the time I see a trend, it's crowded"
- "I have ideas but no time to prototype"
- "I want an AI that actually DOES things, not just suggests"

**Jobs to Be Done:**
1. When I wake up → know what's trending in open source
2. When I see a repo → understand the product opportunity
3. When I approve an idea → have it prototyped automatically
4. When a prototype is ready → see test results and next steps

### 3.3 Secondary Persona: "Agency Alex"

**Demographics:**
- Role: Technical lead at a dev agency
- Manages: Multiple client projects

**Goals:**
- Find reusable components for client work
- Prototype client ideas quickly
- Stay updated on emerging technologies

### 3.4 Tertiary Persona: "VC Victor"

**Demographics:**
- Role: Venture capitalist / angel investor

**Goals:**
- Spot trends before mainstream
- Understand what developers are building
- Identify potential investment opportunities

---

## 4. Solution Overview

### 4.1 Product Vision by Timeframe

**Year 1: The Scout + Analyst**
> Autonomous discovery and ideation system. Daily digests with AI-generated product ideas delivered via Telegram.

**Year 2: The Builder**
> Add autonomous prototyping. Approved ideas get scaffolded, extended, and tested automatically.

**Year 3: The Platform**
> Multi-source intelligence (not just GitHub), team collaboration, API access, marketplace for generated projects.

### 4.2 Core Value Propositions

| For | Value Proposition |
|-----|-------------------|
| **Discovery** | "Wake up to curated opportunities, not information overload" |
| **Analysis** | "Understand problems and solutions without reading code" |
| **Ideation** | "Get product ideas, not just repository links" |
| **Building** | "Approve an idea, wake up to a working prototype" |
| **Learning** | "The more you use it, the better it knows you" |

### 4.3 Competitive Moat Strategy

**Short-term (0-12 months):**
- Execution speed: First with complete pipeline
- User experience: Best-in-class Telegram integration
- Cost efficiency: Sustainable unit economics

**Medium-term (12-24 months):**
- Data moat: Accumulated preferences and feedback
- Build history: Library of successful prototypes
- Quality signals: Learned what makes good ideas

**Long-term (24+ months):**
- Network effects: Community sharing and rating
- Platform: Others build on our intelligence
- Institutional knowledge: Years of trend data

---

# PART II: SYSTEM ARCHITECTURE

---

## 5. Complete System Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GITHUB SCOUT AI - SYSTEM ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║                         ORCHESTRATION LAYER                           ║ │
│  ║                                                                       ║ │
│  ║   ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐  ║ │
│  ║   │  Scheduler  │    │  Pipeline   │    │    State Machine        │  ║ │
│  ║   │ (APScheduler│    │  Manager    │    │  (Approval Workflow)    │  ║ │
│  ║   │  + Cron)    │    │  (CrewAI)   │    │                         │  ║ │
│  ║   └─────────────┘    └─────────────┘    └─────────────────────────┘  ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                      │                                      │
│                                      ▼                                      │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║                          AGENT LAYER (CrewAI)                         ║ │
│  ║                                                                       ║ │
│  ║  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        ║ │
│  ║  │  SCOUT  │ │ ANALYST │ │ IDEATOR │ │ARCHITECT│ │ BUILDER │        ║ │
│  ║  │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │        ║ │
│  ║  │         │ │         │ │         │ │         │ │         │        ║ │
│  ║  │ No AI   │ │DeepSeek │ │DeepSeek │ │DeepSeek │ │DeepSeek │        ║ │
│  ║  │         │ │         │ │ / Qwen  │ │ Coder   │ │ Coder   │        ║ │
│  ║  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘        ║ │
│  ║       │           │           │           │           │              ║ │
│  ║       └───────────┴───────────┴───────────┴───────────┘              ║ │
│  ║                               │                                       ║ │
│  ║  ┌─────────┐           ┌─────────┐                                   ║ │
│  ║  │ TESTER  │           │MESSENGER│                                   ║ │
│  ║  │  Agent  │           │  Agent  │                                   ║ │
│  ║  │         │           │         │                                   ║ │
│  ║  │ No AI   │           │ No AI   │                                   ║ │
│  ║  └─────────┘           └─────────┘                                   ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                      │                                      │
│                                      ▼                                      │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║                          EXECUTION LAYER                              ║ │
│  ║                                                                       ║ │
│  ║   ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐   ║ │
│  ║   │   Sandbox     │    │    Docker     │    │   Code Executor   │   ║ │
│  ║   │  Environment  │    │   Container   │    │   (Safe Runner)   │   ║ │
│  ║   └───────────────┘    └───────────────┘    └───────────────────┘   ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                      │                                      │
│                                      ▼                                      │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║                           DATA LAYER                                  ║ │
│  ║                                                                       ║ │
│  ║   ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐   ║ │
│  ║   │    SQLite     │    │  File System  │    │   Project Store   │   ║ │
│  ║   │   Database    │    │  (Cloned Repos)│   │  (Built Projects) │   ║ │
│  ║   └───────────────┘    └───────────────┘    └───────────────────┘   ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                      │                                      │
│                                      ▼                                      │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║                        EXTERNAL SERVICES                              ║ │
│  ║                                                                       ║ │
│  ║   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ║ │
│  ║   │ GitHub  │  │Telegram │  │ OpenAI  │  │DeepSeek │  │ Claude  │  ║ │
│  ║   │   API   │  │ Bot API │  │   API   │  │   API   │  │   API   │  ║ │
│  ║   └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE DATA FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DISCOVERY FLOW (Daily, Automated)                                          │
│  ══════════════════════════════════                                         │
│                                                                             │
│  [Scheduler] ──▶ [Scout Agent] ──▶ [Filter] ──▶ [Scorer]                   │
│       │              │                              │                       │
│       │              ▼                              ▼                       │
│       │         GitHub API                    Top 5 Repos                   │
│       │         (50-100 repos)                                              │
│       │                                             │                       │
│       │                                             ▼                       │
│       │                                    [Analyst Agent]                  │
│       │                                    (DeepSeek - $0.01)               │
│       │                                             │                       │
│       │                                             ▼                       │
│       │                                    [Ideator Agent]                  │
│       │                                    (DeepSeek - $0.01)               │
│       │                                             │                       │
│       │                                             ▼                       │
│       │                                    [Messenger Agent]                │
│       │                                             │                       │
│       │                                             ▼                       │
│       │                                     TELEGRAM DIGEST                 │
│       │                                     (5 repos + ideas)               │
│       │                                                                     │
│  ═════╪═════════════════════════════════════════════════════════════════   │
│       │                                                                     │
│  APPROVAL FLOW (User-Triggered)                                             │
│  ══════════════════════════════                                             │
│       │                                                                     │
│       │     [User clicks "Approve" on Telegram]                            │
│       │                    │                                                │
│       │                    ▼                                                │
│       │            [State Machine]                                          │
│       │            (status: approved)                                       │
│       │                    │                                                │
│       │                    ▼                                                │
│       │           [Architect Agent]                                         │
│       │           (DeepSeek Coder - $0.01)                                          │
│       │                    │                                                │
│       │                    ▼                                                │
│       │           Architecture Plan                                         │
│       │           + Implementation Steps                                    │
│       │                    │                                                │
│       │                    ▼                                                │
│       │           [Send Plan to User]                                       │
│       │           "Here's how I'll build this"                             │
│       │                    │                                                │
│       │                    ▼                                                │
│       │     [User clicks "Build It" on Telegram]                           │
│       │                                                                     │
│  ═════╪═════════════════════════════════════════════════════════════════   │
│       │                                                                     │
│  BUILD FLOW (After Approval)                                                │
│  ═══════════════════════════                                                │
│       │                                                                     │
│       │            [Builder Agent]                                          │
│       │            (DeepSeek Coder - $0.02)                                         │
│       │                    │                                                │
│       │      ┌─────────────┼─────────────┐                                 │
│       │      ▼             ▼             ▼                                 │
│       │  [Clone Repo] [Modify Code] [Add Features]                         │
│       │      │             │             │                                 │
│       │      └─────────────┼─────────────┘                                 │
│       │                    ▼                                                │
│       │             [Sandbox Environment]                                   │
│       │             (Docker Container)                                      │
│       │                    │                                                │
│       │                    ▼                                                │
│       │            [Tester Agent]                                           │
│       │            (No AI - runs tests)                                     │
│       │                    │                                                │
│       │          ┌────────┴────────┐                                       │
│       │          ▼                 ▼                                        │
│       │      [PASS]            [FAIL]                                       │
│       │          │                 │                                        │
│       │          ▼                 ▼                                        │
│       │   [Package Project]  [Report Errors]                               │
│       │          │                 │                                        │
│       │          ▼                 ▼                                        │
│       │   [Notify User]      [Retry or Escalate]                           │
│       │   "Your project                                                     │
│       │    is ready!"                                                       │
│       │                                                                     │
└───────┴─────────────────────────────────────────────────────────────────────┘
```

### 5.3 Hybrid AI Strategy

**Principle: "AI as Scalpel, Not Hammer"**

| Component | Uses AI? | Model | Cost/Call | Rationale |
|-----------|----------|-------|-----------|-----------|
| Scanner | No | - | $0 | Pure API calls |
| Filter | No | - | $0 | Rule-based logic |
| Scorer | No | - | $0 | Mathematical |
| Deduplicator | No | - | $0 | Database lookup |
| **Analyst** | Yes | DeepSeek | ~$0.001 | Cheap, excellent for extraction |
| **Ideator** | Yes | DeepSeek / Qwen | ~$0.002 | Cheap, surprisingly creative |
| **Architect** | Yes | DeepSeek Coder | ~$0.002 | Cheap, good for technical planning |
| **Builder** | Yes | DeepSeek Coder / Qwen Coder | ~$0.003 | Cheap, strong code generation |
| Tester | No | - | $0 | Runs actual tests |
| Messenger | No | - | $0 | API calls only |
| Formatter | No | - | $0 | Template rendering |
| **Fallback** | Yes | GPT-4 Turbo | ~$0.03 | Only when cheap models fail |

**Cost Control Rules:**
1. AI only for tasks requiring intelligence
2. **ALWAYS use cheap models first** (DeepSeek, Qwen)
3. Expensive models (GPT-4, Claude) only as fallback when cheap models fail
4. Hard limits on tokens per run
5. Batch processing to reduce overhead
6. Cache responses to avoid duplicate API calls

**Model Priority Order:**
1. DeepSeek / DeepSeek Coder (primary - cheapest)
2. Qwen / Qwen Coder (secondary - also very cheap)
3. GPT-4 Turbo (fallback only - 10-20x more expensive)
4. Claude (last resort for complex code - expensive)

---

## 6. Agent Specifications

### 6.1 Scout Agent

**Purpose:** Discover trending and promising repositories from GitHub

**Type:** Deterministic (No AI)

**Inputs:**
- Domain categories to search
- Search parameters (date range, language filters)
- GitHub API credentials

**Outputs:**
```json
{
  "repositories": [
    {
      "id": "github_123456",
      "name": "awesome-tool",
      "full_name": "owner/awesome-tool",
      "description": "A tool that does X",
      "url": "https://github.com/owner/awesome-tool",
      "stars": 1500,
      "forks": 200,
      "language": "Python",
      "topics": ["cli", "developer-tools"],
      "created_at": "2025-01-15",
      "updated_at": "2026-03-07",
      "open_issues": 25,
      "contributors_count": 12,
      "has_readme": true,
      "license": "MIT"
    }
  ],
  "metadata": {
    "scanned_at": "2026-03-08T08:00:00Z",
    "total_found": 87,
    "domains_searched": ["dev-tools", "productivity"]
  }
}
```

**Implementation:**
```python
class ScoutAgent:
    """Discovers repositories from GitHub - NO AI NEEDED"""

    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.graphql = GitHubGraphQL(github_token)

    async def discover(self, domains: List[str], since_days: int = 7) -> List[Repository]:
        """Scan GitHub for trending repos across domains"""
        repositories = []

        for domain in domains:
            # Use GraphQL for efficient batch queries
            query = self._build_search_query(domain, since_days)
            results = await self.graphql.execute(query)
            repositories.extend(self._parse_results(results))

        return repositories

    def _build_search_query(self, domain: str, since_days: int) -> str:
        """Build GraphQL search query"""
        # Domain-specific search terms
        # Stars > 100, pushed recently, has README
        pass
```

---

### 6.2 Analyst Agent

**Purpose:** Extract problem, solution, and context from repositories

**Type:** AI-Powered (DeepSeek)

**Inputs:**
- Repository metadata
- README content
- Description

**Outputs:**
```json
{
  "repository_id": "github_123456",
  "analysis": {
    "problem_statement": "Developers struggle with X when doing Y",
    "solution_approach": "This tool provides Z to solve X",
    "key_features": [
      "Feature 1: Does A",
      "Feature 2: Enables B"
    ],
    "tech_stack": ["Python", "FastAPI", "Redis"],
    "target_users": ["Backend developers", "DevOps engineers"],
    "use_cases": [
      "Automating deployment pipelines",
      "Monitoring service health"
    ],
    "maturity_assessment": "Early but active development",
    "documentation_quality": "Good - clear README with examples"
  },
  "confidence_score": 0.85,
  "tokens_used": 1200,
  "model": "deepseek-chat"
}
```

**System Prompt:**
```
You are a technical analyst specializing in open-source software evaluation.

Given a repository's README and metadata, extract:
1. The core PROBLEM it solves (be specific, not generic)
2. The SOLUTION approach (how it solves the problem)
3. Key FEATURES (3-5 most important)
4. TECH STACK used
5. TARGET USERS (who would use this)
6. USE CASES (2-3 concrete examples)
7. MATURITY assessment (early/growing/mature)
8. DOCUMENTATION quality (poor/adequate/good/excellent)

Be concise and factual. If information is missing, say "Not specified".
Output as JSON matching the provided schema.
```

---

### 6.3 Ideator Agent

**Purpose:** Generate product ideas based on repository analysis

**Type:** AI-Powered (DeepSeek / Qwen - cheap models)

**Inputs:**
- Analyst output
- Market context (optional)
- User preferences (optional)

**Outputs:**
```json
{
  "repository_id": "github_123456",
  "ideas": [
    {
      "id": "idea_001",
      "title": "CloudDeploy Pro",
      "one_liner": "One-click deployment platform for indie hackers",
      "description": "A managed service that wraps this CLI tool...",
      "problem_solved": "Non-technical founders struggle with deployment",
      "target_market": "Indie hackers, no-code builders",
      "monetization": "Freemium: Free tier + $29/mo Pro",
      "competitive_advantage": "Simpler than Vercel, cheaper than Railway",
      "mvp_scope": [
        "GitHub integration",
        "One-click deploy button",
        "Basic dashboard"
      ],
      "feasibility_score": 8,
      "market_score": 7,
      "uniqueness_score": 6,
      "overall_score": 7.0
    }
  ],
  "tokens_used": 2500,
  "model": "deepseek-chat"
}
```

**System Prompt:**
```
You are a product strategist who identifies startup opportunities from open-source projects.

Given the analysis of a repository, generate 2-3 product ideas that:
1. Solve a REAL problem (not hypothetical)
2. Have a clear TARGET MARKET
3. Have obvious MONETIZATION potential
4. Are FEASIBLE to build (especially for solo founders)
5. Are DIFFERENTIATED from existing solutions

For each idea, provide:
- Title: Catchy product name
- One-liner: Single sentence pitch
- Description: 2-3 sentences explaining the product
- Problem solved: Specific pain point addressed
- Target market: Who would pay for this
- Monetization: How to make money (be specific on pricing)
- Competitive advantage: Why this beats alternatives
- MVP scope: 3-5 features for first version
- Scores: Feasibility (1-10), Market (1-10), Uniqueness (1-10)

Think like an indie hacker: prefer simple, profitable, bootstrappable ideas.
Output as JSON matching the provided schema.
```

---

### 6.4 Architect Agent

**Purpose:** Design implementation architecture for approved ideas

**Type:** AI-Powered (DeepSeek Coder - cheap model)

**Inputs:**
- Approved idea
- Repository analysis
- User's technical preferences (optional)

**Outputs:**
```json
{
  "idea_id": "idea_001",
  "architecture": {
    "overview": "Microservices architecture with React frontend...",
    "components": [
      {
        "name": "API Gateway",
        "technology": "FastAPI",
        "responsibility": "Handle all incoming requests",
        "dependencies": ["Auth Service", "Deploy Service"]
      },
      {
        "name": "Deploy Service",
        "technology": "Python + Docker SDK",
        "responsibility": "Manage container deployments",
        "dependencies": ["Docker", "Cloud Provider SDK"]
      }
    ],
    "tech_stack": {
      "frontend": "React + TypeScript + Tailwind",
      "backend": "FastAPI + Python 3.11",
      "database": "PostgreSQL + Redis",
      "infrastructure": "Docker + Railway",
      "auth": "Supabase Auth"
    },
    "implementation_steps": [
      {
        "step": 1,
        "title": "Project Setup",
        "description": "Initialize monorepo with frontend and backend",
        "files_to_create": ["package.json", "pyproject.toml", "docker-compose.yml"],
        "estimated_complexity": "low"
      },
      {
        "step": 2,
        "title": "Core API",
        "description": "Implement deployment endpoints",
        "files_to_create": ["api/main.py", "api/routes/deploy.py"],
        "estimated_complexity": "medium"
      }
    ],
    "from_repository": {
      "files_to_keep": ["src/core/", "src/utils/"],
      "files_to_modify": ["src/cli.py → src/api.py"],
      "files_to_remove": ["tests/", "docs/"]
    }
  },
  "tokens_used": 3500,
  "model": "deepseek-coder"
}
```

**System Prompt:**
```
You are a senior software architect specializing in rapid prototyping.

Given an approved product idea and its source repository, design:
1. High-level ARCHITECTURE (keep it simple, avoid over-engineering)
2. COMPONENTS and their responsibilities
3. TECH STACK choices with rationale
4. IMPLEMENTATION STEPS (ordered, specific)
5. How to TRANSFORM the source repository into the product

Design principles:
- Prefer boring technology (proven, well-documented)
- Minimize dependencies
- Optimize for solo developer workflow
- Make it deployable on Railway
- Keep it modular for future iteration

For repository transformation:
- Identify files to KEEP (core logic)
- Identify files to MODIFY (adapt for product)
- Identify files to REMOVE (unnecessary for MVP)

Output as JSON matching the provided schema.
```

---

### 6.5 Builder Agent

**Purpose:** Execute the implementation plan by writing and modifying code

**Type:** AI-Powered (DeepSeek Coder / Qwen Coder - cheap models)

**Inputs:**
- Architecture plan
- Cloned repository
- Step to execute

**Outputs:**
```json
{
  "step_id": 1,
  "status": "completed",
  "actions_taken": [
    {
      "type": "create_file",
      "path": "api/main.py",
      "content": "...",
      "lines": 45
    },
    {
      "type": "modify_file",
      "path": "requirements.txt",
      "changes": "Added fastapi, uvicorn"
    }
  ],
  "files_created": ["api/main.py", "api/__init__.py"],
  "files_modified": ["requirements.txt"],
  "next_step": 2,
  "notes": "Created base FastAPI app with health endpoint",
  "tokens_used": 4500,
  "model": "deepseek-coder"
}
```

**System Prompt:**
```
You are an expert software developer executing a build plan.

You are given:
1. An ARCHITECTURE PLAN with specific steps
2. The current STEP to execute
3. The REPOSITORY contents

Your job:
1. Execute ONLY the current step (don't do extra work)
2. Write PRODUCTION-QUALITY code
3. Follow best practices for the tech stack
4. Add minimal but clear comments
5. Handle errors gracefully
6. Report what you did

Code principles:
- Write simple, readable code
- No over-engineering
- Follow existing code style
- Include type hints (Python) or types (TypeScript)
- Add basic error handling

Output:
- List of files created/modified
- The actual code content
- Any notes or warnings
- Confirmation of completion

IMPORTANT: Only execute the current step. Do not anticipate future steps.
```

**Safety Rules:**
1. Never delete existing files without explicit instruction
2. Never modify files outside the project directory
3. Never execute arbitrary shell commands
4. Never include credentials or secrets in code
5. Always validate generated code syntax before saving

---

### 6.6 Tester Agent

**Purpose:** Run tests and verify builds

**Type:** Deterministic (No AI)

**Inputs:**
- Project directory
- Test configuration
- Build commands

**Outputs:**
```json
{
  "project_id": "proj_001",
  "test_results": {
    "status": "passed",
    "total_tests": 12,
    "passed": 12,
    "failed": 0,
    "skipped": 0,
    "duration_seconds": 34.5,
    "coverage_percent": 78.5
  },
  "build_results": {
    "status": "success",
    "build_time_seconds": 45.2,
    "output_size_mb": 12.3,
    "warnings": ["Deprecated API usage in line 45"]
  },
  "lint_results": {
    "status": "passed",
    "errors": 0,
    "warnings": 3
  },
  "overall_status": "ready",
  "deployment_ready": true
}
```

**Implementation:**
```python
class TesterAgent:
    """Runs tests and verifies builds - NO AI NEEDED"""

    def __init__(self, sandbox: SandboxEnvironment):
        self.sandbox = sandbox

    async def run_tests(self, project_path: str) -> TestResults:
        """Execute test suite in sandbox"""
        # Detect test framework (pytest, jest, go test, etc.)
        framework = self._detect_test_framework(project_path)

        # Run tests in isolated container
        result = await self.sandbox.execute(
            command=framework.test_command,
            timeout=300,  # 5 minutes max
            capture_output=True
        )

        return self._parse_test_output(result)

    async def verify_build(self, project_path: str) -> BuildResults:
        """Attempt to build the project"""
        # Detect build system
        build_system = self._detect_build_system(project_path)

        # Run build in isolated container
        result = await self.sandbox.execute(
            command=build_system.build_command,
            timeout=600,  # 10 minutes max
            capture_output=True
        )

        return self._parse_build_output(result)
```

---

### 6.7 Messenger Agent

**Purpose:** Handle all Telegram communications

**Type:** Deterministic (No AI)

**Inputs:**
- Message content
- Message type (digest, notification, approval request)
- User preferences

**Outputs:**
- Sent message confirmation
- User response capture

**Telegram Commands:**
```
/start        - Initialize bot, show welcome
/digest       - Get latest digest on demand
/history      - View past discoveries (paginated)
/approved     - View approved ideas and their status
/settings     - Configure preferences
/help         - Show available commands
/status       - Show system status and current builds
```

**Message Templates:**

**Daily Digest:**
```markdown
🔍 **GitHub Scout AI - Daily Digest**
📅 March 8, 2026

Found **5 promising repositories** today:

━━━━━━━━━━━━━━━━━━━━━━

**1. owner/repo-name** ⭐ 1,234
Python | Updated 2 days ago

📋 **Problem:** Developers struggle with X
💡 **Solution:** Provides Y to solve X

🎯 **Product Idea: ProductName**
One-liner description here

Feasibility: ████████░░ 8/10
Market: ███████░░░ 7/10

[Approve] [Skip] [Details]

━━━━━━━━━━━━━━━━━━━━━━

... (repeat for 5 repos)

━━━━━━━━━━━━━━━━━━━━━━

📊 Today's stats:
• Scanned: 87 repos
• Filtered to: 15
• Analyzed: 5
• AI Cost: $0.16

⏰ Next digest: Tomorrow 8:00 AM UTC
```

**Build Status Update:**
```markdown
🔨 **Build Update: ProductName**

Status: ✅ COMPLETED

📦 Project ready:
• 12 files created
• 3 files modified
• All tests passing (15/15)
• Build successful

🚀 **Next steps:**
1. Review the code
2. Deploy to Railway
3. Test manually

[View Code] [Deploy] [Discard]
```

---

## 7. Data Architecture

### 7.1 Database Schema

```sql
-- =============================================
-- GITHUB SCOUT AI - DATABASE SCHEMA
-- SQLite (Railway Volume)
-- =============================================

-- Discovered repositories
CREATE TABLE repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    language TEXT,
    topics JSON,
    created_at DATETIME,
    updated_at DATETIME,
    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    composite_score REAL,
    domain TEXT,

    INDEX idx_github_id (github_id),
    INDEX idx_discovered_at (discovered_at),
    INDEX idx_composite_score (composite_score)
);

-- AI analyses of repositories
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    problem_statement TEXT,
    solution_approach TEXT,
    key_features JSON,
    tech_stack JSON,
    target_users JSON,
    use_cases JSON,
    maturity_assessment TEXT,
    documentation_quality TEXT,
    confidence_score REAL,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_used TEXT,
    tokens_used INTEGER,

    FOREIGN KEY (repository_id) REFERENCES repositories(id),
    INDEX idx_repository_id (repository_id)
);

-- Generated product ideas
CREATE TABLE ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    one_liner TEXT,
    description TEXT,
    problem_solved TEXT,
    target_market TEXT,
    monetization TEXT,
    competitive_advantage TEXT,
    mvp_scope JSON,
    feasibility_score INTEGER,
    market_score INTEGER,
    uniqueness_score INTEGER,
    overall_score REAL,
    status TEXT DEFAULT 'pending',  -- pending, approved, rejected, building, completed
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    model_used TEXT,
    tokens_used INTEGER,

    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_status (status)
);

-- Architecture plans for approved ideas
CREATE TABLE architectures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL,
    overview TEXT,
    components JSON,
    tech_stack JSON,
    implementation_steps JSON,
    repository_transform JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_used TEXT,
    tokens_used INTEGER,

    FOREIGN KEY (idea_id) REFERENCES ideas(id),
    INDEX idx_idea_id (idea_id)
);

-- Build projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    architecture_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, cloning, building, testing, completed, failed
    source_repo_url TEXT,
    local_path TEXT,
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER,
    started_at DATETIME,
    completed_at DATETIME,
    error_message TEXT,

    FOREIGN KEY (architecture_id) REFERENCES architectures(id),
    INDEX idx_architecture_id (architecture_id),
    INDEX idx_status (status)
);

-- Build steps log
CREATE TABLE build_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    title TEXT,
    status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
    actions_taken JSON,
    files_created JSON,
    files_modified JSON,
    started_at DATETIME,
    completed_at DATETIME,
    model_used TEXT,
    tokens_used INTEGER,
    error_message TEXT,

    FOREIGN KEY (project_id) REFERENCES projects(id),
    INDEX idx_project_id (project_id)
);

-- Test results
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    status TEXT,  -- passed, failed, skipped
    total_tests INTEGER,
    passed INTEGER,
    failed INTEGER,
    skipped INTEGER,
    duration_seconds REAL,
    coverage_percent REAL,
    output TEXT,
    tested_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id),
    INDEX idx_project_id (project_id)
);

-- Pipeline runs (for monitoring)
CREATE TABLE runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type TEXT NOT NULL,  -- discovery, analysis, build
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    status TEXT DEFAULT 'running',  -- running, completed, failed
    repos_scanned INTEGER,
    repos_filtered INTEGER,
    repos_analyzed INTEGER,
    ideas_generated INTEGER,
    total_tokens INTEGER,
    total_cost REAL,
    error_message TEXT,

    INDEX idx_started_at (started_at),
    INDEX idx_status (status)
);

-- User preferences
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT UNIQUE NOT NULL,
    domains JSON DEFAULT '["dev-tools", "productivity", "ai-ml"]',
    min_stars INTEGER DEFAULT 100,
    digest_time TEXT DEFAULT '08:00',
    digest_timezone TEXT DEFAULT 'UTC',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_telegram_id (telegram_id)
);

-- Feedback for learning
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL,
    action TEXT NOT NULL,  -- approved, rejected, built, abandoned
    feedback_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    FOREIGN KEY (idea_id) REFERENCES ideas(id),
    INDEX idx_idea_id (idea_id)
);
```

### 7.2 File Storage Structure

```
/data/                              # Railway Volume
├── scout.db                        # SQLite database
├── repos/                          # Cloned repositories
│   ├── proj_001/
│   │   ├── .git/
│   │   ├── src/
│   │   └── ...
│   └── proj_002/
├── builds/                         # Built projects
│   ├── proj_001_build/
│   │   ├── dist/
│   │   └── ...
│   └── proj_002_build/
├── logs/                           # Execution logs
│   ├── runs/
│   ├── builds/
│   └── errors/
└── cache/                          # Temporary cache
    ├── readme_cache/
    └── api_cache/
```

---

## 8. Integration Architecture

### 8.1 External APIs

| Service | Purpose | Authentication | Rate Limits |
|---------|---------|----------------|-------------|
| GitHub REST | Repository metadata | PAT | 5,000/hr |
| GitHub GraphQL | Batch queries | PAT | 5,000 points/hr |
| Telegram Bot | Messaging | Bot Token | 30 msg/sec |
| DeepSeek | Primary for all AI tasks | API Key | 1M tokens/day |
| Qwen (Alibaba) | Secondary/backup | API Key | Generous limits |
| OpenAI | Fallback only | API Key | Tier-based |
| Anthropic | Last resort fallback | API Key | Tier-based |

### 8.2 Integration Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   API GATEWAY                            │   │
│  │                                                          │   │
│  │  • Rate limiting (per service)                          │   │
│  │  • Retry with exponential backoff                       │   │
│  │  • Circuit breaker (fail fast)                          │   │
│  │  • Response caching (15 min TTL)                        │   │
│  │  • Request logging                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│  │   GitHub    │     │  AI Models  │     │  Telegram   │      │
│  │   Client    │     │   Client    │     │   Client    │      │
│  │             │     │             │     │             │      │
│  │ • REST API  │     │ • OpenAI    │     │ • Send msgs │      │
│  │ • GraphQL   │     │ • DeepSeek  │     │ • Webhooks  │      │
│  │ • Caching   │     │ • Anthropic │     │ • Callbacks │      │
│  └─────────────┘     └─────────────┘     └─────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 Error Handling Strategy

| Error Type | Strategy | Notification |
|------------|----------|--------------|
| Rate limit exceeded | Exponential backoff, retry | Log only |
| API timeout | Retry 3x, then skip | Log only |
| AI model error | Fallback to cheaper model | Log only |
| Build failure | Stop, report to user | Telegram alert |
| Test failure | Report details to user | Telegram alert |
| Critical system error | Alert immediately | Telegram + Log |

---

# PART III: FEATURE SPECIFICATIONS

---

## 9. Phase 1: Discovery System

### 9.1 Overview

**Goal:** Automatically discover trending and promising repositories from GitHub daily.

**Components:**
- Scout Agent (scanner)
- Filter Engine
- Scorer
- Deduplicator
- Basic Telegram notification

**Dependencies:** None (first phase)

### 9.2 Detailed Requirements

#### 9.2.1 GitHub Scanner

**Functional Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| DISC-001 | Scan GitHub trending page daily | P0 |
| DISC-002 | Search across 10+ domain categories | P0 |
| DISC-003 | Support multiple programming languages | P0 |
| DISC-004 | Use GraphQL for efficient batching | P0 |
| DISC-005 | Cache results to reduce API calls | P1 |
| DISC-006 | Handle rate limiting gracefully | P0 |

**Domain Categories:**
```python
DOMAINS = {
    "dev-tools": ["cli", "developer-tools", "devtools", "sdk"],
    "productivity": ["productivity", "automation", "workflow"],
    "ai-ml": ["machine-learning", "llm", "ai", "nlp", "deep-learning"],
    "data": ["data-analysis", "analytics", "etl", "database"],
    "infrastructure": ["devops", "kubernetes", "monitoring", "cloud"],
    "fintech": ["payments", "crypto", "trading", "finance"],
    "healthcare": ["health", "medical", "telemedicine"],
    "education": ["learning", "education", "tutorial"],
    "automation": ["automation", "bots", "scraping", "rpa"],
    "security": ["security", "privacy", "encryption", "auth"]
}
```

#### 9.2.2 Filter Engine

**Filter Rules:**
```python
FILTER_RULES = {
    "min_stars": 100,
    "max_age_days": 365,          # Created within last year
    "min_recent_activity_days": 30,  # Updated within 30 days
    "min_contributors": 2,
    "has_readme": True,
    "has_license": True,
    "excluded_topics": ["awesome-list", "tutorial", "course"],
    "excluded_names": ["awesome-", "learn-", "interview-"]
}
```

#### 9.2.3 Scorer

**Composite Scoring Algorithm:**
```python
def calculate_score(repo: Repository) -> float:
    """
    Score = (Stars × 0.25) + (Activity × 0.25) + (Growth × 0.30) + (Quality × 0.20)

    Stars Score (0-10):
        - 100-500: 4
        - 500-1000: 6
        - 1000-5000: 8
        - 5000+: 10

    Activity Score (0-10):
        - Based on commits in last 30 days
        - Issues closed / opened ratio
        - PR merge rate

    Growth Score (0-10):
        - Star velocity (stars gained per week)
        - Fork velocity
        - Contributor growth

    Quality Score (0-10):
        - README completeness
        - Documentation presence
        - Test presence
        - CI/CD presence
    """
    stars_score = calculate_stars_score(repo.stars)
    activity_score = calculate_activity_score(repo)
    growth_score = calculate_growth_score(repo)
    quality_score = calculate_quality_score(repo)

    return (
        stars_score * 0.25 +
        activity_score * 0.25 +
        growth_score * 0.30 +
        quality_score * 0.20
    )
```

### 9.3 User Stories

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| P1-001 | As a founder, I want the system to scan GitHub daily | Scheduled job runs at 8 AM UTC |
| P1-002 | As a founder, I want repos filtered by quality | Only repos meeting filter rules pass |
| P1-003 | As a founder, I want multi-domain coverage | At least 5 domains searched per run |
| P1-004 | As a founder, I want to see top 5 repos | Ranked by composite score |
| P1-005 | As a founder, I want daily Telegram messages | Digest sent after each run |
| P1-006 | As a founder, I want no duplicate repos | Deduplication is 100% accurate |

### 9.4 Technical Implementation

**Files to Create:**
```
src/
├── core/
│   ├── __init__.py
│   ├── scanner.py          # GitHub API integration
│   ├── filter.py           # Rule-based filtering
│   ├── scorer.py           # Composite scoring
│   └── deduplicator.py     # History checking
├── delivery/
│   ├── __init__.py
│   ├── telegram_bot.py     # Basic bot setup
│   └── templates/
│       └── simple_digest.md.j2
├── storage/
│   ├── __init__.py
│   └── database.py         # SQLite setup
├── config.py
└── main.py
```

### 9.5 Exit Criteria

- [ ] Scanner discovers 50+ repos per run
- [ ] Filter reduces to 10-20 quality repos
- [ ] Scorer ranks repos consistently
- [ ] Top 5 repos sent to Telegram
- [ ] No duplicates across runs
- [ ] Deployed on Railway
- [ ] Runs daily without intervention

---

## 10. Phase 2: Analysis System

### 10.1 Overview

**Goal:** Use AI to analyze repositories and generate product ideas.

**Components:**
- Analyst Agent (DeepSeek)
- Ideator Agent (GPT-4)
- Enhanced Telegram digest

**Dependencies:** Phase 1 completed

### 10.2 Detailed Requirements

#### 10.2.1 Analyst Agent

**Functional Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| ANAL-001 | Fetch and parse README content | P0 |
| ANAL-002 | Extract problem statement | P0 |
| ANAL-003 | Extract solution approach | P0 |
| ANAL-004 | Identify tech stack | P0 |
| ANAL-005 | Assess documentation quality | P1 |
| ANAL-006 | Handle missing/poor READMEs gracefully | P0 |

**Input Processing:**
```python
def prepare_analysis_input(repo: Repository) -> str:
    """Prepare input for analyst agent"""
    readme = fetch_readme(repo.full_name)

    return f"""
    Repository: {repo.full_name}
    Description: {repo.description}
    Stars: {repo.stars}
    Language: {repo.language}
    Topics: {', '.join(repo.topics)}

    README Content:
    {truncate(readme, max_chars=8000)}
    """
```

#### 10.2.2 Ideator Agent

**Functional Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| IDEA-001 | Generate 2-3 ideas per repository | P0 |
| IDEA-002 | Ideas must be actionable (not vague) | P0 |
| IDEA-003 | Include monetization strategy | P0 |
| IDEA-004 | Include MVP scope | P0 |
| IDEA-005 | Score ideas on multiple dimensions | P0 |
| IDEA-006 | Prioritize bootstrappable ideas | P1 |

**Idea Validation Rules:**
```python
def validate_idea(idea: Idea) -> bool:
    """Ensure idea meets quality standards"""
    return all([
        len(idea.title) > 3,
        len(idea.description) > 50,
        idea.target_market is not None,
        idea.monetization is not None,
        len(idea.mvp_scope) >= 3,
        1 <= idea.feasibility_score <= 10,
        1 <= idea.market_score <= 10,
        1 <= idea.uniqueness_score <= 10
    ])
```

### 10.3 User Stories

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| P2-001 | As a founder, I want AI analysis of repos | Each top repo has analysis |
| P2-002 | As a founder, I want to understand the problem | Problem statement is clear |
| P2-003 | As a founder, I want product ideas | 2-3 ideas per repo |
| P2-004 | As a founder, I want feasibility scores | Scores are 1-10, justified |
| P2-005 | As a founder, I want MVP scope | 3-5 features listed |
| P2-006 | As a founder, I want monetization ideas | Pricing suggestions included |

### 10.4 Technical Implementation

**Files to Create/Modify:**
```
src/
├── ai/
│   ├── __init__.py
│   ├── crew.py              # CrewAI setup
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── analyst.py       # Analyst agent
│   │   └── ideator.py       # Ideator agent
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── analyze_task.py
│   │   └── ideate_task.py
│   └── prompts/
│       ├── analyst_system.txt
│       └── ideator_system.txt
├── delivery/
│   └── templates/
│       └── full_digest.md.j2   # Enhanced template
```

### 10.5 Cost Controls

```python
PHASE_2_LIMITS = {
    "max_repos_analyzed_per_run": 5,
    "max_tokens_analyst": 2000,
    "max_tokens_ideator": 3000,
    "primary_model": "deepseek-chat",     # Always use first
    "secondary_model": "qwen-turbo",      # If primary fails
    "fallback_model": "gpt-4-turbo",      # Last resort only
    "monthly_budget_usd": 10,             # Much lower with cheap models!
    "alert_threshold_usd": 8
}
```

### 10.6 Exit Criteria

- [ ] Analyst extracts meaningful insights
- [ ] Ideator generates quality ideas
- [ ] Ideas pass validation rules
- [ ] Digest includes full analysis
- [ ] Cost per run < $0.20
- [ ] Handles errors gracefully

---

## 11. Phase 3: Interaction System

### 11.1 Overview

**Goal:** Enable two-way communication and approval workflow via Telegram.

**Components:**
- Approval workflow (approve/reject)
- User preferences
- History and settings commands
- Webhook-based bot

**Dependencies:** Phase 2 completed

### 11.2 Detailed Requirements

#### 11.2.1 Approval Workflow

**State Machine:**
```
                                    ┌─────────────┐
                                    │   PENDING   │
                                    └──────┬──────┘
                                           │
                              ┌────────────┴────────────┐
                              ▼                         ▼
                       [User: Approve]           [User: Skip]
                              │                         │
                              ▼                         ▼
                    ┌─────────────────┐        ┌─────────────┐
                    │    APPROVED     │        │   SKIPPED   │
                    └────────┬────────┘        └─────────────┘
                             │
                    [System: Design]
                             │
                             ▼
                    ┌─────────────────┐
                    │   ARCHITECTED   │
                    └────────┬────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
          [User: Build]           [User: Cancel]
                 │                       │
                 ▼                       ▼
        ┌─────────────────┐     ┌─────────────────┐
        │    BUILDING     │     │    CANCELLED    │
        └────────┬────────┘     └─────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
    [SUCCESS]         [FAILURE]
        │                 │
        ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  COMPLETED  │   │   FAILED    │
└─────────────┘   └─────────────┘
```

#### 11.2.2 Telegram Commands

| Command | Description | Response |
|---------|-------------|----------|
| `/start` | Initialize bot | Welcome message + instructions |
| `/digest` | Get latest digest | Full digest or "No new repos" |
| `/history` | View past discoveries | Paginated list (10/page) |
| `/approved` | View approved ideas | List with status |
| `/settings` | Configure preferences | Inline keyboard menu |
| `/help` | Show commands | Command list |
| `/status` | System status | Current builds, last run |

#### 11.2.3 User Preferences

```python
class UserPreferences:
    telegram_id: str
    domains: List[str] = ["dev-tools", "productivity", "ai-ml"]
    min_stars: int = 100
    digest_time: str = "08:00"
    digest_timezone: str = "UTC"
    notifications_enabled: bool = True
    auto_architect: bool = False  # Auto-design approved ideas
```

### 11.3 User Stories

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| P3-001 | As a founder, I want to approve ideas | Inline button works |
| P3-002 | As a founder, I want to skip ideas | Removes from view |
| P3-003 | As a founder, I want to see history | Paginated, searchable |
| P3-004 | As a founder, I want to configure domains | Settings saved |
| P3-005 | As a founder, I want to see approved items | Status visible |
| P3-006 | As a founder, I want webhook mode | No polling needed |

### 11.4 Technical Implementation

**Files to Create/Modify:**
```
src/
├── delivery/
│   ├── telegram_bot.py      # Enhanced with commands
│   ├── webhook.py           # Webhook server (FastAPI)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── commands.py      # Command handlers
│   │   ├── callbacks.py     # Button callbacks
│   │   └── settings.py      # Settings management
│   └── templates/
│       ├── welcome.md.j2
│       ├── history.md.j2
│       └── settings.md.j2
├── workflow/
│   ├── __init__.py
│   └── state_machine.py     # Approval state machine
```

### 11.5 Exit Criteria

- [ ] Approve/skip buttons work
- [ ] State persists across restarts
- [ ] All commands functional
- [ ] Preferences saved and applied
- [ ] Webhook mode operational
- [ ] Rate limiting implemented

---

## 12. Phase 4: Architect System

### 12.1 Overview

**Goal:** Design implementation architecture for approved ideas.

**Components:**
- Architect Agent (GPT-4)
- Architecture storage
- Architecture review via Telegram

**Dependencies:** Phase 3 completed (approval workflow)

### 12.2 Detailed Requirements

#### 12.2.1 Architect Agent

**Functional Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| ARCH-001 | Generate high-level architecture | P0 |
| ARCH-002 | List all components | P0 |
| ARCH-003 | Specify tech stack | P0 |
| ARCH-004 | Create implementation steps | P0 |
| ARCH-005 | Map repository transformation | P0 |
| ARCH-006 | Estimate complexity per step | P1 |

**Architecture Template:**
```python
class Architecture:
    overview: str                    # High-level description
    components: List[Component]      # System components
    tech_stack: TechStack           # Technologies used
    implementation_steps: List[Step] # Ordered build steps
    repository_transform: Transform  # How to modify source repo
    estimated_complexity: str        # low/medium/high
    estimated_files: int            # Number of files to create/modify

class Step:
    number: int
    title: str
    description: str
    files_to_create: List[str]
    files_to_modify: List[str]
    dependencies: List[int]         # Step numbers this depends on
    complexity: str                 # low/medium/high
```

#### 12.2.2 User Interaction

After architecture is generated:
```markdown
🏗️ **Architecture Ready: ProductName**

**Overview:**
A FastAPI backend with React frontend that wraps the CLI tool...

**Tech Stack:**
• Frontend: React + TypeScript
• Backend: FastAPI + Python
• Database: PostgreSQL
• Deployment: Railway

**Implementation Steps (5):**
1. Project Setup (low complexity)
2. Core API (medium)
3. Database Models (low)
4. Frontend UI (medium)
5. Integration (medium)

**Estimated Files:** 23
**Estimated Complexity:** Medium

[Build It] [Modify Plan] [Cancel]
```

### 12.3 User Stories

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| P4-001 | As a founder, I want architecture auto-generated | Triggered on approval |
| P4-002 | As a founder, I want to see the tech stack | Clear list provided |
| P4-003 | As a founder, I want step-by-step plan | Ordered, estimated |
| P4-004 | As a founder, I want to review before building | Approval required |
| P4-005 | As a founder, I want to modify the plan | Feedback loop |

### 12.4 Technical Implementation

**Files to Create:**
```
src/
├── ai/
│   ├── agents/
│   │   └── architect.py     # Architect agent
│   ├── tasks/
│   │   └── design_task.py   # Design task
│   └── prompts/
│       └── architect_system.txt
├── delivery/
│   └── templates/
│       └── architecture.md.j2
```

### 12.5 Exit Criteria

- [ ] Architect generates valid plans
- [ ] Plans are understandable by humans
- [ ] Tech stack is appropriate
- [ ] Steps are actionable
- [ ] User can approve/modify
- [ ] Plans stored in database

---

## 13. Phase 5: Builder System

### 13.1 Overview

**Goal:** Automatically clone, modify, and build projects based on architecture.

**Components:**
- Builder Agent (Claude)
- Sandbox Environment (Docker)
- File System Manager
- Progress Reporter

**Dependencies:** Phase 4 completed (architecture)

### 13.2 Detailed Requirements

#### 13.2.1 Builder Agent

**Functional Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| BUILD-001 | Clone source repository | P0 |
| BUILD-002 | Execute one step at a time | P0 |
| BUILD-003 | Create new files | P0 |
| BUILD-004 | Modify existing files | P0 |
| BUILD-005 | Handle errors gracefully | P0 |
| BUILD-006 | Report progress | P0 |
| BUILD-007 | Rollback on critical failure | P1 |

**Safety Rules:**
```python
BUILDER_SAFETY_RULES = {
    "allowed_file_extensions": [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml",
        ".md", ".txt", ".html", ".css", ".scss", ".sql", ".sh"
    ],
    "forbidden_paths": [
        "/", "/etc", "/usr", "/var", "/home",
        ".git", ".env", "credentials", "secrets"
    ],
    "max_file_size_kb": 500,
    "max_files_per_step": 10,
    "timeout_per_step_seconds": 300
}
```

#### 13.2.2 Sandbox Environment

**Docker Container Spec:**
```dockerfile
FROM python:3.11-slim

# Install common tools
RUN apt-get update && apt-get install -y \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m builder
USER builder
WORKDIR /workspace

# Resource limits set at runtime:
# --memory=512m
# --cpus=1
# --network=none (isolated)
```

**Sandbox API:**
```python
class SandboxEnvironment:
    async def clone_repository(self, url: str, path: str) -> bool:
        """Clone repo into sandbox"""

    async def execute_command(
        self,
        command: str,
        timeout: int = 60
    ) -> CommandResult:
        """Run command in sandbox"""

    async def read_file(self, path: str) -> str:
        """Read file from sandbox"""

    async def write_file(self, path: str, content: str) -> bool:
        """Write file to sandbox"""

    async def list_files(self, path: str) -> List[str]:
        """List files in directory"""

    async def cleanup(self) -> None:
        """Destroy sandbox"""
```

#### 13.2.3 Progress Reporting

```markdown
🔨 **Build Progress: ProductName**

Step 2 of 5: Core API

Status: ⏳ In Progress

**Actions:**
✅ Created api/main.py
✅ Created api/routes/__init__.py
⏳ Creating api/routes/deploy.py...

**Files Changed:** 3 / 5
**Time Elapsed:** 45s

[Pause] [Cancel]
```

### 13.3 User Stories

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| P5-001 | As a founder, I want automatic cloning | Repo cloned to sandbox |
| P5-002 | As a founder, I want step-by-step building | One step at a time |
| P5-003 | As a founder, I want progress updates | Telegram notifications |
| P5-004 | As a founder, I want to pause builds | Pause/resume works |
| P5-005 | As a founder, I want error handling | Graceful failure |
| P5-006 | As a founder, I want safe execution | Sandbox isolation |

### 13.4 Technical Implementation

**Files to Create:**
```
src/
├── ai/
│   ├── agents/
│   │   └── builder.py       # Builder agent
│   ├── tasks/
│   │   └── build_task.py    # Build task
│   └── prompts/
│       └── builder_system.txt
├── execution/
│   ├── __init__.py
│   ├── sandbox.py           # Docker sandbox
│   ├── file_manager.py      # File operations
│   └── progress.py          # Progress tracking
├── delivery/
│   └── templates/
│       └── build_progress.md.j2
```

### 13.5 Exit Criteria

- [ ] Repositories clone successfully
- [ ] Builder creates valid code
- [ ] Sandbox isolates execution
- [ ] Progress reported to Telegram
- [ ] Errors handled gracefully
- [ ] Pause/cancel works

---

## 14. Phase 6: Testing System

### 14.1 Overview

**Goal:** Automatically run tests and verify builds.

**Components:**
- Tester Agent (deterministic)
- Test Framework Detection
- Build Verification
- Results Reporter

**Dependencies:** Phase 5 completed (builder)

### 14.2 Detailed Requirements

#### 14.2.1 Test Framework Detection

```python
TEST_FRAMEWORKS = {
    "python": {
        "pytest": {
            "detect": ["pytest.ini", "pyproject.toml[pytest]", "conftest.py"],
            "command": "pytest --tb=short -v",
            "coverage": "pytest --cov"
        },
        "unittest": {
            "detect": ["test_*.py"],
            "command": "python -m unittest discover"
        }
    },
    "javascript": {
        "jest": {
            "detect": ["jest.config.js", "package.json[jest]"],
            "command": "npm test"
        },
        "mocha": {
            "detect": ["mocha.opts", ".mocharc"],
            "command": "npm test"
        }
    },
    "typescript": {
        "jest": {
            "detect": ["jest.config.ts"],
            "command": "npm test"
        }
    }
}
```

#### 14.2.2 Build Verification

```python
BUILD_SYSTEMS = {
    "python": {
        "poetry": {
            "detect": ["pyproject.toml[poetry]"],
            "install": "poetry install",
            "build": "poetry build"
        },
        "pip": {
            "detect": ["requirements.txt"],
            "install": "pip install -r requirements.txt",
            "build": "python setup.py build"
        }
    },
    "javascript": {
        "npm": {
            "detect": ["package.json"],
            "install": "npm install",
            "build": "npm run build"
        }
    }
}
```

#### 14.2.3 Results Reporting

```markdown
🧪 **Test Results: ProductName**

**Status:** ✅ ALL PASSED

**Test Summary:**
• Total: 15
• Passed: 15 ✅
• Failed: 0
• Skipped: 0
• Duration: 12.3s

**Coverage:** 78%

**Build Status:** ✅ SUCCESS
• Build time: 23.4s
• Output size: 8.2 MB
• Warnings: 2

**Lint Status:** ✅ PASSED
• Errors: 0
• Warnings: 5

🚀 **Ready for deployment!**

[Download Code] [Deploy to Railway] [View Details]
```

### 14.3 User Stories

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| P6-001 | As a founder, I want auto test detection | Framework auto-detected |
| P6-002 | As a founder, I want tests to run | Tests execute in sandbox |
| P6-003 | As a founder, I want clear results | Pass/fail clearly shown |
| P6-004 | As a founder, I want coverage info | Coverage % displayed |
| P6-005 | As a founder, I want build verification | Build success confirmed |
| P6-006 | As a founder, I want to download code | Export functionality |

### 14.4 Technical Implementation

**Files to Create:**
```
src/
├── execution/
│   ├── tester.py            # Test runner
│   ├── builder_verify.py    # Build verification
│   └── detector.py          # Framework detection
├── delivery/
│   └── templates/
│       └── test_results.md.j2
```

### 14.5 Exit Criteria

- [ ] Tests run automatically
- [ ] Results accurately reported
- [ ] Coverage calculated
- [ ] Build verified
- [ ] Export works
- [ ] Failures handled gracefully

---

## 15. Phase 7: Learning System

### 15.1 Overview

**Goal:** Improve recommendations based on user feedback over time.

**Components:**
- Feedback Collector
- Scoring Adjuster
- Preference Learner
- A/B Testing Framework

**Dependencies:** Phases 1-6 completed

### 15.2 Detailed Requirements

#### 15.2.1 Feedback Signals

| Signal | Weight | Source |
|--------|--------|--------|
| Idea approved | +2.0 | Direct action |
| Idea rejected | -1.0 | Direct action |
| Build completed | +3.0 | Pipeline completion |
| Build failed (user's fault) | 0 | No signal |
| Build abandoned | -0.5 | User cancelled |
| Time spent viewing | +0.1/sec | Engagement proxy |

#### 15.2.2 Scoring Adjustment

```python
def adjust_domain_weights(feedback: List[Feedback]) -> Dict[str, float]:
    """Adjust domain weights based on feedback"""

    # Count approvals/rejections per domain
    domain_signals = defaultdict(lambda: {"positive": 0, "negative": 0})

    for fb in feedback:
        domain = get_idea_domain(fb.idea_id)
        if fb.action in ["approved", "built"]:
            domain_signals[domain]["positive"] += 1
        elif fb.action in ["rejected", "abandoned"]:
            domain_signals[domain]["negative"] += 1

    # Calculate new weights
    weights = {}
    for domain, signals in domain_signals.items():
        ratio = signals["positive"] / max(signals["negative"], 1)
        weights[domain] = min(2.0, max(0.5, ratio))  # Clamp 0.5-2.0

    return weights
```

#### 15.2.3 Weekly Reports

```markdown
📊 **Weekly Learning Report**

**Your Activity:**
• Ideas viewed: 35
• Ideas approved: 8
• Ideas rejected: 12
• Builds completed: 3

**Preference Insights:**
Your top domains:
1. 🛠 Developer Tools (45%)
2. 🤖 AI/ML (30%)
3. 📊 Data (15%)

**System Improvements:**
• Scoring adjusted for dev-tools (+15%)
• Reduced AI/ML visibility (you skip most)
• Added fintech to rotation (new interest?)

**Best Ideas This Week:**
1. "DeployBot" - Approved, Built ✅
2. "CodeReview AI" - Approved
3. "DataSync Pro" - Approved
```

### 15.3 User Stories

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| P7-001 | As a founder, I want personalized results | Recommendations improve |
| P7-002 | As a founder, I want to see my patterns | Weekly report |
| P7-003 | As a founder, I want domain adjustment | Weights change over time |
| P7-004 | As a founder, I want transparent learning | Explained in report |

### 15.4 Exit Criteria

- [ ] Feedback stored for all actions
- [ ] Domain weights adjust based on patterns
- [ ] Weekly reports generated
- [ ] Measurable improvement in approval rate

---

# PART IV: OPERATIONS

---

## 16. Deployment Architecture

### 16.1 Railway Configuration

**Services:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    RAILWAY PROJECT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ SERVICE: scout-worker                                    │   │
│  │ Type: Worker (always-on)                                 │   │
│  │                                                          │   │
│  │ • Runs scheduler                                         │   │
│  │ • Executes discovery pipeline                            │   │
│  │ • Manages AI agent execution                             │   │
│  │                                                          │   │
│  │ Resources: 512MB RAM, 0.5 vCPU                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ SERVICE: telegram-webhook                                │   │
│  │ Type: Web (HTTP)                                         │   │
│  │                                                          │   │
│  │ • FastAPI webhook server                                 │   │
│  │ • Handles Telegram callbacks                             │   │
│  │ • Port 8080                                              │   │
│  │                                                          │   │
│  │ Resources: 256MB RAM, 0.25 vCPU                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ SERVICE: builder-sandbox (Phase 5+)                      │   │
│  │ Type: Worker (on-demand)                                 │   │
│  │                                                          │   │
│  │ • Docker-in-Docker for sandboxed builds                  │   │
│  │ • Isolated execution environment                         │   │
│  │ • Spins up only when building                            │   │
│  │                                                          │   │
│  │ Resources: 1GB RAM, 1 vCPU                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ VOLUME: data                                             │   │
│  │                                                          │   │
│  │ • SQLite database                                        │   │
│  │ • Cloned repositories                                    │   │
│  │ • Build artifacts                                        │   │
│  │                                                          │   │
│  │ Size: 1GB (expandable)                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 16.2 Configuration Files

**railway.toml:**
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "always"

[service]
name = "scout-worker"
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY config/ ./config/

# Create data directory
RUN mkdir -p /data

# Run as non-root
RUN useradd -m scout
USER scout

# Entry point
CMD ["python", "-m", "src.main"]
```

### 16.3 Environment Variables

```bash
# ===========================================
# GITHUB SCOUT AI - ENVIRONMENT VARIABLES
# ===========================================

# --- Application ---
APP_ENV=production
LOG_LEVEL=INFO
DATABASE_PATH=/data/scout.db

# --- GitHub ---
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# --- Telegram ---
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
TELEGRAM_WEBHOOK_URL=https://your-app.railway.app/webhook

# --- AI Providers ---
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# --- Scheduler ---
DIGEST_SCHEDULE=0 8 * * *
RUN_FREQUENCY=2

# --- Cost Controls ---
MAX_REPOS_PER_RUN=5
MAX_TOKENS_PER_RUN=50000
MONTHLY_BUDGET_USD=30
ALERT_THRESHOLD_USD=25

# --- Feature Flags ---
ENABLE_BUILDER=false
ENABLE_LEARNING=false
```

---

## 17. Security & Compliance

### 17.1 Security Requirements

| Area | Requirement | Implementation |
|------|-------------|----------------|
| API Keys | Never in code | Environment variables only |
| Database | Protected | Railway internal network |
| Sandbox | Isolated | Docker with no network |
| User Data | Minimal | Only Telegram ID stored |
| Logging | Redacted | No sensitive data logged |

### 17.2 Sandbox Security

```python
SANDBOX_SECURITY = {
    "network": "none",           # No network access
    "read_only_root": True,      # Read-only filesystem
    "no_new_privileges": True,   # No privilege escalation
    "memory_limit": "512m",      # Memory cap
    "cpu_limit": "1",            # CPU cap
    "timeout": 600,              # 10 minute max
    "allowed_commands": [
        "python", "pip", "node", "npm", "git",
        "pytest", "jest", "cargo", "go"
    ]
}
```

### 17.3 Code Generation Security

**Before executing generated code:**
```python
def validate_generated_code(code: str) -> ValidationResult:
    """Validate AI-generated code for safety"""

    dangerous_patterns = [
        r"subprocess\.(call|run|Popen)",
        r"os\.system",
        r"eval\(",
        r"exec\(",
        r"__import__",
        r"open\(.*/etc",
        r"shutil\.rmtree\s*\(\s*['\"/]",
        r"requests\.(get|post)",  # No network in sandbox
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return ValidationResult(
                valid=False,
                reason=f"Dangerous pattern detected: {pattern}"
            )

    return ValidationResult(valid=True)
```

---

## 18. Cost Management

### 18.1 Cost Breakdown by Phase (Using Cheap Models)

| Phase | AI Calls | Cost/Run | Monthly (60 runs) |
|-------|----------|----------|-------------------|
| 1: Discovery | 0 | $0 | $0 |
| 2: Analysis | 5 analyst + 5 ideator (DeepSeek) | ~$0.02 | ~$1.20 |
| 3: Interaction | 0 | $0 | $0 |
| 4: Architect | ~2 per approval (DeepSeek Coder) | ~$0.01/approval | Variable |
| 5: Builder | ~10 per build (DeepSeek Coder) | ~$0.05/build | Variable |
| 6: Testing | 0 | $0 | $0 |
| 7: Learning | 0 | $0 | $0 |

**Note:** These costs assume DeepSeek/Qwen as primary models. Costs would be 10-20x higher with GPT-4/Claude.

### 18.2 Cost Controls

```python
class CostController:
    def __init__(self, monthly_budget: float = 30.0):
        self.monthly_budget = monthly_budget
        self.current_month_spend = 0.0

    def can_spend(self, estimated_cost: float) -> bool:
        """Check if we can afford this operation"""
        return (self.current_month_spend + estimated_cost) <= self.monthly_budget

    def record_spend(self, model: str, tokens: int):
        """Record actual spend"""
        cost = self.calculate_cost(model, tokens)
        self.current_month_spend += cost

        if self.current_month_spend > self.monthly_budget * 0.8:
            self.send_alert("80% of monthly budget used")

    def get_remaining_budget(self) -> float:
        return self.monthly_budget - self.current_month_spend
```

### 18.3 Model Selection Strategy

```python
def select_model(task_type: str, remaining_budget: float, retry_count: int = 0) -> str:
    """Select appropriate model based on task, budget, and retry count

    PRINCIPLE: Always try cheap models first. Only escalate on failure.
    """

    # Primary models - ALWAYS try these first (super cheap)
    primary_models = {
        "analysis": "deepseek-chat",
        "ideation": "deepseek-chat",
        "architecture": "deepseek-coder",
        "building": "deepseek-coder",
    }

    # Secondary models - try if primary fails (still cheap)
    secondary_models = {
        "analysis": "qwen-turbo",
        "ideation": "qwen-plus",
        "architecture": "qwen-coder",
        "building": "qwen-coder",
    }

    # Fallback models - only if cheap models fail (expensive!)
    fallback_models = {
        "analysis": "gpt-4-turbo",
        "ideation": "gpt-4-turbo",
        "architecture": "gpt-4-turbo",
        "building": "claude-3-5-sonnet",
    }

    if retry_count == 0:
        return primary_models.get(task_type, "deepseek-chat")
    elif retry_count == 1:
        return secondary_models.get(task_type, "qwen-turbo")
    else:
        # Only use expensive fallback if budget allows
        if remaining_budget > 5.0:
            return fallback_models.get(task_type, "gpt-4-turbo")
        return secondary_models.get(task_type, "qwen-turbo")
```

---

## 19. Monitoring & Observability

### 19.1 Health Checks

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    checks = {
        "database": await check_database(),
        "github_api": await check_github_rate_limit(),
        "telegram": await check_telegram_connection(),
        "scheduler": check_scheduler_running(),
    }

    all_healthy = all(checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 19.2 Metrics to Track

| Metric | Type | Alert Threshold |
|--------|------|-----------------|
| Pipeline success rate | Percentage | < 90% |
| AI cost per run | Dollar | > $0.50 |
| Telegram delivery rate | Percentage | < 95% |
| Build success rate | Percentage | < 70% |
| Average response time | Seconds | > 30s |
| Error rate | Percentage | > 5% |

### 19.3 Logging Strategy

```python
import structlog

logger = structlog.get_logger()

# Structured logging example
logger.info(
    "pipeline_completed",
    run_id=run.id,
    repos_scanned=run.repos_scanned,
    repos_analyzed=run.repos_analyzed,
    ideas_generated=run.ideas_generated,
    total_cost=run.total_cost,
    duration_seconds=run.duration
)

# Error logging (redacted)
logger.error(
    "api_error",
    service="openai",
    error_type=type(e).__name__,
    # Never log: API keys, tokens, full responses
)
```

---

# PART V: BUSINESS & LAUNCH

---

## 20. Business Model

### 20.1 Revenue Model

**Freemium + Usage-Based**

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 1 digest/week, top 3 repos, no ideas |
| **Pro** | $19/mo | Daily digests, all domains, AI ideas, history |
| **Builder** | $49/mo | Pro + 5 builds/month, architecture plans |
| **Unlimited** | $99/mo | Unlimited builds, priority support, API access |

### 20.2 Unit Economics

| Metric | Value |
|--------|-------|
| CAC (Content marketing) | $10 |
| LTV (12-mo retention) | $180 |
| LTV:CAC | 18:1 |
| Gross Margin | 75% |
| Payback Period | 1 month |

---

## 21. Go-To-Market Strategy

### 21.1 Launch Phases

**Phase A: Private Alpha (Month 1)**
- 10 hand-picked indie hackers
- Direct feedback loop
- Success: 60% daily engagement

**Phase B: Public Beta (Month 2)**
- Soft launch on Indie Hackers
- Build in public on Twitter
- Success: 200 signups

**Phase C: Product Hunt (Month 3)**
- Full launch
- Press outreach
- Success: Top 5 of day, 1000+ signups

### 21.2 Marketing Channels

| Channel | Strategy | Priority |
|---------|----------|----------|
| Twitter/X | Build in public, daily insights | P0 |
| Indie Hackers | Community posts, case studies | P0 |
| Product Hunt | Launch campaign | P0 |
| YouTube | Weekly "top repos" videos | P1 |
| SEO | "Best GitHub repos for X" articles | P2 |

---

## 22. Success Metrics

### 22.1 North Star Metric

**Weekly Active Users Who Approve Ideas (WAUAI)**

### 22.2 Key Metrics by Phase

| Phase | Primary Metric | Target |
|-------|---------------|--------|
| 1: Discovery | Digest delivery rate | 100% |
| 2: Analysis | Idea quality score (user rating) | 4.0/5 |
| 3: Interaction | Approval rate | 20%+ |
| 4-6: Building | Build success rate | 80%+ |
| 7: Learning | Approval rate improvement | +10% |

---

## 23. Risks & Mitigations

### 23.1 Technical Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| GitHub API changes | High | Low | Abstract API layer, monitor deprecations |
| AI model quality degradation | Medium | Medium | Prompt versioning, A/B testing |
| Sandbox escape | Critical | Very Low | Defense in depth, regular audits |
| Railway outages | Medium | Low | Health checks, alerting |

### 23.2 Business Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| Low willingness to pay | High | Medium | Validate pricing early, freemium |
| Competition from GitHub | High | Medium | Focus on ideation + building (GitHub won't) |
| AI costs increase | Medium | Medium | Model flexibility, caching |

### 23.3 Execution Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| Scope creep | High | High | Strict phase boundaries |
| Builder agent complexity | High | High | Defer until Phase 5 |
| Burnout | Medium | Medium | Automate everything, sustainable pace |

---

# PART VI: IMPLEMENTATION

---

## 24. Implementation Timeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE IMPLEMENTATION TIMELINE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: DISCOVERY                                          Weeks 1-2     │
│  ══════════════════                                                         │
│  □ Project setup (config, structure, Railway)                              │
│  □ GitHub scanner (GraphQL + REST)                                         │
│  □ Filter engine (rule-based)                                              │
│  □ Scorer (composite algorithm)                                            │
│  □ SQLite storage                                                          │
│  □ Basic Telegram bot (polling)                                            │
│  □ Simple digest template                                                  │
│  □ Scheduler (APScheduler)                                                 │
│  □ Railway deployment                                                      │
│  ✓ MILESTONE: Daily repos sent to Telegram                                │
│                                                                             │
│  PHASE 2: ANALYSIS                                           Weeks 3-4     │
│  ═════════════════                                                          │
│  □ CrewAI setup                                                            │
│  □ Analyst agent (DeepSeek)                                                │
│  □ Ideator agent (DeepSeek/Qwen)                                           │
│  □ Structured output validation                                            │
│  □ Cost tracking                                                           │
│  □ Enhanced digest template                                                │
│  □ /history command                                                        │
│  ✓ MILESTONE: AI-generated ideas in digest                                │
│                                                                             │
│  PHASE 3: INTERACTION                                        Weeks 5-6     │
│  ════════════════════                                                       │
│  □ Inline approval buttons                                                 │
│  □ State machine (approval flow)                                           │
│  □ User preferences storage                                                │
│  □ /settings command                                                       │
│  □ /approved command                                                       │
│  □ Webhook mode (FastAPI)                                                  │
│  □ Rate limiting                                                           │
│  ✓ MILESTONE: Interactive approval workflow                               │
│                                                                             │
│  PHASE 4: ARCHITECT                                          Weeks 7-8     │
│  ══════════════════                                                         │
│  □ Architect agent (DeepSeek Coder)                                        │
│  □ Architecture templates                                                  │
│  □ Repository transformation plans                                         │
│  □ Implementation step generator                                           │
│  □ Architecture review via Telegram                                        │
│  □ Modify/approve flow                                                     │
│  ✓ MILESTONE: Architecture plans for approved ideas                       │
│                                                                             │
│  PHASE 5: BUILDER                                            Weeks 9-11    │
│  ════════════════                                                           │
│  □ Docker sandbox environment                                              │
│  □ Repository cloning                                                      │
│  □ Builder agent (DeepSeek Coder)                                          │
│  □ File creation/modification                                              │
│  □ Step-by-step execution                                                  │
│  □ Progress reporting                                                      │
│  □ Error handling & recovery                                               │
│  □ Pause/cancel functionality                                              │
│  ✓ MILESTONE: Automated code generation                                   │
│                                                                             │
│  PHASE 6: TESTING                                            Week 12       │
│  ════════════════                                                           │
│  □ Test framework detection                                                │
│  □ Test execution in sandbox                                               │
│  □ Build verification                                                      │
│  □ Coverage reporting                                                      │
│  □ Results formatting                                                      │
│  □ Export functionality                                                    │
│  ✓ MILESTONE: Automated testing and verification                          │
│                                                                             │
│  PHASE 7: LEARNING                                           Weeks 13-14   │
│  ═════════════════                                                          │
│  □ Feedback collection                                                     │
│  □ Scoring weight adjustment                                               │
│  □ Domain preference learning                                              │
│  □ Weekly reports                                                          │
│  □ A/B testing framework                                                   │
│  ✓ MILESTONE: System improves over time                                   │
│                                                                             │
│  PHASE 8: LAUNCH                                             Weeks 15-16   │
│  ══════════════                                                             │
│  □ Landing page                                                            │
│  □ Documentation                                                           │
│  □ Product Hunt preparation                                                │
│  □ Beta user outreach                                                      │
│  □ Launch!                                                                 │
│  ✓ MILESTONE: Public launch                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 25. Technical Specifications

### 25.1 Complete Project Structure

```
github-scout-ai/
├── src/
│   ├── __init__.py
│   │
│   ├── core/                          # Phase 1: Discovery (No AI)
│   │   ├── __init__.py
│   │   ├── scanner.py                 # GitHub API scanning
│   │   ├── filter.py                  # Rule-based filtering
│   │   ├── scorer.py                  # Composite scoring
│   │   └── deduplicator.py            # History checking
│   │
│   ├── ai/                            # Phases 2, 4, 5: AI Agents
│   │   ├── __init__.py
│   │   ├── crew.py                    # CrewAI orchestration
│   │   ├── cost_controller.py         # Budget management
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── analyst.py             # Phase 2: Analysis
│   │   │   ├── ideator.py             # Phase 2: Ideation
│   │   │   ├── architect.py           # Phase 4: Architecture
│   │   │   └── builder.py             # Phase 5: Building
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── analyze_task.py
│   │   │   ├── ideate_task.py
│   │   │   ├── design_task.py
│   │   │   └── build_task.py
│   │   └── prompts/
│   │       ├── analyst_system.txt
│   │       ├── ideator_system.txt
│   │       ├── architect_system.txt
│   │       └── builder_system.txt
│   │
│   ├── execution/                     # Phases 5-6: Build & Test
│   │   ├── __init__.py
│   │   ├── sandbox.py                 # Docker sandbox
│   │   ├── file_manager.py            # File operations
│   │   ├── tester.py                  # Test runner
│   │   ├── detector.py                # Framework detection
│   │   └── progress.py                # Progress tracking
│   │
│   ├── delivery/                      # All Phases: Telegram
│   │   ├── __init__.py
│   │   ├── telegram_bot.py            # Bot setup & handlers
│   │   ├── webhook.py                 # Webhook server
│   │   ├── formatter.py               # Message formatting
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── commands.py
│   │   │   ├── callbacks.py
│   │   │   └── settings.py
│   │   └── templates/
│   │       ├── simple_digest.md.j2
│   │       ├── full_digest.md.j2
│   │       ├── architecture.md.j2
│   │       ├── build_progress.md.j2
│   │       ├── test_results.md.j2
│   │       ├── welcome.md.j2
│   │       └── weekly_report.md.j2
│   │
│   ├── workflow/                      # Phase 3: State Management
│   │   ├── __init__.py
│   │   └── state_machine.py
│   │
│   ├── learning/                      # Phase 7: Learning
│   │   ├── __init__.py
│   │   ├── feedback.py
│   │   ├── adjuster.py
│   │   └── reporter.py
│   │
│   ├── storage/                       # All Phases: Data
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── migrations.py
│   │
│   ├── pipeline.py                    # Main orchestration
│   ├── scheduler.py                   # APScheduler setup
│   ├── config.py                      # Configuration
│   └── main.py                        # Entry point
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_scanner.py
│   ├── test_filter.py
│   ├── test_scorer.py
│   ├── test_analyst.py
│   ├── test_ideator.py
│   ├── test_architect.py
│   ├── test_builder.py
│   ├── test_sandbox.py
│   └── test_telegram.py
│
├── docs/
│   ├── MASTER_PRD.md                  # This document
│   └── API.md
│
├── .mind/
│   └── MEMORY.md                      # Session memory
│
├── config/
│   └── domains.yaml                   # Domain configuration
│
├── data/                              # Local dev (gitignored)
│   └── .gitkeep
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml                 # Local dev with sandbox
├── railway.toml
└── README.md
```

### 25.2 Dependencies

```toml
# pyproject.toml
[project]
name = "github-scout-ai"
version = "1.0.0"
requires-python = ">=3.11"

dependencies = [
    # Core
    "pydantic>=2.0",
    "pydantic-settings>=2.0",

    # GitHub
    "PyGithub>=2.0",
    "gql>=3.0",
    "aiohttp>=3.9",

    # AI
    "crewai>=0.30",
    "langchain>=0.1",
    "langchain-openai>=0.1",
    "openai>=1.0",
    "anthropic>=0.20",

    # Telegram
    "python-telegram-bot>=20.0",

    # Web
    "fastapi>=0.100",
    "uvicorn>=0.25",

    # Database
    "aiosqlite>=0.19",

    # Scheduling
    "apscheduler>=3.10",

    # Templates
    "jinja2>=3.1",

    # Docker (for sandbox)
    "docker>=7.0",

    # Utilities
    "structlog>=24.0",
    "tenacity>=8.0",
    "httpx>=0.26",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.0",
    "ruff>=0.2",
    "mypy>=1.8",
]
```

---

## 26. Appendix

### 26.1 Glossary

| Term | Definition |
|------|------------|
| Agent | AI-powered component that performs a specific task |
| Composite Score | Weighted score combining multiple repository metrics |
| Digest | Daily summary message sent to Telegram |
| Idea | AI-generated product concept based on a repository |
| Pipeline | Sequential execution of discovery → analysis → notification |
| Sandbox | Isolated Docker environment for code execution |
| Scout | The discovery agent that scans GitHub |

### 26.2 API Reference

**GitHub GraphQL Query Example:**
```graphql
query TrendingRepos($query: String!, $first: Int!) {
  search(query: $query, type: REPOSITORY, first: $first) {
    repositoryCount
    nodes {
      ... on Repository {
        id
        name
        nameWithOwner
        description
        url
        stargazerCount
        forkCount
        primaryLanguage { name }
        repositoryTopics(first: 10) {
          nodes { topic { name } }
        }
        createdAt
        updatedAt
        hasIssuesEnabled
        licenseInfo { spdxId }
      }
    }
  }
}
```

### 26.3 Environment Variables Reference

See Section 16.3 for complete list.

### 26.4 Domain Configuration

```yaml
# config/domains.yaml
domains:
  dev-tools:
    search_terms:
      - cli
      - developer-tools
      - devtools
      - sdk
      - terminal
    priority: 1

  productivity:
    search_terms:
      - productivity
      - automation
      - workflow
      - efficiency
    priority: 1

  ai-ml:
    search_terms:
      - machine-learning
      - llm
      - ai
      - nlp
      - deep-learning
      - transformers
    priority: 1

  data:
    search_terms:
      - data-analysis
      - analytics
      - etl
      - database
      - data-science
    priority: 2

  infrastructure:
    search_terms:
      - devops
      - kubernetes
      - monitoring
      - cloud
      - infrastructure
    priority: 2

  fintech:
    search_terms:
      - payments
      - crypto
      - trading
      - finance
      - blockchain
    priority: 2

  healthcare:
    search_terms:
      - health
      - medical
      - telemedicine
      - biotech
    priority: 3

  education:
    search_terms:
      - learning
      - education
      - tutorial
      - e-learning
    priority: 3

  automation:
    search_terms:
      - automation
      - bots
      - scraping
      - rpa
      - workflow
    priority: 2

  security:
    search_terms:
      - security
      - privacy
      - encryption
      - auth
      - cybersecurity
    priority: 3
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-08 | AI Architect | Initial PRD (Phases 1-3) |
| 2.0 | 2026-03-08 | AI Architect | Complete system (Phases 1-7) |

---

**END OF MASTER PRD**
