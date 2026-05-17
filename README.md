# Finance Risk Intelligence: Multi-Agent System

A production-grade multi-agent AI system that performs automated financial risk analysis on any publicly traded company. Built with 6 specialized AI agents, a master orchestrator, real-time WebSocket streaming, and a full audit trail.

## What it does

Give it a company ticker and name. Seven specialized agents research it from different angles, cross-check each other's findings, detect contradictions, and produce a structured risk memo,the kind a financial analyst would write manually.

## Architecture

All agents communicate through a typed `FinancialContext` state object (Pydantic v2). No agent talks directly to another. This is called a **blackboard architecture**.
User Request
↓
Master Orchestrator (token budget, routing, fault tolerance)
↓
┌─────────────────────────────────────────┐
│  News Agent       → real NewsAPI search  │
│  Financial Agent  → Yahoo Finance data   │
│  Risk Scorer      → 4 dimensional scores │
│  Contradiction    → cross-agent checks   │
│  Sentiment Agent  → tone analysis        │
│  Report Agent     → structured memo      │
└─────────────────────────────────────────┘
↓
Risk Memo + Audit Trail

## Agent Temperature Map

| Agent | Temperature | Reason |
|---|---|---|
| Orchestrator | 0 | Deterministic routing |
| News Agent | 0.7 | Creative angle finding |
| Financial Agent | 0 | Numbers are facts |
| Risk Scorer | 0 | Repeatable scoring |
| Contradiction Agent | 0.3 | Structured skepticism |
| Sentiment Agent | 0.5 | Nuanced tone reading |
| Report Agent | 0.7 | Readable prose |

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12+ | Core language |
| Groq API | LLM inference (llama-3.1-8b-instant) |
| LangGraph | Agent orchestration |
| Pydantic v2 | Typed state validation |
| FastAPI | REST and WebSocket API |
| yfinance | Real financial data |
| NewsAPI | Real news articles |
| ChromaDB | Vector DB (long term memory) |
| Docker Compose | Containerization |

## API Endpoints

### REST
POST /analyze
{
"ticker": "AAPL",
"company_name": "Apple Inc",
"max_tokens": 50000
}

### WebSocket (real-time streaming)
WS /analyze/stream
→ live agent updates as each one completes
→ final memo on completion

### Docs
GET /docs   → interactive Swagger UI

## Sample Output

```json
{
  "overall_risk": 5.75,
  "sentiment_score": -0.4,
  "contradictions": 4,
  "final_memo": "MEDIUM RISK — Apple Inc shows strong profitability...",
  "tokens_used": 9500
}
```

## Setup

### 1. Clone and install
```bash
git clone https://github.com/rishikarai23/Multi_Agent.git
cd Multi_Agent
python3 -m venv venv
source venv/bin/activate
pip install ".[dev]"
```

### 2. Environment variables
```bash
cp .env.example .env
# Add your keys:
# GROQ_API_KEY=
# NEWS_API_KEY=
```

### 3. Run the API
```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Test it
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "company_name": "Apple Inc"}'
```

## Key Design Decisions

**Blackboard architecture** — agents never communicate directly. All state flows through `FinancialContext`. This means any agent can be swapped, upgraded, or removed without touching the others.

**Token budget enforcement** — the orchestrator tracks token usage per agent and skips agents when budget is exhausted. Prevents cost overruns on complex queries.

**Fault tolerance** — each agent runs inside a try/except block. One agent failing doesn't crash the pipeline. The report agent produces a memo with whatever data is available.

**Typed state** — Pydantic v2 with `validate_assignment=True` catches wrong data types the moment they're assigned, not somewhere deep in production.

**Real data** — web search is real (NewsAPI), financial data is real (Yahoo Finance), AI inference is real (Groq). Nothing is mocked.

## Validation Results

| Company | Overall Risk | Result |
|---|---|---|
| Apple (AAPL) | 5.75/10 | Medium risk |
| SVB (SIVBQ) | 8.0/10 | High risk (collapsed 2023) |
| Beyond Meat (BYND) | 7.0/10 | High risk (struggling) |
| Tesla (TSLA) | 7.5/10 | Medium-high risk|

## Roadmap

- [ ] Phase 6 — Evaluation pipeline + meta agent
- [ ] Phase 7 — MCP + A2A protocol integration
- [ ] Docker deployment
- [ ] Frontend dashboard
- [ ] ChromaDB long term memory
- [ ] Streaming synthesis

## Known Limitations

- Token tracking is approximate (not exact Groq token counts)
- NewsAPI free tier limited to 100 requests/day
- LLM-as-judge evaluation introduces self-bias
- No authentication on API endpoints (development only)

## Production Safety Backlog

- [ ] Input sanitization
- [ ] Rate limiting on all endpoints
- [ ] API key authentication
- [ ] SOC 2 compliant data handling
- [ ] Secrets rotation strategy