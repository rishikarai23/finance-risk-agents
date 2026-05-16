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
            "ross_margins" : info.get("grossMargins")
        }
        missing = [key for key,value in data.items if value is None ]
        if missing:
            data["missing_financial_fields"] = missing
            data["financial_data_quality"] = "partial"
        else:
            data["missing_financial_fields"] = "complete"
        return data
    except Exception as e:
        return {
            "error" : str(e),
            "data_quality" : "failed"
        }