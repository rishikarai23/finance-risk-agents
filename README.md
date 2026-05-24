# Finance Risk Intelligence — Multi-Agent System

A production-grade multi-agent AI system for automated financial risk analysis of publicly traded companies. Provide a company name and ticker — six specialized AI agents research it, cross-check findings, detect contradictions, and produce a structured analyst-style risk memo with full audit trail.

## What it does

Give it a ticker and company name. The system launches six specialized AI agents that:

- Search real financial news via NewsAPI
- Fetch live financial metrics via Yahoo Finance
- Score risk across 4 dimensions (liquidity, credit, concentration, market)
- Detect contradictions between agent findings
- Analyze market sentiment from news tone
- Generate a structured analyst-style risk memo

All agent activity streams live to the dashboard via WebSocket. Every action is recorded in a full audit trail.

## Architecture

Follows a **blackboard architecture** — all agents communicate through a shared typed state object (`FinancialContext`) implemented with **Pydantic v2**. Agents never communicate directly.

```text
Agent → FinancialContext → Agent
```

```text
User Request
      ↓
Master Orchestrator
(token budget, routing, fault tolerance, rate limiting)
      ↓
News Agent        → NewsAPI (real web search)
Financial Agent   → Yahoo Finance (real market data)
Risk Scorer       → 4-dimensional risk scoring
Contradiction     → Cross-agent inconsistency detection
Sentiment Agent   → Tone and mood analysis
Report Agent      → Structured risk memo
      ↓
Risk Memo + Audit Trail
```

## Agent Temperature Map

| Agent | Temperature | Purpose |
|---|---:|---|
| Orchestrator | 0.0 | Deterministic routing |
| News Agent | 0.7 | Broader information exploration |
| Financial Agent | 0.0 | Deterministic factual analysis |
| Risk Scorer | 0.0 | Consistent scoring |
| Contradiction Agent | 0.3 | Structured validation |
| Sentiment Agent | 0.5 | Nuanced tone analysis |
| Report Agent | 0.7 | Human-readable report generation |

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12+ | Core language |
| Groq API | LLM inference (llama-3.1-8b-instant) |
| Pydantic v2 | Typed state validation |
| FastAPI | REST and WebSocket API |
| slowapi | Rate limiting (5/minute, 20/day per IP) |
| yfinance | Real financial data |
| NewsAPI | Real news articles |
| ChromaDB | Long-term memory (in progress) |
| Docker Compose | Containerization |

## API Endpoints

### REST

**POST /analyze** — rate limited to 5/minute, 20/day

```json
{
    "ticker": "AAPL",
    "company_name": "Apple Inc",
    "max_tokens": 50000
}
```

### WebSocket

**WS /analyze/stream** — rate limited to 5/minute, 20/day per IP

- Live agent execution updates
- Incremental status messages per agent
- Final structured memo on completion

### Dashboard

**GET /dashboard** — live streaming UI

### Documentation

**GET /docs** — interactive Swagger UI

## Sample Output

```json
{
  "overall_risk": 5.75,
  "sentiment_score": -0.4,
  "contradictions": 4,
  "final_memo": "MEDIUM RISK — Apple Inc shows strong profitability...",
  "tokens_used": 9500,
  "audit_log": [...]
}
```

## Setup

### Clone and install

```bash
git clone https://github.com/rishikarai23/Multi_Agent.git
cd finance-risk-agents
python3 -m venv venv
source venv/bin/activate
pip install ".[dev]"
```

### Configure environment

```bash
cp .env.example .env
```

Add your keys:

```env
GROQ_API_KEY=
NEWS_API_KEY=
```

### Run with Docker (recommended)

```bash
docker-compose up --build
```

### Run locally

```bash
uvicorn api.main:app --reload --port 8000
```

### Open dashboard
http://localhost:8000/dashboard

### Test API

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "company_name": "Apple Inc"}'
```

## Key Design Decisions

### Blackboard Architecture
Agents never communicate directly. All state flows through `FinancialContext`. Any agent can be swapped, upgraded, or removed without touching the others.

### Token Budget Enforcement
The orchestrator tracks exact token consumption per agent using Groq's `response.usage.total_tokens`. Agents are skipped when the budget is exhausted.

### Fault Tolerance
Every agent runs inside a try/except block. One agent failing does not terminate the pipeline. The Report Agent produces a partial memo from whatever data is available.

### Typed State Validation
Pydantic v2 with `validate_assignment=True` validates every field assignment at runtime. Wrong types are caught immediately, not deep in production.

### Rate Limiting
REST endpoints protected by slowapi (5 requests/minute, 20/day per IP). WebSocket endpoint protected by in-memory per-IP tracking with the same limits.

### Real Data Only
No mock data anywhere in the system. NewsAPI for news, Yahoo Finance for financial metrics, Groq for LLM inference.

## Validation Results

| Company | Overall Risk | Classification | Accuracy |
|---|---:|---|---|
| Apple (AAPL) | 5.75/10 | Medium | correct |
| SVB (SIVBQ) | 8.00/10 | High | correct (collapsed 2023) |
| Beyond Meat (BYND) | 7.00/10 | High | correct (declining revenue) |
| Tesla (TSLA) | 7.50/10 | Medium-High | correct (volatile) |

## Eval Pipeline

15 standardized test cases across 3 categories:

| Category | Cases | Pass Rate |
|---|---|---|
| Baseline (stable companies) | 5 | 100% |
| Ambiguous (mixed signals) | 5 | 100% |
| Adversarial (edge cases) | 5 | 100% |
