import os
import json
from core.context import FinancialContext
from core.prompts import RISK_SCORER_PROMPT
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

def prepare_risk_input(context: FinancialContext) -> dict:
    """prepares input for groq"""
    return {
        "company" : context.company_name,
        "ticker": context.ticker,
        "current_ratio": context.current_ratio,
        "debt_to_equity": context.debt_to_equity,
        "revenue_growth": context.revenue_growth,
        "gross_margins": context.gross_margins,
        "market_cap": context.market_cap,
        "news_summary": context.news_summary,
        "financial_analysis": context.financial_analysis,
        "data_quality": context.financial_data_quality
    }

def score_risk(risk_input: dict,company_name: str) -> dict:
    input_text = "\n".join([
        f"{key} : {value}"
        for key,value in risk_input.items()
    ])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            { "role":"system","content":RISK_SCORER_PROMPT},
            {
                "role":"user",
                "content": f"Score the financial risk for {company_name}:\n\n{input_text}"
            },
        ],
        temperature=0,
        max_tokens=1500)
    raw = response.choices[0].message.content
    clean = raw.strip()
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0]
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0]
    elif "{" in clean:
        start = clean.index("{")
        end = clean.rindex("}") + 1
        clean = clean[start:end]
    clean = clean.strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "liquidity_risk": 5.0,
            "credit_risk": 5.0,
            "concentration_risk": 5.0,
            "market_risk": 5.0,
            "overall_risk": 5.0,
            "reasoning": raw
        }
    
async def run(context:FinancialContext)->FinancialContext:
    """Orchestrator will call this for risk scoring"""
    context.current_agent = "risk_scorer_agent"
    context.audit_log.append(
        f"[risk_score_agent] started - for company {context.company_name}"
    )
    groq_input = prepare_risk_input(context)

    final_data = score_risk(groq_input,context.company_name)

    context.liquidity_risk = final_data.get("liquidity_risk")
    context.credit_risk = final_data.get("credit_risk")
    context.concentration_risk = final_data.get("concentration_risk")
    context.market_risk = final_data.get("market_risk")
    context.overall_risk = final_data.get("overall_risk")
    context.risk_analysis = final_data.get("reasoning")

    context.audit_log.append(
        f"[risk_scorer_agent] completed - overall risk: {context.overall_risk}/10"
    )

    context.tokens_used += 1500
    return context