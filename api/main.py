from fastapi import FastAPI,WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.orchestrator import run as orchestrator_run
from api.websocket import websocket_endpoint
from fastapi.responses import FileResponse
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request


app = FastAPI(
    title="Finance Risk Analyzer",
    description="MultiAgent Finance Risk Analysis system",
    version="1.0.0"
)
limiter = Limiter(key_func=get_remote_address)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

class AnalyzeRequest(BaseModel):
    ticker: str
    company_name: str
    max_tokens: int = 50000

@app.get("/")
@limiter.limit("20/day;2/minute")
async def root(request: Request):
    return {
        "status" : "running","service":"Finance Risk Intelligence API"
    }

@app.post("/analyze")
@limiter.limit("20/day;1/minute")
async def analyze(request:Request,body: AnalyzeRequest):
    """
        Run full 6 agent api for a company
        Returns complete risk,memo
    """
    context = await orchestrator_run(
        ticker = body.ticker,
        company_name= body.company_name,
        max_tokens=body.max_tokens
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

@app.get('/dashboard')
@limiter.limit("60/minute")
async def dashboard(request: Request):
    return FileResponse("api/dashboard.html")

@app.get('/download_pdf')
async def downloadpdf(request:Request):
    return "hello i will become a pdf download function"
