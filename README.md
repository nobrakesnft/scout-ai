# GitHub Scout AI 🔭

An autonomous AI system that discovers trending GitHub repositories, analyzes them, and generates actionable product ideas—delivered straight to your Telegram.

## Features

- **Daily Discovery**: Scans GitHub for trending repos across 10+ domains
- **AI Analysis**: Extracts problem/solution patterns using DeepSeek (cost-efficient)
- **Idea Generation**: Transforms repos into actionable product concepts
- **Telegram Delivery**: Get curated digests without leaving your messenger
- **Feedback Learning**: System improves based on your approvals/rejections

## Quick Start

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token
- Telegram Bot Token (from @BotFather)
- DeepSeek API Key (or OpenAI as fallback)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/github-scout-ai.git
cd github-scout-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` with your credentials:

```env
GITHUB_TOKEN=ghp_your_github_token
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_CHAT_ID=your_chat_id
DEEPSEEK_API_KEY=sk-your_deepseek_key
```

### Running

```bash
# Development (local)
python -m src.main

# Production (Railway)
railway up
```

## Project Structure

```
github-scout-ai/
├── src/
│   ├── core/           # Scanner, Filter, Scorer (Phase 1)
│   ├── ai/             # CrewAI agents (Phase 2+)
│   ├── delivery/       # Telegram bot & formatting
│   ├── storage/        # SQLite database
│   ├── workflow/       # Approval state machine (Phase 3+)
│   ├── execution/      # Builder sandbox (Phase 5+)
│   ├── learning/       # Feedback system (Phase 7+)
│   ├── pipeline.py     # Main orchestration
│   ├── scheduler.py    # Cron jobs
│   └── main.py         # Entry point
├── tests/
├── docs/
│   ├── PRD.md
│   └── MASTER_PRD.md
└── config/
```

## Implementation Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1. Foundation | 🔨 Building | GitHub scanner, filter, Telegram bot |
| 2. Analysis | ⏳ Planned | AI analysis & idea generation |
| 3. Interaction | ⏳ Planned | Approval workflow, settings |
| 4. Architect | ⏳ Planned | Design implementation plans |
| 5. Builder | ⏳ Planned | Auto-build prototypes |
| 6. Testing | ⏳ Planned | Automated testing |
| 7. Learning | ⏳ Planned | Feedback-driven improvement |

## Commands

Once running, use these Telegram commands:

- `/start` - Welcome message
- `/digest` - Get latest digest on demand
- `/history` - View past discoveries
- `/settings` - Configure preferences
- `/help` - Show help

## Cost Estimate

Using DeepSeek (primary) instead of GPT-4:

| Component | Monthly Cost |
|-----------|--------------|
| AI (DeepSeek) | ~$1-2 |
| Railway hosting | ~$5 |
| **Total** | **~$6-7/month** |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint code
ruff check src/

# Type check
mypy src/
```

## License

MIT

## Contributing

PRs welcome! Please read the PRD in `docs/` before contributing.
