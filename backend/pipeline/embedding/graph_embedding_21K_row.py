import requests
from neo4j import GraphDatabase
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
# ==========================================
# 1. CẤU HÌNH KẾT NỐI
# ==========================================
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "123456789"


driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASS))
model = SentenceTransformer('keepitreal/vietnamese-sbert', device='mps')
# ==========================================
# 2. HÀM GỌI OLLAMA ĐỂ ĐÚC VECTOR
# ==========================================
def get_vector_embedding(text):
    try:
        vector = model.encode(text)
        return vector.tolist()
    except Exception as e:
        print(f"Lỗi tạo vector: {e}")
        return []

# ==========================================
# 3. TIẾN HÀNH QUÉT VÀ NẠP VECTOR
# ==========================================
print("🔍 Đang tìm các node Chunk chưa có Vector Embedding...")

# Lấy ra danh sách các Chunk chưa có thuộc tính embedding
get_chunks_query = """
MATCH (c:Chunk) 
WHERE c.embedding IS NULL AND c.text IS NOT NULL
RETURN c.id AS id, c.text AS text
"""

with driver.session() as session:
    results = session.run(get_chunks_query)
    chunks = [{"id": record["id"], "text": record["text"]} for record in results]
    
    if not chunks:
        print(" Tuyệt vời! Toàn bộ các Chunk đã được nạp Vector từ trước rồi!")
    else:
        print(f" Tìm thấy {len(chunks)} Chunk cần xử lý. Bắt đầu đúc bê tông số...")
        
        # Cập nhật từng node một (hoặc có thể chia batch nếu muốn)
        update_query = """
        MATCH (c:Chunk {id: $chunk_id})
        SET c.embedding = $embedding
        """
        
        for chunk in tqdm(chunks, desc="Đúc Vector"):
            # 1. Đi lấy mảng số từ Ollama
            vector = get_vector_embedding(chunk["text"])
            
            if vector:
                # 2. Bắn ngược mảng số vào Neo4j
                session.run(update_query, chunk_id=chunk["id"], embedding=vector)
            else:
                print(f"  Bỏ qua chunk {chunk['id']} do lỗi tạo Vector.")

driver.close()
print("\n  HOÀN THÀNH BƯỚC 1! Bây giờ tất cả các miếng thịt (Chunk) của bác đã sở hữu tọa độ không gian Vector xịn sò!")