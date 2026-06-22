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
    # 1. Accept the handshake immediately so we can handle errors gracefully
    await websocket.accept()

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Missing sub in token")

        user_id = int(sub)

    except (JWTError, ValueError, TypeError) as e:
        print(f"WebSocket Authentication failed: {e}")
        # 2. Now we can cleanly close it because the connection was accepted
        await websocket.close(code=1008)
        return

    # 3. Register connection to your manager
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

                msg_timestamp = new_msg.timestamp.isoformat() if new_msg.timestamp else datetime.utcnow().isoformat()

                payload = {
                    "id": new_msg.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "content": content,
                    "timestamp": msg_timestamp
                }

            # 4. Deliver message to the receiver
            try:
                await manager.send_personal_message(payload, receiver_id)
            except Exception as e:
                print(f"Receiver {receiver_id} is offline. Message saved to DB.")

            # 5. Echo the message back to the sender so their UI updates instantly!
            try:
                await manager.send_personal_message(payload, user_id)
            except Exception as e:
                print(f"Failed to echo back to sender: {e}")

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"Unexpected WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)