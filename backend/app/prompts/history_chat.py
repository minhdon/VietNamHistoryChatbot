import requests
import json
# Import hàm tìm kiếm thần thánh từ file cũ của bạn
from backend.app.services.retriever import retrieve_context 

# ==========================================
# 1. HÀM TẠO PROMPT VÀ GỌI OLLAMA
# ==========================================
def ask_llm(question, context_list):
    # Bước A: Ép các đoạn trích thành một khối văn bản để LLM đọc
    context_text = ""
    for i, chunk in enumerate(context_list):
        context_text += f"--- TÀI LIỆU {i+1} ---\n{chunk['text']}\n\n"
        
    # Bước B: Kỹ thuật Prompt Engineering (Cấp độ 1: Trói buộc sự thật)
    prompt = f"""Bạn là một chuyên gia lịch sử Việt Nam uyên bác.
Nhiệm vụ của bạn là trả lời câu hỏi dựa TRÊN CÁC TÀI LIỆU DƯỚI ĐÂY.

{context_text}

QUY TẮC BẮT BUỘC:
1. Chỉ sử dụng thông tin từ các tài liệu trên để trả lời.
2. Nếu tài liệu không chứa câu trả lời, hãy nói chính xác câu này: "Dữ liệu hiện tại của tôi không có thông tin về vấn đề này." Tuyệt đối không tự bịa ra lịch sử.
3. Cố gắng trích dẫn nguồn nếu có thể (Ví dụ: "Dựa theo Tài liệu 1...").         

CÂU HỎI CỦA NGƯỜI DÙNG: {question}
CÂU TRẢ LỜI CỦA BẠN:"""
    return prompt