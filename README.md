# Finance Risk Intelligence: Multi-Agent System

A multi-agent AI system for automated financial risk analysis of publicly traded companies. The system combines specialized agents, centralized state management, real-time streaming, and a full audit trail to generate structured financial risk reports.


## What it does

Provide a company ticker and company name.

The system launches specialized AI agents that:

- Gather financial and news data
- Analyze market sentiment
- Compute multidimensional risk scores
- Detect inconsistencies across findings
- Generate a structured analyst-style risk memo

The output resembles the workflow of a financial analyst, but is fully automated.


## Architecture

This system follows a **blackboard architecture** where all agents communicate through a shared typed state object (`FinancialContext`) implemented using **Pydantic v2**.

Agents never communicate directly with each other.

Instead:

```text
Agent → FinancialContext → Agent
```

The shared state acts as a central memory layer where agents read existing information and write updated results.

### Workflow

```text
User Request
      ↓
Master Orchestrator
(token budget, routing, fault tolerance)
      ↓
 News Agent       → NewsAPI search      
 Financial Agent  → Yahoo Finance data  
 Risk Scorer      → 4D risk analysis    
 Contradiction    → Cross-agent checks  
 Sentiment Agent  → Tone analysis       
 Report Agent     → Structured memo     

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
| Groq API | LLM inference (`llama-3.1-8b-instant`) |
| LangGraph | Agent orchestration |
| Pydantic v2 | Typed state validation |
| FastAPI | REST and WebSocket API |
| yfinance | Financial data |
| NewsAPI | News retrieval |
| ChromaDB | Long-term memory |
| Docker Compose | Containerization |



## API Endpoints

### REST

**POST /analyze**

```json
{
    "ticker":"AAPL",
    "company_name":"Apple Inc",
    "max_tokens":50000
}
```

### WebSocket

**WS /analyze/stream**

Features:

- Live agent execution updates
- Incremental status messages
- Final memo upon completion

### Documentation

```text
GET /docs
```

Interactive Swagger UI available through FastAPI.


## Sample Output

```json
{
  "overall_risk":5.75,
  "sentiment_score":-0.4,
  "contradictions":4,
  "final_memo":"MEDIUM RISK — Apple Inc shows strong profitability...",
  "tokens_used":9500
}
```


## Setup

### Clone repository

```bash
git clone https://github.com/rishikarai23/Multi_Agent.git

cd Multi_Agent

python3 -m venv venv

source venv/bin/activate

pip install ".[dev]"
```

### Configure environment

```bash
cp .env.example .env
```

Add:

```env
GROQ_API_KEY=
NEWS_API_KEY=
```

### Run API

```bash
uvicorn api.main:app --reload --port 8000
```

### Test API

```bash
curl -X POST http://localhost:8000/analyze \
-H "Content-Type: application/json" \
-d '{"ticker":"AAPL","company_name":"Apple Inc"}'
```


## Key Design Decisions

### Blackboard Architecture

Agents never communicate directly.

Benefits:

- Loose coupling
- Easier upgrades
- Simplified debugging
- Plug-and-play agent replacement


### Token Budget Enforcement

The orchestrator tracks token consumption across agents and can skip lower-priority agents when limits are reached.

Benefits:

- Prevents excessive inference cost
- Maintains predictable execution


### Fault Tolerance

Every agent executes independently inside exception handling.

Benefits:

- Single-agent failure does not terminate the pipeline
- Partial reports remain available


### Typed State Validation

`Pydantic v2` with `validate_assignment=True` validates state during assignment.

Benefits:

- Early error detection
- Reduced runtime failures


### Real Data Sources

All external information comes from live services:

- NewsAPI
- Yahoo Finance
- Groq LLM inference

No mock data is used.


## Validation Results

| Company | Overall Risk | Classification |
|---|---:|---|
| Apple (AAPL) | 5.75/10 | Medium |
| SVB (SIVBQ) | 8.00/10 | High |
| Beyond Meat (BYND) | 7.00/10 | High |
| Tesla (TSLA) | 7.50/10 | Medium–High |


## Roadmap

- [ ] Evaluation pipeline + meta-agent
- [ ] MCP + A2A protocol integration
- [ ] Docker deployment
- [ ] Frontend dashboard
- [ ] Streaming synthesis improvements


## Known Limitations

- Token tracking uses estimates rather than exact provider counts
- NewsAPI free tier restrictions apply
- LLM-based evaluation can introduce model bias
- Authentication not yet implemented


## Production Safety Backlog

- [ ] Input sanitization
- [ ] API rate limiting
- [ ] Authentication and API keys
- [ ] Secrets rotation strategy
- [ ] Compliance and secure data handling