import os
import json
from dotenv import load_dotenv
from core.context import FinancialContext
from core.prompts import CONTRADICTION_AGENT_PROMPT
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def prepare_input_data(context: FinancialContext) -> dict:
    """Prepare Input for Groq"""
    return {
        "company_name" : context.company_name,
        "news_article" : context.news_articles,
        "news_summary" : context.news_summary,
        "pe_ratio" : context.pe_ratio,
        "debt_to_equity" : context.debt_to_equity,
        "revenue_growth" : context.revenue_growth,
        "current_ratio" : context.current_ratio,
        "return_on_equity" : context.return_on_equity,
        "market_cap" : context.market_cap,
        "total_revenue" : context.total_revenue,
        "gross_margin" : context.gross_margins,
        "financial_data_quality" : context.financial_data_quality,
        "missing_financial_fields" : context.missing_financial_fields,
        "financial_analysis" : context.financial_analysis,
        "liquidity_risk" : context.liquidity_risk,
        "credit_risk" : context.credit_risk,
        "concentration_risk" : context.concentration_risk,
        "market_risk" : context.market_risk,
        "risk_analysis" : context.risk_analysis
    }

def get_contradictions(data_text: dict,company_name: str) -> dict:
    data_text = "\n".join([
        f"{key}: {value}"
        for key, value in data_text.items()
    ])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":CONTRADICTION_AGENT_PROMPT},
            {"role":"user","content":f"Analyze this financial metrics and find contradictions for {company_name} with the following details:\n {data_text}"}
        ],
        temperature=0.3,
        max_tokens=2000
    )
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
            "contradictions": [],
        }
    
async def run(context:FinancialContext) -> FinancialContext:
    context.current_agent = "contradiction_agent"
    context.audit_log.append(
        f"[contradiction agent] started - for company {context.company_name}"
    )
    input_data = prepare_input_data(context)
    groq_output = get_contradictions(input_data,context.company_name)
    raw_contradictions = groq_output.get("contradictions") or []
    context.contradictions = [
        f"{c.get('claim', '')} — Reality: {c.get('reality', '')} (Severity: {c.get('severity', '')}, Source: {c.get('source', '')})"
        if isinstance(c, dict) else str(c)
        for c in raw_contradictions
    ]
    context.audit_log.append(
            f"[contradiction agent] ended : there were {len(context.contradictions)}"
    )
    context.tokens_used += 1500
    return context