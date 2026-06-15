import requests
import json
from backend.app.models.chat_message import ChatMessage
from backend.app.models.chat_session import ChatSession
from backend.app.services.retriever import retrieve_context 
from backend.app.prompts.history_chat import ask_llm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.crud.chat import save_chat_message
from backend.app.crud.chat import create_chat_session
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1"

def chat_stream(question, context_list, session_id: str, db: Session):
    # 🌟 CÁCH 1: In trực tiếp ra Terminal của Backend để kiểm tra chéo
    print("\n[DEBUG] --- DANH SÁCH CONTEXT NHẬN TỪ NEO4J ---")
    print(json.dumps(context_list, indent=2, ensure_ascii=False))
    print("-----------------------------------------------\n")
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not db_session:
        print(f"➕ [DB] Chưa có Session {session_id}, tiến hành tạo mới...")
        db_session = ChatSession(id=session_id, title="Cuộc hội thoại mới")
        db.add(db_session)
        db.commit() # Ép Postgres ghi xuống đĩa cứng bảng mẹ liền!
        db.refresh(db_session)
    
    # 🚨 CHỐT CHẶN 2: Đảm bảo đối tượng session đã nằm vững chắc trong DB rồi mới lưu tin nhắn con
    try:
        user_msg = ChatMessage(session_id=session_id, role="user", content=question)
        db.add(user_msg)
        db.commit() # Ép commit tin nhắn user liền
    except Exception as e:
        db.rollback() # Nếu lỗi thì rollback để tránh nghẽn transaction
        print(f"❌ Lỗi lưu tin nhắn user: {e}")
        raise e

    # Các đoạn bên dưới giữ nguyên...
    prompt = ask_llm(question, context_list)
    
    def stream_response():
        # 🌟 CÁCH 2: Phát (yield) danh sách nguồn về cho Frontend đầu tiên trước khi chữ chạy ra
        # Tạo gói tin có type là 'sources' để Frontend dễ phân biệt với 'content'
        yield f"data: {json.dumps({'type': 'sources', 'data': context_list}, ensure_ascii=False)}\n\n"

        if not prompt:
            yield f"data: {json.dumps({'type': 'content', 'delta': 'Dữ liệu hiện tại của tôi không có thông tin về vấn đề này.'}, ensure_ascii=False)}\n\n"
            return
            
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.0,  
                "top_p": 0.1
            }
        }
        
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, stream=True)
        full_ai_answer = ""
        for line in response.iter_lines():
            if line:
                chunk_json = json.loads(line.decode('utf-8'))
                delta = chunk_json.get('response', '')
                full_ai_answer += delta
                yield f"data: {json.dumps({'type': 'content', 'delta': chunk_json.get('response', '')}, ensure_ascii=False)}\n\n"
        if full_ai_answer.strip():
            save_chat_message(db, session_id, role="assistant", content=full_ai_answer.strip())        
    return StreamingResponse(stream_response(), media_type="text/event-stream")