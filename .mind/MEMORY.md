# GitHub Scout AI - Master Session Memory

**Project:** GitHub Scout AI
**Location:** `C:\Users\HP OWNER\Vibecoding\github-scout-ai`
**Last Updated:** 2026-03-08
**PRD Version:** 2.0 (Complete System)

---

## Quick Context Restore

When starting a new session, read this section first:

> **GitHub Scout AI** is an autonomous system that discovers GitHub repositories, analyzes them with AI, generates product ideas, and upon approval, can automatically build and test prototypes. It runs on Railway and communicates via Telegram.

**Current Status:** Planning complete, ready to build Phase 1

---

## Project Vision

```
DISCOVER → ANALYZE → IDEATE → ARCHITECT → BUILD → TEST → LEARN
   │          │         │          │         │       │       │
 Scout     Analyst   Ideator  Architect  Builder  Tester  Feedback
 Agent     Agent     Agent     Agent      Agent   Agent    Loop
   │          │         │          │         │       │       │
 No AI    DeepSeek  DeepSeek  DeepSeek  DeepSeek  No AI   No AI
                    / Qwen     Coder     Coder
```

**MODEL STRATEGY: CHEAP FIRST!**
- Primary: DeepSeek / DeepSeek Coder (super cheap)
- Secondary: Qwen / Qwen Coder (also cheap)
- Fallback: GPT-4 / Claude (ONLY if cheap models fail)

**The big idea:** An AI research assistant + builder team that works while you sleep.

---

## Implementation Phases

### Phase 1: Discovery System ⬜ NOT STARTED
**Goal:** Scan GitHub daily, filter repos, send to Telegram
**Components:** Scanner, Filter, Scorer, Deduplicator, Basic Telegram
**AI Usage:** None (all deterministic)
**Estimated Time:** 2 weeks

**Checklist:**
- [ ] Project setup (pyproject.toml, structure)
- [ ] GitHub scanner (GraphQL + REST API)
- [ ] Filter engine (rule-based: stars >100, updated <30 days)
- [ ] Scorer (composite algorithm)
- [ ] SQLite database setup
- [ ] Basic Telegram bot (polling mode)
- [ ] Simple digest template
- [ ] APScheduler for cron
- [ ] Deploy to Railway
- [ ] End-to-end testing

**Exit Criteria:**
- Scanner discovers 50+ repos/run
- Filter reduces to 10-20 quality repos
- Top 5 sent to Telegram daily
- No duplicates across runs
- Running on Railway

---

### Phase 2: Analysis System ⬜ NOT STARTED
**Goal:** AI analyzes repos and generates product ideas
**Components:** Analyst Agent, Ideator Agent, Enhanced Digest
**AI Usage:** DeepSeek (both analyst AND ideator - cheap!)
**Estimated Time:** 2 weeks

**Checklist:**
- [ ] CrewAI integration
- [ ] Analyst agent (DeepSeek) - extracts problem/solution
- [ ] Ideator agent (DeepSeek/Qwen) - generates product ideas
- [ ] Structured output schemas (Pydantic)
- [ ] Cost tracking and limits
- [ ] Enhanced digest with ideas
- [ ] /history command

**Exit Criteria:**
- Analyst extracts meaningful insights
- 2-3 quality ideas per repo
- Cost per run < $0.20
- Errors handled gracefully

---

### Phase 3: Interaction System ⬜ NOT STARTED
**Goal:** Two-way communication and approval workflow
**Components:** Approval buttons, Settings, State machine
**AI Usage:** None
**Estimated Time:** 2 weeks

**Checklist:**
- [ ] Inline approval buttons (Approve/Skip/Details)
- [ ] State machine for approval workflow
- [ ] User preferences storage
- [ ] /settings command
- [ ] /approved command
- [ ] Webhook mode (FastAPI server)
- [ ] Rate limiting

**Exit Criteria:**
- Approve/skip buttons work
- State persists across restarts
- Preferences saved and applied
- Webhook mode operational

---

### Phase 4: Architect System ⬜ NOT STARTED
**Goal:** Design implementation architecture for approved ideas
**Components:** Architect Agent, Architecture templates
**AI Usage:** DeepSeek Coder (cheap!)
**Estimated Time:** 2 weeks

**Checklist:**
- [ ] Architect agent (DeepSeek Coder)
- [ ] Architecture template structure
- [ ] Repository transformation planning
- [ ] Implementation step generator
- [ ] Architecture review via Telegram
- [ ] Modify/approve architecture flow

**Exit Criteria:**
- Valid architecture plans generated
- Tech stack appropriate for project
- Steps are actionable
- User can review before building

---

### Phase 5: Builder System ⬜ NOT STARTED
**Goal:** Automatically clone, modify, and build projects
**Components:** Builder Agent, Docker Sandbox, Progress Reporter
**AI Usage:** DeepSeek Coder / Qwen Coder (cheap!)
**Estimated Time:** 3 weeks

**Checklist:**
- [ ] Docker sandbox environment
- [ ] Repository cloning
- [ ] Builder agent (DeepSeek Coder)
- [ ] File creation/modification
- [ ] Step-by-step execution
- [ ] Progress reporting to Telegram
- [ ] Error handling & recovery
- [ ] Pause/cancel functionality
- [ ] Safety validations

**Exit Criteria:**
- Repos clone successfully
- Builder creates valid code
- Sandbox isolates execution
- Progress reported to Telegram
- Pause/cancel works

---

### Phase 6: Testing System ⬜ NOT STARTED
**Goal:** Run tests and verify builds automatically
**Components:** Tester Agent, Framework Detection, Results Reporter
**AI Usage:** None (deterministic)
**Estimated Time:** 1 week

**Checklist:**
- [ ] Test framework detection (pytest, jest, etc.)
- [ ] Test execution in sandbox
- [ ] Build verification
- [ ] Coverage reporting
- [ ] Results formatting
- [ ] Export/download functionality

**Exit Criteria:**
- Tests run automatically
- Results accurately reported
- Build verified
- Export works

---

### Phase 7: Learning System ⬜ NOT STARTED
**Goal:** Improve recommendations based on feedback
**Components:** Feedback Collector, Score Adjuster, Weekly Reports
**AI Usage:** None
**Estimated Time:** 2 weeks

**Checklist:**
- [ ] Feedback collection (approve/reject/build signals)
- [ ] Scoring weight adjustment
- [ ] Domain preference learning
- [ ] Weekly summary reports
- [ ] A/B testing framework

**Exit Criteria:**
- Feedback stored for all actions
- Approval rate improves over time
- Weekly reports generated

---

## Architecture Decisions

### Decision 1: Hybrid AI Architecture
**What:** Use AI only where it adds value; deterministic code elsewhere
**Why:** Cost control, reliability, speed
**Details:**
- Scanner, Filter, Scorer, Tester, Messenger = No AI
- Analyst, Ideator, Architect, Builder = AI-powered

### Decision 2: CrewAI for Agent Framework
**What:** Use CrewAI over LangGraph, MetaGPT, AutoGen
**Why:** Right abstraction level, model-agnostic, good DX
**Status:** Confirmed

### Decision 3: Model Selection Strategy - CHEAP FIRST!
**What:** Use cheap models (DeepSeek/Qwen) for ALL tasks, expensive models only as fallback
**Why:** Massive cost reduction (10-20x cheaper)
**Details:**
- DeepSeek: Analysis, Ideation (primary for all text tasks)
- DeepSeek Coder: Architecture, Building (primary for all code tasks)
- Qwen / Qwen Coder: Secondary if DeepSeek fails
- GPT-4 / Claude: LAST RESORT only when cheap models fail completely

**Cost comparison:**
- DeepSeek: ~$0.001 per 1K tokens
- GPT-4: ~$0.03 per 1K tokens (30x more expensive!)
- Claude: ~$0.015 per 1K tokens (15x more expensive!)

### Decision 4: Telegram-First Delivery
**What:** Telegram as primary (only) channel initially
**Why:** Zero friction, users already have it, good bot API
**Future:** Add email/web after proving value

### Decision 5: SQLite Database
**What:** SQLite on Railway Volume
**Why:** Simple, file-based, sufficient for initial scale
**Migrate When:** 1000+ users → PostgreSQL

### Decision 6: Docker Sandbox for Building
**What:** Isolated Docker containers for code execution
**Why:** Security - never run untrusted code on host
**Details:**
- No network access
- Memory/CPU limits
- Read-only root filesystem
- Timeout enforcement

### Decision 7: Phased Implementation
**What:** Build in strict phases, don't skip ahead
**Why:** Validate each layer before adding complexity
**Rule:** Each phase must hit exit criteria before starting next

---

## Tech Stack

| Component | Technology | Phase |
|-----------|------------|-------|
| Language | Python 3.11+ | All |
| Agent Framework | CrewAI | 2+ |
| **AI (Primary)** | **DeepSeek / DeepSeek Coder** | 2+ |
| **AI (Secondary)** | **Qwen / Qwen Coder** | 2+ |
| AI (Fallback) | GPT-4 / Claude (rarely used) | 2+ |
| GitHub API | PyGithub + GraphQL | 1+ |
| Telegram | python-telegram-bot | 1+ |
| Database | SQLite | 1+ |
| Scheduler | APScheduler | 1+ |
| Web Framework | FastAPI | 3+ |
| Sandbox | Docker | 5+ |
| Templates | Jinja2 | 1+ |
| Deployment | Railway | 1+ |

---

## Cost Projections (Using DeepSeek/Qwen - CHEAP!)

### Per-Run Costs (Phases 1-3)
| Component | Cost |
|-----------|------|
| Scanner | $0 (API free) |
| Filter/Score | $0 |
| Analyst (5 repos, DeepSeek) | ~$0.005 |
| Ideator (5 repos, DeepSeek) | ~$0.01 |
| **Total** | **~$0.02/run** |

### Monthly Costs (2 runs/day)
| Item | Cost |
|------|------|
| AI (60 runs × $0.02) | ~$1.20 |
| Railway | ~$5 |
| **Total** | **~$6-7/month** |

### Per-Build Costs (Phases 4-6)
| Component | Cost |
|-----------|------|
| Architect (DeepSeek Coder) | ~$0.01 |
| Builder (10 steps, DeepSeek Coder) | ~$0.05 |
| Tester | $0 |
| **Total** | **~$0.06/build** |

### Cost Comparison
| Model Strategy | Monthly Cost |
|----------------|--------------|
| **DeepSeek/Qwen (our choice)** | **~$6-7** |
| GPT-4/Claude (expensive) | ~$50-100 |

---

## Environment Variables Needed

```env
# Application
APP_ENV=production
LOG_LEVEL=INFO
DATABASE_PATH=/data/scout.db

# GitHub
GITHUB_TOKEN=ghp_xxx

# Telegram
TELEGRAM_BOT_TOKEN=123:ABC
TELEGRAM_CHAT_ID=123456789
TELEGRAM_WEBHOOK_URL=https://app.railway.app/webhook

# AI Providers (Priority Order)
DEEPSEEK_API_KEY=sk-xxx         # PRIMARY - use for everything
QWEN_API_KEY=sk-xxx             # SECONDARY - backup if DeepSeek fails
OPENAI_API_KEY=sk-xxx           # FALLBACK ONLY - expensive!
ANTHROPIC_API_KEY=sk-ant-xxx    # LAST RESORT - expensive!

# Scheduler
DIGEST_SCHEDULE=0 8 * * *
RUN_FREQUENCY=2

# Cost Controls
MAX_REPOS_PER_RUN=5
MAX_TOKENS_PER_RUN=50000
MONTHLY_BUDGET_USD=30

# Feature Flags
ENABLE_BUILDER=false
ENABLE_LEARNING=false
```

---

## Files Created

| File | Purpose | Status |
|------|---------|--------|
| `docs/MASTER_PRD.md` | Complete system PRD (all phases) | ✅ Created |
| `.mind/MEMORY.md` | This session memory file | ✅ Created |
| `docs/PRD.md` | Initial PRD (superseded by MASTER_PRD) | ✅ Created |

---

## Project Structure (Target)

```
github-scout-ai/
├── src/
│   ├── core/           # Phase 1: Scanner, Filter, Scorer
│   ├── ai/             # Phases 2,4,5: AI Agents
│   ├── execution/      # Phases 5-6: Sandbox, Tester
│   ├── delivery/       # All: Telegram bot
│   ├── workflow/       # Phase 3: State machine
│   ├── learning/       # Phase 7: Feedback loop
│   ├── storage/        # All: Database
│   ├── pipeline.py     # Orchestration
│   ├── scheduler.py    # Cron jobs
│   ├── config.py       # Configuration
│   └── main.py         # Entry point
├── tests/
├── docs/
│   └── MASTER_PRD.md
├── .mind/
│   └── MEMORY.md
├── config/
│   └── domains.yaml
├── .env.example
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── railway.toml
└── README.md
```

---

## Risks to Watch

| Risk | Status | Mitigation |
|------|--------|------------|
| GitHub rate limits | Not tested | Use authenticated API, cache, spread requests |
| AI hallucinations | Not tested | Structured outputs, validation, confidence scores |
| Builder complexity | HIGH RISK | Defer until Phases 1-4 validated |
| Token cost explosion | Not tested | Hard limits, budget alerts, cheap model fallbacks |
| Sandbox escape | Not tested | Defense in depth, no network, resource limits |
| Scope creep | ACTIVE | Strict phase boundaries, exit criteria |

---

## Session Log

### Session 1: 2026-03-08

**What was discussed:**
- User wants autonomous AI system for GitHub discovery + building
- Evaluated with IdeaRalph (PMF score: 7.3/10)
- Recommended hybrid architecture (deterministic + selective AI)
- Recommended CrewAI for agent framework
- Defined 7 implementation phases
- User requested ONE comprehensive PRD covering everything

**What was created:**
1. `docs/MASTER_PRD.md` - Complete PRD covering all 7 phases
2. `.mind/MEMORY.md` - This comprehensive memory file

**Key decisions made:**
- Single Master PRD (not separate docs per system)
- Single Memory file (not separate per agent)
- Build in phases but document everything upfront
- **CHEAP MODELS FIRST: DeepSeek/Qwen for ALL tasks**
- GPT-4/Claude only as fallback when cheap models fail
- CrewAI for agent orchestration
- Railway deployment
- Telegram-first delivery
- Docker sandbox for builder security

**User preferences noted:**
- Minimize AI token usage
- Open-source frameworks preferred
- Modular architecture
- Cloud deployment (Railway)
- Run 1-2x daily
- Wants complete vision documented before building

**Next steps:**
- [ ] Start Phase 1 implementation
- [ ] Set up project structure
- [ ] Implement GitHub scanner
- [ ] Create basic Telegram bot

---

## Quick Commands

```bash
# Navigate to project
cd "C:\Users\HP OWNER\Vibecoding\github-scout-ai"

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies (after requirements.txt created)
pip install -r requirements.txt

# Run locally
python -m src.main

# Run tests
pytest

# Deploy to Railway
railway up
```

---

## Reference Links

- **MASTER_PRD:** `docs/MASTER_PRD.md` - Complete system documentation
- **CrewAI Docs:** https://docs.crewai.com
- **Railway Docs:** https://docs.railway.app
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **GitHub GraphQL:** https://docs.github.com/en/graphql

---

## How to Use This Memory

1. **Starting a new session:** Read "Quick Context Restore" and "Current Status"
2. **Checking progress:** Look at Phase checklists
3. **Making decisions:** Check "Architecture Decisions" for context
4. **Debugging:** Check "Risks to Watch" and "Session Log"
5. **After work:** Update phase checklist, add to session log

---

**Remember:** Always update this file at the end of each session!
