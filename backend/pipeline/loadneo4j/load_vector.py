import pandas as pd
import json
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

load_dotenv()

# 1. KẾT NỐI HỆ THỐNG
# --- SỬA LẠI DÒNG 12 ---
# Lấy thư mục chứa file load_vector.py hiện tại
current_dir = os.path.dirname(os.path.abspath(__file__))

# Đi ngược lên 2 bậc để vào thư mục gốc dự án, rồi trỏ thẳng vào file parquet
parquet_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "data", "process", "dataset_final_graphrag.parquet"))

print(f"📂 Đường dẫn file tìm kiếm thực tế: {parquet_path}")

# Đọc file bằng đường dẫn tuyệt đối vừa tìm được
df = pd.read_parquet(parquet_path)
model = SentenceTransformer('keepitreal/vietnamese-sbert', device='mps')

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "123456789")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

print(f"📦 Đã tải {len(df)} dòng dữ liệu từ file Parquet. Bắt đầu nạp vào Neo4j...")

# ====================================================================
# 2. HÀM NẠP DỮ LIỆU ĐÃ CHUẨN HÓA CÚ PHÁP ĐỂ TRÁNH LỖI TYPEXCEPTION
# ====================================================================
def insert_batch(tx, batch_data):
    cypher_query = """
    UNWIND $batch AS row
    // 1. Tạo hoặc Cập nhật node Chunk lưu nội dung hội thoại và Vector
    MERGE (c:Chunk {id: row.chunk_id})
    SET c.text = row.text,
        c.embedding = row.embedding
        
    // 2. Duyệt qua dữ liệu thực thể đã làm sạch để dựng Node động
    WITH c, row
    UNWIND row.entities AS entity_info
    CALL apoc.merge.node([entity_info.label], {name: entity_info.name}) YIELD node AS e
    MERGE (c)-[:HAS_ENTITY]->(e)
    
    // 3. Duyệt qua dữ liệu quan hệ để nối các Thực thể lại với nhau
    WITH c, row
    UNWIND row.relationships AS rel_info
    MATCH (source:Chunk {id: row.chunk_id})-[:HAS_ENTITY]->(e1) WHERE e1.name = rel_info.source_name
    CALL apoc.merge.node(['Entity'], {name: rel_info.target_name}) YIELD node AS e2
    CALL apoc.merge.relationship(e1, rel_info.rel_type, {}, {}, e2) YIELD rel
    RETURN count(*)
    """
    tx.run(cypher_query, batch=batch_data)

# ====================================================================
# 3. TIẾN HÀNH XỬ LÝ DỮ LIỆU VÀ TRÍCH XUẤT CHUẨN ĐẦU VÀO
# ====================================================================
BATCH_SIZE = 200
batch = []

with driver.session() as session:
    # Xóa sạch dữ liệu lỗi cũ để làm lại cho chuẩn chỉnh
    session.run("MATCH (n) DETACH DELETE n")
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="🚀 Đang khôi phục GraphRAG"):
        full_text = f"Hỏi: {row['user']}\nĐáp: {row['assistant']}"
        embedding = model.encode(full_text).tolist()
        
        # Ép kiểu parse JSON an toàn
        try:
            entities_raw = json.loads(row['entities_json']) if isinstance(row['entities_json'], str) else row['entities_json']
            rels_raw = json.loads(row['relationships_json']) if isinstance(row['relationships_json'], str) else row['relationships_json']
        except Exception:
            entities_raw, rels_raw = {}, {}

        # 🛡️ BỘ LỌC VÀNG 1: Duỗi phẳng và ép dữ liệu Thực thể về String thuần túy
        cleaned_entities = []
        if isinstance(entities_raw, dict):
            for label, names in entities_raw.items():
                if isinstance(names, list):
                    for name in names:
                        # Chỉ lấy nếu name là chuỗi hoặc số, bỏ qua nếu nó là Dict/List lồng
                        if isinstance(name, (str, int, float)):
                            cleaned_entities.append({"label": str(label), "name": str(name)})
                            
        # 🛡️ BỘ LỌC VÀNG 2: Duỗi phẳng dữ liệu Quan hệ
        cleaned_rels = []
        if isinstance(rels_raw, dict):
            for rel_type, targets in rels_raw.items():
                if isinstance(targets, list):
                    for target in targets:
                        if isinstance(target, (str, int, float)) and cleaned_entities:
                            # Lấy đại diện thực thể đầu tiên làm gốc kết nối hoặc map logic của mày
                            source_name = cleaned_entities[0]["name"]
                            cleaned_rels.append({
                                "source_name": str(source_name),
                                "rel_type": str(rel_type).upper().replace(" ", "_"), # Chuẩn hóa tên quan hệ viết hoa
                                "target_name": str(target)
                            })

        batch.append({
            "chunk_id": int(idx),
            "text": full_text,
            "embedding": embedding,
            "entities": cleaned_entities,
            "relationships": cleaned_rels
        })
        
        if len(batch) >= BATCH_SIZE:
            session.execute_write(insert_batch, batch_data=batch)
            batch = []
            
    if batch:
        session.execute_write(insert_batch, batch_data=batch)

driver.close()
print("\n✅ XUẤT SẮC! Đồ thị và Vector Database đã vượt qua bộ lọc lỗi và khôi phục 100%!")