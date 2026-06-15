from sqlalchemy.orm import Session
from uuid import UUID
from backend.app.models.chat_message import ChatMessage
from backend.app.models.chat_session import ChatSession

def create_chat_session(db: Session, session_id: UUID) -> ChatSession:
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if db_session:
        db_session=ChatSession(id=session_id)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    return db_session
def save_chat_message(db: Session, session_id: UUID, role: str, content: str) -> ChatMessage:
    db_message = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
