import pandas as pd
import json
import requests
from tqdm.auto import tqdm
import re
import os
import unicodedata

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN TRÊN MAC (Dựa theo Terminal của bác)
# ==========================================
# Trỏ ngược ra thư mục data từ thư mục pipeline
INPUT_PATH = "../data/process/dataset_final_clean.parquet"
OUTPUT_PATH = "../data/process/dataset_final_graphrag_12000_21943.parquet"

print(" Đang đọc file dữ liệu từ thư mục data/process...")
if not os.path.exists(INPUT_PATH):
    print(f" LỖI: Không tìm thấy file tại {INPUT_PATH}!")
    exit()

# 👉 CHẠY THỬ ĐÚNG 10 DÒNG NHƯ BÁC YÊU CẦU
df = pd.read_parquet(INPUT_PATH)

# ==========================================
# 2. HÀM PYTHON TỰ ĐỘNG DỌN RÁC TIẾNG VIỆT
# ==========================================
# ==========================================
# 2. HÀM PYTHON TỰ ĐỘNG DỌN RÁC TIẾNG VIỆT (ĐÃ FIX LỖI CHỮ Đ)
# ==========================================
def clean_rel_name(text):
    if not text:
        return "LIEN_QUAN"
    
    # 1. Ép kiểu và trị dứt điểm chữ Đ/đ trước
    text = str(text).replace('đ', 'd').replace('Đ', 'D')
    
    # 2. Lột sạch các dấu tiếng Việt còn lại
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    
    # 3. Thay khoảng trắng/ký tự lạ bằng dấu gạch dưới _, viết hoa toàn bộ
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '_', text).upper().strip('_')
    
    return cleaned if cleaned else "LIEN_QUAN"
# ==========================================
# 3. HÀM GỌI OLLAMA (CHẠY NGẦM TRÊN MACBOOK)
# ==========================================
def extract_edges_ollama(text, nodes_json):
    prompt = f"""Bạn là chuyên gia trích xuất Đồ thị Tri thức Lịch sử.
    
    NHIỆM VỤ CỦA BẠN:
    1. Đọc VĂN BẢN GỐC. BỔ SUNG các Tên Sự Kiện (Trận đánh, Khởi nghĩa...) hoặc Tên Văn Bản (Hiệp định, Chiếu chỉ...) quan trọng bị thiếu vào "new_nodes". Tuyệt đối không bịa thêm tên không có thật trong văn bản.
    2. Vẽ các mối quan hệ (edges) nối các thực thể.
    
    QUY TẮC BẮT BUỘC:
    - Tên quan hệ (rel) là MỘT ĐỘNG TỪ/CỤM ĐỘNG TỪ TIẾNG VIỆT NGẮN GỌN (Ví dụ: nhường ngôi, thành lập, gia nhập, ký kết, đánh bại, bình thường hóa). 
    - Tuyệt đối KHÔNG nhét tên riêng vào tên quan hệ (Sai: "gia nhập ASEAN" -> Đúng: "gia nhập").
    
    MẪU JSON ĐẦU RA: 
    {{
        "new_nodes": {{
            "SuKien": ["Tên Sự Kiện 1"],
            "VanBan": ["Tên Văn Bản 1"]
        }},
        "edges": [
            {{"source": "Thực thể A", "rel": "tên quan hệ", "target": "Thực thể B"}}
        ]
    }}

    VĂN BẢN GỐC: "{text}"
    THỰC THỂ ĐÃ CÓ: {nodes_json}
    """

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "format": "json" # Ép Llama 3 nhả chuẩn JSON
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        result_text = response.json().get('response', '{}')
        
        # Bắt Object JSON
        match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if not match: return "{}"
        
        # Đọc JSON và cho Python lột dấu tiếng Việt của quan hệ
        data = json.loads(match.group(0))
        if "edges" in data:
            for edge in data["edges"]:
                if "rel" in edge:
                    edge["rel"] = clean_rel_name(edge["rel"])
                    
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        return "{}"

# ==========================================
# 4. TIẾN HÀNH BÀO DATA VỚI TQDM
# ==========================================
print("\n Bắt đầu nhờ Ollama đọc và nối dây (Test 10 dòng)...")
tqdm.pandas(desc="Tiến độ Llama 3 (Local)")

def process_row(row):
    text = str(row['user']) + " " + str(row['assistant'])
    nodes = str(row['entities_json'])
    
    if nodes == "{}" or nodes == "" or nodes == "null":
        return "{}"
        
    return extract_edges_ollama(text, nodes)

df['relationships_json'] = df.progress_apply(process_row, axis=1)

# ==========================================
# 5. NGHIỆM THU KẾT QUẢ
# ==========================================
print("\n👀 KẾT QUẢ NGHIỆM THU (3 DÒNG ĐẦU TIÊN):")
for index, row in df.head(3).iterrows():
    print("-" * 80)
    print(f" Nodes gốc (PhoBERT): {row['entities_json']}")
    print(f" Kết quả mới (Llama 3 + Python fix): {row['relationships_json']}")

print("\nĐang lưu file test...")
df.to_parquet(OUTPUT_PATH, index=False)
print(f" XONG! File test đã nằm tại: {OUTPUT_PATH}")