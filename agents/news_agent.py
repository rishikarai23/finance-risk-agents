import httpx
import os
import json
import datetime
from dotenv import load_dotenv
from core.context import FinancialContext
from core.prompts import NEWS_AGENT_PROMPT
from groq import Groq


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def search_news(company_name : str,ticker : str) -> list[str]:
    news_api_key = os.getenv("NEWS_API_KEY")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{company_name} {ticker} stock earnings revenue financial results",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 8,
        "apiKey": news_api_key,
    }
    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(url,params=params)
        data = response.json()

    results = []

    if data.get("status") == "ok":
        for article in data.get("articles", []):
            title = article.get("title", "")
            description = article.get("description", "")
            source = article.get("source", {}).get("name", "Unknown")
            published = article.get("publishedAt", "")[:10]
            results.append(f"{title} — {description} (Source: {source}, {published})")
    
    if not results:
        results = [f"No recent news found for {company_name} ({ticker})"]

    return results

def summarize_news(raw_results: list[str], company_name: str) -> dict:
    """Sends raw news to Groq, gets back structured JSON."""
    news_text = "\n".join(raw_results)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": NEWS_AGENT_PROMPT},
            {
                "role": "user",
                "content": f"Filter and structure this news about {company_name}:\n\n{news_text}"
            }
        ],
        temperature=0.7,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content

    # Strip markdown code fences if Groq wraps response in ```json
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        parsed = json.loads(clean)
        parsed['tokens_used'] = response.usage.total_tokens
        return parsed
    except json.JSONDecodeError:
        # If Groq doesn't return valid JSON, return a safe default
        return {
            "news_articles": raw_results,
            "news_summary": raw,
            "risk_signals": [],
            "tokens_used" : response.usage.total_tokens
        }

async def run(context: FinancialContext) -> FinancialContext:
    """Main agent function — orchestrator calls this."""

    context.current_agent = "news_agent"
    context.audit_log.append(
        f"[news_agent] started — searching news for {context.ticker}"
    )

    raw_news = await search_news(context.company_name, context.ticker)

    structured = summarize_news(raw_news, context.company_name)

    articles = structured.get("news_articles", [])
    context.news_articles = [
        f"{a.get('title', '')} — {a.get('summary', '')} (Source: {a.get('source', '')}, {a.get('date', '')})"
        if isinstance(a, dict) else str(a)
        for a in articles
    ]
    context.news_summary = structured.get("news_summary", "")

    # Step 4 — update audit log
    risk_signals = structured.get("risk_signals", [])
    context.audit_log.append(
        f"[news_agent] completed — {len(context.news_articles)} relevant articles, "
        f"{len(risk_signals)} risk signals found"
    )

    # Step 5 — token tracking
    context.tokens_used += structured["tokens_used"] or 0

    return context

