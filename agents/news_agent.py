import httpx
import os
import json
import datetime
from dotenv import load_dotenv
from core.context import FinancialContext
from core.budget import TokenBudget
from core.prompts import NEWS_AGENT_PROMPT
from groq import Groq


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def search_news(company_name : str,ticker : str) -> list[str]:
    current_year = datetime.datetime.now().year
    """Fetches real headlines using duckduckgo"""
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

def summarize_news(raw_results : list[str] , company_name : str) -> str:
    """This will summarize the results for the company using the new results from the search part"""
    news_text = "\n".join(raw_results)

    response = client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        messages = [
            {"role":"system","content":NEWS_AGENT_PROMPT},
            {
                "role":"user",
                "content":f"summarize these news about {company_name}:\n\n{news_text}"
            }
        ],
        temperature=0,
        max_tokens=1000,
    )
    return response.choices[0].message.content

async def run(context: FinancialContext) -> FinancialContext:
    context.current_agent = "news_agent"
    context.audit_log.append(
        f"[news_agent] started: searching for news {context.ticker}"
    )
    raw_news = await search_news(context.company_name,context.ticker)
    summary = summarize_news(raw_news,context.company_name)
    context.news_articles = raw_news
    context.audit_log.append(
    f"[news_agent] summary : {summary}"
    )
    context.tokens_used += 1000
    return context

