import requests
import json
# Import hàm tìm kiếm thần thánh từ file cũ của bạn
from backend.app.schema import question
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
Nhiệm vụ của bạn là trả lời câu hỏi dựa trên các tài liệu được cung cấp dưới đây.

{context_text}

QUY TẮC BẮT BUỘC:
1. Trả lời trực tiếp, rõ ràng vào câu hỏi của người dùng dựa trên thông tin có trong tài liệu.
2. Bạn ĐƯỢC PHÉP liên kết logic các mốc thời gian, sự kiện và ý nghĩa có trong cùng một tài liệu để đưa ra câu trả lời toàn diện (Ví dụ: Nếu tài liệu ghi sự kiện diễn ra ngày 30/4/1975 và ý nghĩa là thống nhất đất nước, bạn hoàn toàn có thể kết luận ngày 30/4/1975 là ngày thống nhất đất nước).
3. Nếu tài liệu hoàn toàn không có bất kỳ thông tin nào liên quan đến câu hỏi, hãy trả lời chính xác: "Dữ liệu hiện tại của tôi không có thông tin về vấn đề này."
4. Trích dẫn nguồn rõ ràng (Ví dụ: "Theo tài liệu 1, vào ngày 30/4/1975...").

CÂU HỎI CỦA NGƯỜI DÙNG: {question}
CÂU TRẢ LỜI CỦA BẠN:"""
    return prompt