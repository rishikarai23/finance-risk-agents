import chromadb
from core.context import FinancialContext
from datetime import datetime

class Financial_Memory:
    def __init__(self):
        self.client = chromadb.PersistentClient(path = "../data/chromadb")
        self.collection = self.client.get_or_create_collection(
            name="financialAnalysisBot",
            metadata={"hnsw:space" : "cosine"}
        )

    def store_analysis(self,context:FinancialContext) -> None:
        if not context.final_memo:
            return
        doc_id = f"{context.ticker}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.collection.add(
            documents= context.final_memo,
            metadatas={
                "ticker" : context.ticker,
                "company_name" : context.company_name,
                "overall_risk" : context.overall_risk,
                "sentiment_score" : context.sentiment_score,
                "contradictions_count" : len(context.contradictions),
                "tokens_used" : context.tokens_used,
                "date" : datetime.now().isoformat
            },
            ids=[doc_id]
        )

    def get_previous_analysis(self,ticker:str,n=3) -> list[dict]:
        results = self.collection.query(
            query_texts=[f"{ticker} financial risk analysis"],
            n_results=n,
            where={"ticker": ticker}
        )

        analyses = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                analyses.append({
                    "memo": doc,
                    "metadata": results["metadatas"][0][i]
                })

        return analyses
    
    def get_risk_trend(self,ticker:str) -> list[dict]:
        results = self.collection.query(
            where={ticker:ticker},
            include=["metadatas"]
        )
        if not results["metadatas"]:
            return []
        trend = sorted(
            results["metadatas"],
            key=lambda x: x["date"]
        )
        return trend