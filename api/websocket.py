from fastapi import WebSocket
from agents.orchestrator import run as orchestrator_run
from collections import defaultdict
from datetime import datetime, timedelta

request_count = defaultdict(list)

def is_rate_limit_exceeded(client_ip: str)->bool:
    now = datetime.now()
    request_count[client_ip] = [
        t for t in request_count[client_ip]
        if now-t < timedelta(days=1)
    ]
    requests_today = request_count[client_ip]
    requests_last_minute = [
        t for t in requests_today
        if now-t < timedelta(minutes=1)
    ]
    if len(requests_last_minute) > 5:
        return True
    if len(requests_today) > 20:
        return True
    
    return False


async def websocket_endpoint(websocket: WebSocket):
    """Streams live agents api to user"""
    await websocket.accept()
    client_ip = websocket.client.host
    if is_rate_limit_exceeded(client_ip):
        await websocket.send_json({
            "error": "Rate limit exceeded. Max 5 per minute, 20 per day."
        })
        await websocket.close()
        return
    request_count[client_ip].append(datetime.now())
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