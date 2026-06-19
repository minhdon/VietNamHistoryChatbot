from sqlalchemy import Column, Text, DateTime, String, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username=Column(String(50), unique=True, nullable=False)
    password=Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Mối quan hệ 1 - Nhiều: Một Session có nhiều Messages
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")