# ==========================================
# CÀI ĐẶT THƯ VIỆN 
# ==========================================


import pandas as pd
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from tqdm.auto import tqdm
import json
import re

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & KHỞI TẠO MÔ HÌNH
# ==========================================
INPUT_PATH = '/kaggle/input/datasets/anminhon/history-dataset/dataset_chats.parquet' 
OUTPUT_PATH = '/kaggle/working/dataset_nodes.parquet'

print("🔄 Đang khởi động GPU...")
device = 0 if torch.cuda.is_available() else -1

print("📥 Đang nạp mô hình PhoBERT-NER...")
model_checkpoint = "NlpHUST/ner-vietnamese-electra-base"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForTokenClassification.from_pretrained(model_checkpoint)

ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, device=device, aggregation_strategy="simple")

# ==========================================
# 2. ĐỌC DỮ LIỆU (ĐANG BẬT CHẾ ĐỘ TEST 1000 DÒNG)
# ==========================================
print("\n📊 Đang đọc file dữ liệu raw...")

# ⚠️ XÓA chữ ".head(1000)" ở dòng dưới nếu bạn muốn chạy thật 1 triệu dòng:
df = pd.read_parquet(INPUT_PATH)

texts = (df['user'].astype(str) + " " + df['assistant'].astype(str)).tolist()

# ==========================================
# 3. HÀM VÉT CẠN THỰC THỂ (NODES ONLY)
# ==========================================
def extract_nodes(model_output, raw_text):
    entities = {'Nguoi': [], 'DiaDanh': [], 'ToChuc': [], 'MocThoiGian': []}
    
    # 1. Quét nhãn từ PhoBERT
    for ent in model_output:
        label = ent['entity_group'].upper()
        word = ent['word'].replace(" ", " ").strip()
        
        if len(word) > 1:
            if label in ['PER', 'PERSON']: entities['Nguoi'].append(word)
            elif label in ['LOC', 'LOCATION']: entities['DiaDanh'].append(word)
            elif label in ['ORG', 'ORGANIZATION']: entities['ToChuc'].append(word)
            else:
                if label not in entities: entities[label] = []
                entities[label].append(word)
                
    # 2. Vớt các mốc thời gian: Bắt cả "năm 1884" và "(1884)"
    time_patterns = re.findall(r'(?i)\bnăm\s+(\d{1,4})\b|\((\d{3,4})\)', raw_text)
    for match in time_patterns:
        # match sẽ trả về tuple do có 2 điều kiện OR. Ta lấy phần tử nào có chứa số.
        y = match[0] if match[0] else match[1]
        entities['MocThoiGian'].append(f"Năm {y}")
            
    # 3. Lọc sạch mảng rỗng và loại bỏ trùng lặp
    entities_clean = {k: list(set(v)) for k, v in entities.items() if v}
    return json.dumps(entities_clean, ensure_ascii=False)

# ==========================================
# 4. CHẠY PIPELINE TRÊN GPU
# ==========================================
print("\n Bắt đầu quá trình trích xuất Nodes...")
BATCH_SIZE = 64
entities_col = []

with tqdm(total=len(texts), desc="Tiến độ GPU") as pbar:
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i : i + BATCH_SIZE]
        
        # Quét NER qua GPU
        batch_outputs = ner_pipeline(batch_texts, batch_size=BATCH_SIZE)
        
        # Format kết quả
        for text, out in zip(batch_texts, batch_outputs):
            entities_col.append(extract_nodes(out, text))
            
        pbar.update(len(batch_texts))

df['entities_json'] = entities_col

# ==========================================
# 5. IN KẾT QUẢ NGHIỆM THU & XUẤT FILE
# ==========================================
print("\n KẾT QUẢ NGHIỆM THU (3 DÒNG ĐẦU TIÊN):")
for index, row in df.head(3).iterrows():
    print("-" * 60)
    print(f" Gốc: {str(row['user'])[:80]}... {str(row['assistant'])[:80]}...") 
    print(f" Nodes: {row['entities_json']}")

print("\n Đang lưu file thành phẩm...")
df.to_parquet(OUTPUT_PATH, index=False)
print(f" XONG! Dữ liệu Nodes siêu sạch đã nằm tại: {OUTPUT_PATH}")