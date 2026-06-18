from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.app.database.session import Base

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username=Column(String(50), unique=True, nullable=False)
    password=Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Mối quan hệ 1 - Nhiều: Một Session có nhiều Messages
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")