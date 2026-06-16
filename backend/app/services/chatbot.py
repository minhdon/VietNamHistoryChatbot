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
from backend.app.services.analyzer_questions import decompose_questions

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1"

def chat_stream(question: str, context_list: list, session_id: str, db: Session):
    # 1. Đảm bảo phiên chat (Session mẹ) đã tồn tại vững chắc trong Postgres
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not db_session:
        print(f"➕ [DB] Chưa có Session {session_id}, tiến hành tạo mới...")
        title = question[:50] + "..." if len(question) > 50 else question
        db_session = ChatSession(id=session_id, title=title)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    
    # 2. Lưu câu hỏi GỐC (chứa chuỗi nhiều câu hỏi hoặc đoạn văn bản OCR) của User vào DB
    try:
        user_msg = ChatMessage(session_id=session_id, role="user", content=question)
        db.add(user_msg)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi lưu tin nhắn user: {e}")
        raise e

    # 3. GỌI HÀM PHÂN RÃ CÂU HỎI (Tách chuỗi thô thành mảng câu hỏi đơn)
    # Ví dụ: ["Câu hỏi 1", "Câu hỏi 2"]
    sub_questions = decompose_questions(question)
    print(f"🔍 [DEBUG MULTI-QUERY] Đã phân rã thành {len(sub_questions)} câu hỏi nhỏ: {sub_questions}")
    
    def stream_response():
        full_ai_answer = ""
        
        # 🔑 VÒNG LẶP VÀNG: Duyệt qua từng câu hỏi nhỏ để xử lý gối đầu nhau
        for index, sub_q in enumerate(sub_questions):
            
            # IN CÂU HỎI LÊN GIAO DIỆN (NẾU CÓ NHIỀU CÂU HỎI)
            if len(sub_questions) > 1:
                question_header = f"**Câu hỏi {index + 1}: {sub_q}**\n\n"
                yield f"data: {json.dumps({'type': 'content', 'delta': question_header}, ensure_ascii=False)}\n\n"
                full_ai_answer += question_header

            # TRÍCH XUẤT CONTEXT RIÊNG CHO CÂU HỎI NHỎ NÀY TỪ NEO4J
            current_context = retrieve_context(sub_q)
            
            # In debug ra terminal backend xem nó bốc trúng tài liệu không
            print(f"\n[DEBUG] --- CONTEXT CHO CÂU HỎI {index + 1}: {sub_q} ---")
            print(json.dumps(current_context, indent=2, ensure_ascii=False))
            print("-----------------------------------------------------------\n")

            # Phát nguồn (sources) của riêng câu hỏi này lên cho FE nạp
            yield f"data: {json.dumps({'type': 'sources', 'data': current_context}, ensure_ascii=False)}\n\n"

            # Dựng prompt kết hợp context
            prompt = ask_llm(sub_q, current_context)
            
            if not prompt:
                msg_refuse = "Dữ liệu hiện tại của tôi không có thông tin về vấn đề này."
                yield f"data: {json.dumps({'type': 'content', 'delta': msg_refuse}, ensure_ascii=False)}\n\n"
                full_ai_answer += msg_refuse
                continue # Nhảy sang câu tiếp theo luôn
                
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.0,  
                    "top_p": 0.1
                }
            }
            
            # Gọi Ollama sinh chữ dạng stream cho câu hỏi hiện tại
            response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, stream=True)
            
            for line in response.iter_lines():
                if line:
                    chunk_json = json.loads(line.decode('utf-8'))
                    delta = chunk_json.get('response', '')
                    full_ai_answer += delta
                    # Bắn chữ về cho giao diện theo thời gian thực
                    yield f"data: {json.dumps({'type': 'content', 'delta': delta}, ensure_ascii=False)}\n\n"
            
            # Ngắt dòng ngăn cách rõ ràng giữa các câu hỏi cho người dùng dễ đọc trên FE
            if index < len(sub_questions) - 1:
                separator = "\n\n---\n\n"
                yield f"data: {json.dumps({'type': 'content', 'delta': separator}, ensure_ascii=False)}\n\n"
                full_ai_answer += separator

        # 🚨 ĐIỂM NEO KINH ĐIỂN: Kết thúc toàn bộ vòng lặp, AI đã trả lời xong tất cả các câu hỏi!
        # Tiến hành lưu duy nhất 1 khối câu trả lời tổng hợp này vào Postgres
        if full_ai_answer.strip():
            save_chat_message(db, session_id=session_id, role="assistant", content=full_ai_answer.strip())        
            
    return StreamingResponse(stream_response(), media_type="text/event-stream")