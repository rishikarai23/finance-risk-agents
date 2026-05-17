from fastapi import WebSocket
from agents.orchestrator import run as orchestrator_run

async def websocket_endpoint(websocket: WebSocket):
    """Streams live agents api to user"""
    await websocket.accept()

    try:
        data = await websocket.receive_json()
        ticker = data.get("ticker")
        company_name = data.get("company_name")
        max_tokens = data.get("max_tokens",50000)
        if not ticker or not company_name:
            await websocket.send_json({"error": "ticker and company_name required"})
            await websocket.close()
            return
        await orchestrator_run(
            ticker=ticker,
            company_name=company_name,
            max_tokens=max_tokens,
            websocket=websocket
        )
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()