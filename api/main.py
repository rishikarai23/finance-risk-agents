from fastapi import FastAPI,WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.orchestrator import run as orchestrator_run
from api.websocket import websocket_endpoint

app = FastAPI(
    title="Finance Risk Analyzer",
    description="MultiAgent Finance Risk Analysis system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    ticker: str
    company_name: str
    max_tokens: int = 50000

@app.get("/")
async def root():
    return {
        "status" : "running","service":"Finance Risk Intelligence API"
    }

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
        Run full 6 agent api for a company
        Returns complete risk,memo
    """
    context = await orchestrator_run(
        ticker = request.ticker,
        company_name= request.company_name,
        max_tokens=request.max_tokens
    )
    return {
        "ticker": context.ticker,
        "company_name": context.company_name,
        "overall_risk": context.overall_risk,
        "sentiment_score": context.sentiment_score,
        "contradictions": context.contradictions,
        "final_memo": context.final_memo,
        "tokens_used": context.tokens_used,
        "audit_log": context.audit_log,
    }

@app.websocket("/analyze/stream")
async def stream_analyze(websocket: WebSocket):
    await websocket_endpoint(websocket)