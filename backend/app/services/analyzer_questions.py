import json
import requests
import re

def decompose_questions(raw_input: str) -> list[str]:
    lines = [line.strip() for line in raw_input.split('\n') if line.strip()]
    if len(lines) <= 1:
        return [raw_input]

    # Cố gắng tự tách nếu người dùng nhập theo format đánh số: 1., 2., 3.
    numbered_lines = [line for line in lines if re.match(r'^\d+\.', line)]
    if len(numbered_lines) == len(lines) and len(lines) > 1:
        # Xóa số ở đầu để câu hỏi sạch hơn
        return [re.sub(r'^\d+\.\s*', '', line) for line in lines]

    prompt = f"""
    Bạn là một trợ lý AI ngôn ngữ học. Nhiệm vụ của bạn là đọc đoạn văn bản đầu vào và phân tách nó thành danh sách các câu hỏi lịch sử đơn lẻ, độc lập.
    Tuyệt đối CHỈ TRẢ VỀ JSON ARRAY. KHÔNG ĐƯỢC GIẢI THÍCH, KHÔNG CHÀO HỎI.
    
    Văn bản đầu vào: "{raw_input}"
    
    Ví dụ kết quả trả về đúng:
    [
        "Thành tựu quân sự thời nhà Trần là gì?",
        "Nhà Trần thành lập năm bao nhiêu?"
    ]
    """
    payload = {
        "model": "llama3.1", 
        "prompt": prompt, 
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response_text = response.json().get("response", "[]").strip()
        
        try:
            parsed = json.loads(response_text)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except:
            pass
            
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed
            except:
                pass
    except Exception as e:
        print(f"Lỗi phân rã câu hỏi: {e}")
        
    return [raw_input]