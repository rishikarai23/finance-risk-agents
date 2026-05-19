import os
import json
import yfinance as yf
from core.context import FinancialContext
from core.prompts import FINANCIAL_AGENT_PROMPT
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
"""
P/E ratio — is the stock expensive or cheap relative to earnings?
Debt to equity — how much has the company borrowed vs what it owns?
Revenue growth — is it growing or shrinking?
Current ratio — can it pay its bills in the short term?
Return on equity — how efficiently is it using investor money?
"""
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

def fetch_financial_data(ticker : str) -> dict:
    """Fetches real financial data from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        data = {
            "pe_ratio" : info.get("trailingPE"),
            "debt_to_equity" : info.get("debtToEquity"),
            "revenue_growth" : info.get("revenueGrowth"),
            "current_ratio" : info.get("currentRatio"),
            "return_on_equity" : info.get("returnOnEquity"),
            "market_cap" : info.get("marketCap"),
            "total_revenue" : info.get("totalRevenue"),
            "gross_margins" : info.get("grossMargins")
        }
        missing = [key for key,value in data.items() if value is None ]
        if missing:
            data["missing_financial_fields"] = missing
            data["financial_data_quality"] = "partial"
        else:
            data["financial_data_quality"] = "complete"
        return data
    except Exception as e:
        return {
            "error" : str(e),
            "data_quality" : "failed"
        }
    
def analyze_financial_data(data : dict,company_name : str) -> dict:
    """Sends raw financial data to groq for analysis"""
    data_text = "\n".join([
        f"{key}: {value}" 
        for key, value in data.items()
    ])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages = [
            {"role":"system","content":FINANCIAL_AGENT_PROMPT},
            {"role":"user", "content": f"Analyze these financial metrics for {company_name}:\n\n{data_text}"}
        ],
        temperature=0,
        max_tokens=1500
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
        parsed = json.loads(clean)
        parsed["tokens_used"] = response.usage.total_tokens
        return parsed
    except json.JSONDecodeError:
        return {
            "analysis": raw,
            "flags": [],
            "data_quality_note": "Could not parse structured response",
            "tokens_used": response.usage.total_tokens
        }
    
async def run(context: FinancialContext) -> FinancialContext:
    "Main function Orchestrator calls this"
    context.current_agent = "financial_agent"
    context.audit_log.append(
        f"[financial agent] started - fetching data for {context.ticker}"
    )
    raw_data = fetch_financial_data(context.ticker)
    analysis = analyze_financial_data(raw_data,context.company_name)
    context.pe_ratio = raw_data.get("pe_ratio")
    context.debt_to_equity = raw_data.get("debt_to_equity")
    context.revenue_growth = raw_data.get("revenue_growth")
    context.current_ratio = raw_data.get("current_ratio")
    context.return_on_equity = raw_data.get("return_on_equity")
    context.market_cap = raw_data.get("market_cap")
    context.total_revenue = raw_data.get("total_revenue")
    context.gross_margins = raw_data.get("gross_margins")
    context.financial_data_quality = raw_data.get("financial_data_quality")
    context.missing_financial_fields = raw_data.get("missing_financial_fields",[])

    overall = analysis.get("overall_assessment","")
    context.financial_analysis = overall

    flags = analysis.get("flags")
    context.audit_log.append(
        f"[financial_agent] completed — {len(flags)} flags raised"
    )
    if flags:
        for flag in flags:
            context.audit_log.append(f"[financial_agent] flag: {flag}")
    context.tokens_used += analysis.get('tokens_used') or 0
    return context
    

