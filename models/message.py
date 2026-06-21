from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    
    sender_id = Column(Integer, ForeignKey("users.id"), index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    content = Column(String)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship(
        "User", 
        foreign_keys=[sender_id], 
        back_populates="messages_sent"
    )
    
    receiver = relationship(
        "User", 
        foreign_keys=[receiver_id], 
        back_populates="messages_received"
    )