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
from core.context import FinancialContext
from weasyprint import HTML
import io
from typing import Optional
from fastapi.responses import StreamingResponse
from datetime import datetime
import os

os.environ["DYLD_LIBRARY_PATH"] = (
    "/opt/homebrew/lib:"
    "/opt/homebrew/opt/glib/lib:"
    "/opt/homebrew/opt/pango/lib"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

class PDFReport(BaseModel):
    ticker: str
    company_name: str
    overall_risk: Optional[float] = None
    sentiment_score: Optional[float] = None
    contradictions: list[str] = []
    final_memo: Optional[str] = None
    tokens_used: int = 0
    pe_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    revenue_growth: Optional[float] = None
    current_ratio: Optional[float] = None
    return_on_equity: Optional[float] = None
    gross_margins: Optional[float] = None
    liquidity_risk: Optional[float] = None
    credit_risk: Optional[float] = None
    concentration_risk: Optional[float] = None
    market_risk: Optional[float] = None
    historical_context: list[str] = []
    news_summary: Optional[str] = None
    created_at: Optional[str] = None

def build_pdf_body(body: PDFReport) -> str:
    template_path = os.path.join(BASE_DIR,"api","report_template.html")
    with open(template_path, "r") as f:
        template = f.read()
    risk = body.overall_risk or 0
    def bar_color(score):
        if score <= 3: return "#4fd1a8"
        if score <= 6: return "#f7a84f"
        return "#f87171"
    def pct(score):
        return round((score or 0) * 10)
    if body.contradictions:
        contradictions_html = "\n".join([
            f'<div class="contradictions">{c}</div>'
            for c in body.contradictions
        ])
    else:
        contradictions_html = '<p style="color:#888">No contradictions detected</p>'
    if body.historical_context:
        historical_items = "\n".join([
            f'<div class="historical-item">{h}</div>'
            for h in body.historical_context
        ])
        historical_section = f"""
        <div class="section-box">
            <h2>Historical Context</h2>
            {historical_items}
        </div>
        """
    else:
        historical_section = ""
    template = template.replace("{{contradiction_count}}", str(len(body.contradictions)))
    template = template.replace("{{overall_risk_score}}", str(risk))
    template = template.replace("{{sentiment_score}}", str(body.sentiment_score or 0))
    template = template.replace("{{pe_ratio}}", str(body.pe_ratio or "N/A"))
    template = template.replace("{{debt_to_equity}}", str(body.debt_to_equity or "N/A"))
    template = template.replace("{{revenue_growth}}", str(body.revenue_growth or "N/A"))
    template = template.replace("{{current_ratio}}", str(body.current_ratio or "N/A"))
    template = template.replace("{{return_on_equity}}", str(body.return_on_equity or "N/A"))
    template = template.replace("{{gross_margins}}", str(body.gross_margins or "N/A"))
    template = template.replace("{{contradictions_html}}", contradictions_html)
    template = template.replace("{{news_summary}}", body.news_summary or "")
    template = template.replace("{{company_name}}", body.company_name)
    template = template.replace("{{created_at}}", body.created_at or "")
    template = template.replace("{{liquidity_risk}}", str(body.liquidity_risk or 0))
    template = template.replace("{{credit_risk}}", str(body.credit_risk or 0))
    template = template.replace("{{concentration_risk}}", str(body.concentration_risk or 0))
    template = template.replace("{{market_risk}}", str(body.market_risk or 0))
    template = template.replace("{{overall_risk}}", str(risk))
    template = template.replace("{{liquidity_pct}}", str(pct(body.liquidity_risk)))
    template = template.replace("{{credit_pct}}", str(pct(body.credit_risk)))
    template = template.replace("{{concentration_pct}}", str(pct(body.concentration_risk)))
    template = template.replace("{{market_pct}}", str(pct(body.market_risk)))
    template = template.replace("{{overall_pct}}", str(pct(body.overall_risk)))
    template = template.replace("{{liquidity_color}}", bar_color(body.liquidity_risk or 0))
    template = template.replace("{{credit_color}}", bar_color(body.credit_risk or 0))
    template = template.replace("{{concentration_color}}", bar_color(body.concentration_risk or 0))
    template = template.replace("{{market_color}}", bar_color(body.market_risk or 0))
    template = template.replace("{{overall_color}}", bar_color(risk))
    template = template.replace("{{historical_section}}", historical_section)
    template = template.replace("{{final_memo}}", body.final_memo or "")
    return template


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

@app.post("/generate-pdf")
@limiter.limit("10/day;2/minute")
async def generate_pdf(request: Request, body: PDFReport):
    """Generates PDF from analysis data — no pipeline re-run."""
    html_content = build_pdf_body(body)
    pdf_bytes = HTML(string=html_content).write_pdf()
    filename = f"{body.ticker}-risk-report-{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

