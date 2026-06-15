from sqlalchemy import Column, Integer, String, DateTime, Text,ForeignKey,DATETIME
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.app.database.session import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id=Column(UUID(as_uuid=True),ForeignKey("chat_sessions.id",on_delete="CASCADE"),nullable=False, index=True)
    role=Column(String, nullable=False)  # 'user' hoặc 'assistant'
    content=Column(Text, nullable=False)
    created_at=Column(DATETIME(timezone=True), server_default=func.now())
    session=relationship("ChatSession", back_populates="messages") # Thiết lập quan hệ với ChatSession