from fastapi import APIRouter, Depends
from app.services.retriever import retrieve_context
from app.services.chatbot import chat_stream
from app.schema.question import QuestionRequest

router = APIRouter(
    prefix="/api",
    tags=["Chatbot"]
)
@router.post("/stream")
def stream_chatbot_response(request: QuestionRequest):
    user_question= request.question.strip()
    if not user_question:
        return {"error": "Câu hỏi không được để trống."}
    return  chat_stream(user_question, retrieve_context(user_question))
        