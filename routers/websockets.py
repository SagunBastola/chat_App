from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from datetime import datetime

from core.config import settings
from db.database import SessionLocal
from models.message import Message
from services.connection_manager import manager

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Missing sub in token")

        user_id = int(sub)

    except (JWTError, ValueError, TypeError) as e:
        print(f"Authentication failed: {e}")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()
            receiver_id = data.get("receiver_id")
            content = data.get("message")

            if not receiver_id or not content:
                continue

            receiver_id = int(receiver_id)

            with SessionLocal() as db:
                new_msg = Message(
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    content=content
                )
                db.add(new_msg)
                db.commit()
                db.refresh(new_msg)

                payload = {
                    "id": new_msg.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "content": content,
                    "timestamp": new_msg.timestamp.isoformat()
                }

            await manager.send_personal_message(payload, receiver_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)