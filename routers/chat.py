from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List

from db.database import get_db
from models.message import Message
from models.user import User
from schemas.message import MessageResponse
from core.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat History"])

@router.get("/history/{contact_id}", response_model=List[MessageResponse])
def get_chat_history(
    contact_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = db.query(User).filter(User.id == contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Contact not found"
        )
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == contact_id),
            and_(Message.sender_id == contact_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()
    return messages