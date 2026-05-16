from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime

class FinancialContext(BaseModel):

    model_config = {"strict": False, "validate_assignment": True}
    
    #Basic info provided by the user
    #It is company name like "AAPL"
    ticker : str
    #It is full Company name like "Apple Inc"
    company_name : str

    #variables produced by financial data agents
    #price to earnings ratio
    # --- Financial Data Agent ---
    pe_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    revenue_growth: Optional[float] = None
    current_ratio: Optional[float] = None
    return_on_equity: Optional[float] = None
    market_cap: Optional[float] = None
    total_revenue: Optional[float] = None
    gross_margins: Optional[float] = None
    financial_data_quality: Optional[str] = None
    missing_financial_fields: list[str] = Field(default_factory=list)
    financial_analysis: Optional[str] = None

    #News Agent
    news_articles: list[str] = Field(default_factory=list)
    news_summary: Optional[str] = None

    #prduced by risk scorer
    liquidity_risk : Optional[float] = None
    credit_risk : Optional[float] = None
    concentration_risk : Optional[float] = None
    market_risk : Optional[float] = None
    overall_risk : Optional[float] = None
    risk_analysis : Optional[str] = None

    #Contradictions agent produces
    contradictions : list[str] = Field(default_factory=list)

    #Sentiment agent produces
    sentiment_score : Optional[float] = None
    sentiment_signals : list[str] = Field(default_factory=list)

    #Report Agents
    final_memo : list[str] = Field(default_factory=list)

    #Orchestrator Agent
    tokens_used: int = 0
    current_agent: Optional[str] = None
    audit_log: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())




