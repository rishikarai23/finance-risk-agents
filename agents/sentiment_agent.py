import os
import json
from dotenv import load_dotenv
from core.context import FinancialContext
from core.prompts import SENTIMENT_AGENT_PROMPT
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def prepare_input(context:FinancialContext)->dict:
    return {
        "company_name": context.company_name,
        "news_summary": context.news_summary,
        "financial_analysis": context.financial_analysis,
        "risk_analysis" : context.risk_analysis,
        "contradictions" : context.contradictions,
    }

def get_sentiment(raw_input:dict,company_name:str)->list:
    input = "\n".join([
        f"{key}: {value}"
        for key,value in raw_input.items()
    ])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":SENTIMENT_AGENT_PROMPT},
            {"role":"user","content":
             f"Find the Sentiment for this company {company_name} and the follwing analysis data: \n {input}"
             }
        ],
        temperature=0.5,
        max_tokens=2500
    )
    raw_sentiment = response.choices[0].message.content
    clean = raw_sentiment.strip()
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
    
async def run(context:FinancialContext)->FinancialContext:
    context.current_agent = "sentiment_agent"
    context.audit_log.append(
        f"[sentiment_agent] started - for the company {context.company_name}"
    )
    raw_data = prepare_input(context)
    sentiment = get_sentiment(raw_data,context.company_name)
    context.sentiment_score = sentiment.get("sentiment_score")
    context.sentiment_signals = sentiment.get("signals") or []
    context.audit_log.append(
        f"[sentiment_agent] ended - for the company the sentiment score is {context.sentiment_score} and the number of sentiment signals are {len(context.sentiment_signals)}"
    )
    context.tokens_used += 2000
    return context

