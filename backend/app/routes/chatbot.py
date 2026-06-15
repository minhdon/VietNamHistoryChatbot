from fastapi import APIRouter, Depends,HTTPException
import sqlalchemy
from backend.app.services.retriever import retrieve_context
from backend.app.services.chatbot import chat_stream
from backend.app.schema.question import QuestionRequest
from backend.app.database.session import get_db
from sqlalchemy.orm import Session
from uuid import uuid4,UUID


router = APIRouter(
    prefix="/api",
    tags=["Chatbot"]
)
@router.post("/stream")
def stream_chatbot_response(request: QuestionRequest, db: Session = Depends(get_db)):
    user_question= request.question.strip()
    if not user_question:
        return {"error": "Câu hỏi không được để trống."}
 
    session_id = request.session_id or str(uuid4())
    context=retrieve_context(user_question)
    return  chat_stream(user_question, context,session_id=session_id,db=db)