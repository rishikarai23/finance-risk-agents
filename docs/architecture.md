# Architecture Documentation

## Agent Temperature Map

| Agent | Temperature | Reason |
|---|---|---|
| Orchestrator | 0 | Pure logic, deterministic routing, no creativity needed |
| News Agent | 0.7 | Needs creative angle finding across different sources |
| Financial Agent | 0 | Numbers are facts, must be precise and repeatable |
| Risk Scorer | 0 | Scoring must be deterministic, same input = same score |
| Contradiction Agent | 0.3 | Mostly factual but needs flexibility to spot subtle mismatches |
| Sentiment Agent | 0.5 | Structured analysis but needs nuance to read tone |
| Report Agent | 0.7 | Memo must be readable and well written, not robotic |


## core/context.py — FinancialContext

### What it is
The single shared state object that flows through all 7 agents.
No agent talks directly to another — they all read from and write to this object.
This pattern is called a **blackboard architecture**.

### Why Pydantic
- Data validation at assignment time, not at runtime deep in production
- Every field has a declared type — no ambiguous dictionaries
- `validate_assignment=True` means wrong types are rejected immediately
- Serialization to JSON with one call: `context.model_dump()`
- Critical in financial systems where ambiguous data is a compliance risk

### Why Optional fields
Most fields start as `None` because only the ticker and company name
are known at the start. Each agent fills in its own fields as it runs.
`Optional[float] = None` means "this will exist eventually, blank for now."

### Why Field(default_factory=list)
Writing `= []` directly causes all instances to share the same list in memory.
`default_factory=list` creates a fresh empty list for every new context instance.

### Fields and which agent owns them

| Field | Type | Owner |
|---|---|---|
| ticker | str | User input |
| company_name | str | User input |
| news_articles | list[str] | News Agent |
| pe_ratio | Optional[float] | Financial Agent |
| debt_to_equity | Optional[float] | Financial Agent |
| revenue_growth | Optional[float] | Financial Agent |
| liquidity_risk | Optional[float] | Risk Scorer |
| credit_risk | Optional[float] | Risk Scorer |
| overall_risk | Optional[float] | Risk Scorer |
| contradictions | list[str] | Contradiction Agent |
| sentiment_score | Optional[float] | Sentiment Agent |
| sentiment_signals | list[str] | Sentiment Agent |
| final_memo | Optional[str] | Report Agent |
| tokens_used | int | Orchestrator |
| current_agent | Optional[str] | Orchestrator |
| audit_log | list[str] | Orchestrator |
| created_at | str | Auto-generated |

---

## core/budget.py — TokenBudget

### What it is
Tracks token usage across all agents per run.
Prevents cost overruns and context window exhaustion.

### Why it exists
Without a budget, agents keep calling the API until the task is done.
One complex run could exhaust all credits or fill the context window,
causing later agents to lose context and hallucinate.

### How it works
- `consume(agent_name, tokens)` — called after every agent run
- `can_proceed(estimated_tokens)` — checked before every agent runs
- `summary()` — full breakdown of usage per agent
- Default budget: 50,000 tokens per run (set in .env)

### Three level memory strategy
- **Short term** — last 2 agent rounds fully in context window
- **Medium term** — older rounds compressed into dense summaries
- **Long term** — stored in ChromaDB, searchable by meaning