import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm
import time

# ==========================================
# 1. CẤU HÌNH KẾT NỐI
# ==========================================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "123456789" # Mật khẩu mới

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# ==========================================
# 2. ĐỌC FILE ĐÃ CÓ SẴN VECTOR TỪ KAGGLE
# ==========================================
print("⏳ Đang đọc file Vector 1 triệu dòng từ Kaggle...")
# ĐỔI ĐƯỜNG DẪN NÀY trỏ đúng vào file bạn tải về từ Kaggle
df = pd.read_parquet("../../data/vectorDatabase/dataset_with_embeddings.parquet") 

# ==========================================
# 3. HÀM GHI VÀO NEO4J SIÊU TỐC
# ==========================================
def write_vectors_batch(tx, batch_data):
    query = """
    UNWIND $batch AS row
    MERGE (c:Chunk {id: row.id})
    SET c.text = row.text,
        c.embedding = row.embedding
    """
    tx.run(query, batch=batch_data)

# ==========================================
# 4. CHẠY BATCH (KHÔNG CẦN ENCODE)
# ==========================================
BATCH_SIZE = 2000 # Nạp 2000 dòng mỗi lô cho lẹ

print(f"🚀 Bắt đầu bắn Vector vào Neo4j (Tổng: {len(df)} dòng)...")
start_time = time.time()

with tqdm(total=len(df), desc="Nạp Vector Kaggle") as pbar:
    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i : i + BATCH_SIZE]
        
        # Đóng gói dữ liệu thành List of Dicts
        batch_data = []
        for _, row in batch_df.iterrows():
            batch_data.append({
                "id": row['id'],
                "text": row['text'],
                # Ép mảng numpy về dạng list chuẩn để Neo4j đọc được
                "embedding": row['embedding'].tolist() if hasattr(row['embedding'], 'tolist') else list(row['embedding'])
            })
            
        # Bắn thẳng vào DB
        with driver.session() as session:
            session.execute_write(write_vectors_batch, batch_data)
            
        pbar.update(len(batch_df))

driver.close()
total_time = (time.time() - start_time) / 60
print(f"\n✅ HOÀN THÀNH NẠP 1 TRIỆU VECTOR TRONG {total_time:.2f} PHÚT!")