# app/routers/ws_dashboard.py
import json
from asyncio import sleep

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.database import SessionLocal
from app.services.dashboard import (
    get_services_with_latest_status as latest_service_statuses,
)

router = APIRouter(prefix="/ws", tags=["Dashboard"])


@router.websocket("/status")
async def ws_status(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()
    try:
        while True:
            rows = latest_service_statuses(db)
            payload = [
                {
                    "id": svc.id,
                    "name": svc.name,
                    "status": st.status.value,
                    "response_time": st.response_time,
                    "checked_at": st.checked_at.isoformat(),
                }
                for svc, st in rows
            ]
            await websocket.send_text(json.dumps(payload))
            await sleep(5)
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        db.close()
