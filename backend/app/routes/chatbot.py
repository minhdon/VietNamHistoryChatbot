from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
import sqlalchemy
from backend.app.models.chat_session import ChatSession
from backend.app.models.chat_message import ChatMessage
from backend.app.services.retriever import retrieve_context
from backend.app.services.chatbot import chat_stream
from backend.app.schema.question import QuestionRequest
from backend.app.database.session import get_db
from sqlalchemy.orm import Session
from uuid import uuid4,UUID
from backend.app.crud.chat import save_chat_message, create_chat_session,get_user_chat_sessions
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from pypdf import PdfReader
from PIL import Image
import pytesseract
import io

def extract_file_content(file: UploadFile) -> str:
    content = ""
    try:
        file_bytes = file.file.read()
        if file.content_type == 'application/pdf':
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
        elif file.content_type and file.content_type.startswith('image/'):
            image = Image.open(io.BytesIO(file_bytes))
            content = pytesseract.image_to_string(image, lang='vie')
    except Exception as e:
        print(f"Lỗi trích xuất file: {e}")
    return content.strip()

router = APIRouter(
    prefix="/api",
    tags=["Chatbot"]
)
@router.post("/stream")
def stream_chatbot_response(
    question: str = Form(...),
    session_id: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_question = question.strip()
    
    if file:
        extracted_text = extract_file_content(file)
        if extracted_text:
            user_question += f"\n\n[Nội dung đính kèm]:\n{extracted_text}"

    if not user_question:
        return {"error": "Câu hỏi không được để trống."}
 
    session_id = session_id or str(uuid4())
    context = retrieve_context(user_question)
    return chat_stream(user_question, context, session_id=session_id, db=db, user_id=current_user.id)
@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = get_user_chat_sessions(db, user_id=current_user.id)
    return [{"id": str(s.id), "title": s.title, "created_at": s.created_at} for s in sessions]

@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return [{"id": str(msg.id), "role": msg.role, "content": msg.content} for msg in messages]