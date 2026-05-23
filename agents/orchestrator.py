from agents import financial_agent,news_agent,report_agent,risk_scorer,sentiment_agent,contradiction_agent
import os
from dotenv import load_dotenv
import json
from core.context import FinancialContext
from core.budget import TokenBudget
from core.memory import Financial_Memory

load_dotenv()

AGENT_PIPELINE = [
    ("news_agent",news_agent.run),
    ("financial_agent",financial_agent.run),
    ("risk_scorer_agent",risk_scorer.run),
    ("contradiction_agent",contradiction_agent.run),
    ("sentiment_agent",sentiment_agent.run),
    ("report_agent",report_agent.run)
]

AGENT_TOKEN_ESTIMATES = {
    "news_agent": 1500,
    "financial_agent": 1000,
    "risk_scorer": 1000,
    "contradiction_agent": 1500,
    "sentiment_agent": 2000,
    "report_agent": 2000,
}

async def send_update(websocket, message: str):
    """Sends a message through WebSocket if connected."""
    if websocket:
        await websocket.send_json({"update": message})

        
async def run(ticker:str,company_name:str,max_tokens:int=50000,websocket=None)->FinancialContext:
    context = FinancialContext(
        ticker=ticker,
        company_name=company_name
    )
    budget = TokenBudget(max_tokens=max_tokens)
    memory = Financial_Memory()
    previous = memory.get_previous_analysis(ticker)
    if previous:
        history_previous = []
        for p in previous:
            meta = p["metadata"]
            history_previous.append(
                f"Previous analysis ({meta['date'][:10]}): "
                f"risk={meta['overall_risk']}, "
                f"sentiment={meta['sentiment_score']}, "
                f"contradictions={meta['contradictions_count']}"
            )
        context.audit_log.append(
        f"[orchestrator] found {len(previous)} previous analyses for {ticker}"
        )
        context.audit_log.append(
            f"[orchestrator] history: {' | '.join(history_previous)}"
        )

    msg = f"[orchestrator] started — {company_name} ({ticker}), budget: {max_tokens} tokens"
    context.audit_log.append(msg)
    await send_update(websocket,msg)

    for agent_name , agent_run in AGENT_PIPELINE:
        estimated = AGENT_TOKEN_ESTIMATES.get(agent_name) or 2000
        if not budget.can_proceed(estimated):
            msg = f"[orchestrator] skipping {agent_name} — budget exhausted"
            context.audit_log.append(msg)
            await send_update(websocket,msg)
            continue

        msg = f"[orchestrator] running {agent_name}"
        context.audit_log.append(msg)
        await send_update(websocket,msg)
        try:
            tokens_before = context.tokens_used
            context = await agent_run(context)
            tokens_spent = context.tokens_used - tokens_before
            budget.consume(agent_name, tokens_spent)

        except Exception as e:
            msg = f"[orchestrator] {agent_name} failed — {str(e)}"
            context.audit_log.append(msg)
            await send_update(websocket,msg)
            continue
    
    msg = f"[orchestrator] completed — {budget.summary()['used_tokens']} tokens used"
    context.audit_log.append(msg)
    memory.store_analysis(context)
    context.audit_log.append(
        f"[orchestrator] analysis stored in memory"
    )
    await send_update(websocket,msg)

    if websocket:
        await websocket.send_json({
            "complete": True,
            "overall_risk": context.overall_risk,
            "sentiment_score": context.sentiment_score,
            "contradictions": context.contradictions,
            "final_memo": context.final_memo,
            "tokens_used": context.tokens_used,
            "audit_log" : context.audit_log
        })
        
    return context

