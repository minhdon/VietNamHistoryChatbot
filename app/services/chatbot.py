import requests
import json
from app.services.retriever import retrieve_context 
from app.prompts.history_chat import ask_llm
from fastapi.responses import StreamingResponse

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1"

def chat_stream(question, context_list):
    # 🌟 CÁCH 1: In trực tiếp ra Terminal của Backend để kiểm tra chéo
    print("\n[DEBUG] --- DANH SÁCH CONTEXT NHẬN TỪ NEO4J ---")
    print(json.dumps(context_list, indent=2, ensure_ascii=False))
    print("-----------------------------------------------\n")

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
        for line in response.iter_lines():
            if line:
                chunk_json = json.loads(line.decode('utf-8'))
                yield f"data: {json.dumps({'type': 'content', 'delta': chunk_json.get('response', '')}, ensure_ascii=False)}\n\n"
                
    return StreamingResponse(stream_response(), media_type="text/event-stream")