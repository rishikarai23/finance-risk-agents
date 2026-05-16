import os
from dotenv import load_dotenv
from core.context import FinancialContext
from core.prompts import REPORT_AGENT_PROMPT
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def prepare_report_input(context: FinancialContext) -> dict:
    """Packages everything from context for the final report."""
    return {
        "company_name": context.company_name,
        "ticker": context.ticker,
        "news_summary": context.news_summary,
        "pe_ratio": context.pe_ratio,
        "debt_to_equity": context.debt_to_equity,
        "revenue_growth": context.revenue_growth,
        "current_ratio": context.current_ratio,
        "return_on_equity": context.return_on_equity,
        "gross_margins": context.gross_margins,
        "financial_analysis": context.financial_analysis,
        "liquidity_risk": context.liquidity_risk,
        "credit_risk": context.credit_risk,
        "concentration_risk": context.concentration_risk,
        "market_risk": context.market_risk,
        "overall_risk": context.overall_risk,
        "risk_reasoning": context.risk_analysis,
        "contradictions": context.contradictions,
        "sentiment_score": context.sentiment_score,
        "sentiment_signals": context.sentiment_signals,
        "tokens_used": context.tokens_used,
    }


def generate_report(input_data: dict, company_name: str) -> str:
    """Sends everything to Groq, gets back a structured risk memo."""
    input_text = "\n".join([
        f"{key}: {value}"
        for key, value in input_data.items()
    ])

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": REPORT_AGENT_PROMPT},
            {
                "role": "user",
                "content": f"Generate a financial risk memo for {company_name}:\n\n{input_text}"
            }
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


async def run(context: FinancialContext) -> FinancialContext:
    """Main agent function — orchestrator calls this."""
    context.current_agent = "report_agent"
    context.audit_log.append(
        f"[report_agent] started — generating memo for {context.company_name}"
    )

    input_data = prepare_report_input(context)
    context.final_memo = generate_report(input_data, context.company_name)

    context.audit_log.append(
        f"[report_agent] completed — memo generated, {len(context.final_memo)} characters"
    )
    context.tokens_used += 2000

    return context