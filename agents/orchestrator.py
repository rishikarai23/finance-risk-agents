from agents import financial_agent,news_agent,report_agent,risk_scorer,sentiment_agent,contradiction_agent
import os
from dotenv import load_dotenv
import json
from core.context import FinancialContext
from core.budget import TokenBudget

load_dotenv

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

async def run(ticker:str,company_name:str,max_tokens:int=50000)->FinancialContext:
    context = FinancialContext(
        ticker=ticker,
        company_name=company_name
    )
    budget = TokenBudget(max_tokens=max_tokens)
    context.audit_log.append(
        f"[orchestrator] started — {company_name} ({ticker}), budget: {max_tokens} tokens"
    )
    for agent_name , agent_run in AGENT_PIPELINE:
        estimated = AGENT_TOKEN_ESTIMATES.get(agent_name) or 2000
        if not budget.can_proceed(estimated):
            context.audit_log.append(f"[orchestrator] skipping {agent_name} — budget exhausted")
            continue
        context.audit_log.append(
            f"[orchestrator] running {agent_name}"
        )
        try:
            context = await agent_run(context)
            budget.consume(agent_name, estimated)
        except Exception as e:
            context.audit_log.append(
                f"[orchestrator] {agent_name} failed — {str(e)}"
            )
            continue
    
    context.audit_log.append(
        f"[orchestrator] completed — {budget.summary()['used_tokens']} tokens used"
    )
    
    return context

