import pandas as pd
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from tqdm import tqdm
import time

# ==========================================
# 1. CẤU HÌNH KẾT NỐI & MODEL
# ==========================================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "123456789"

# Load model Tiếng Việt chuẩn (Tạo vector 768 chiều)
print("⏳ Đang load model...")
model = SentenceTransformer('keepitreal/vietnamese-sbert', device='mps')
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# ==========================================
# 2. ĐỌC VÀ CHUẨN BỊ DỮ LIỆU
# ==========================================
print("⏳ Đang đọc dữ liệu 1 triệu dòng...")
# Thay 'your_data.csv' bằng đường dẫn file data thực tế của bạn
df = pd.read_parquet('../../data/raw/dataset_nodes.parquet') 

# Gộp Câu hỏi và Câu trả lời thành một khối văn bản (Chunk) giàu ngữ nghĩa
df['chunk_text'] = "Hỏi: " + df['user'].astype(str) + "\nĐáp: " + df['assistant'].astype(str)

# ==========================================
# 3. HÀM GHI DỮ LIỆU VÀO NEO4J SIÊU TỐC (UNWIND)
# ==========================================
def write_batch_to_neo4j(tx, batch_data):
    # Dùng UNWIND đẩy cả ngàn dòng vào DB trong 1 lệnh duy nhất (nhanh gấp 100 lần)
    query = """
    UNWIND $batch AS row
    MERGE (c:Chunk {id: row.id})
    SET c.text = row.text,
        c.embedding = row.embedding
    """
    tx.run(query, batch=batch_data)

# ==========================================
# 4. CHẠY VÒNG LẶP THEO LÔ (BATCH PROCESSING)
# ==========================================
# Kích thước lô: Đẩy 1000 dòng mỗi lần để không tràn RAM
BATCH_SIZE = 1000 
ENCODE_BATCH_SIZE = 256 # Số lượng câu model xử lý cùng lúc trên GPU/MPS

print(f"🚀 Bắt đầu đúc Vector và nạp vào Neo4j (Tổng: {len(df)} dòng)...")
start_time = time.time()

# Duyệt qua data mỗi bước là 1000 dòng
for i in tqdm(range(0, len(df), BATCH_SIZE), desc="Tiến trình Batch"):
    # Cắt lấy 1 lô dữ liệu
    batch_df = df.iloc[i : i + BATCH_SIZE]
    
    # Chuẩn bị danh sách text và ID
    texts = batch_df['chunk_text'].tolist()
    # Tạo ID tự động: chunk_0, chunk_1...
    ids = ["chunk_" + str(idx) for idx in batch_df.index]
    
    # 1. ĐÚC VECTOR HÀNG LOẠT TRÊN MPS
    embeddings = model.encode(texts, batch_size=ENCODE_BATCH_SIZE, show_progress_bar=False)
    
    # 2. ĐÓNG GÓI DỮ LIỆU CHUẨN BỊ ĐẨY LÊN DB
    batch_data = []
    for j in range(len(batch_df)):
        batch_data.append({
            "id": ids[j],
            "text": texts[j],
            "embedding": embeddings[j].tolist()  # Ép về list để Neo4j hiểu
        })
        
    # 3. MỞ SESSION GHI VÀO NEO4J
    with driver.session() as session:
        session.execute_write(write_batch_to_neo4j, batch_data)

driver.close()
total_time = (time.time() - start_time) / 60
print(f"✅ HOÀN THÀNH TOÀN BỘ 1 TRIỆU DÒNG TRONG {total_time:.2f} PHÚT!")