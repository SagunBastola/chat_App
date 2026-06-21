from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import relationship
from db.database import Base #declarative base

class User(Base):
    __tablename__="users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True,index= True)
    hashed_password=Column(String)

    messages_sent=relationship("Message",foreign_keys="[Message.sender_id]",
                               back_populates="sender")
    messages_received = relationship(
        "Message", 
        foreign_keys="[Message.receiver_id]", 
        back_populates="receiver"
    )