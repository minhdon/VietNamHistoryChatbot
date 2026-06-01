import pandas as pd
import json
from neo4j import GraphDatabase
from tqdm import tqdm

# ==========================================
# 1. CẤU HÌNH NEO4J & ĐƯỜNG DẪN
# ==========================================
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "123456789" 
driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASS))

FILE_PATH = "../data/process/dataset_final_graphrag.parquet"

print(" Đang nạp siêu dữ liệu (Parquet)...")
df = pd.read_parquet(FILE_PATH)

# ==========================================
# 2. HÀNG RÀO BỌC THÉP (ÉP KIỂU DỮ LIỆU)
# ==========================================
def clean_entity_dict(d):
    """Ép mọi rác rưởi (Dict, Int, Float) về chuẩn List of Strings"""
    if not isinstance(d, dict): return {}
    clean_d = {}
    for k, v in d.items():
        if not isinstance(v, list): v = [v]
        clean_list = []
        for item in v:
            if isinstance(item, dict):
                # Trị dứt điểm lỗi "Map{DiaDanh -> String}"
                if item: clean_list.append(str(list(item.values())[0]))
            elif item is not None:
                clean_list.append(str(item))
        clean_d[k] = clean_list
    return clean_d

def clean_edges_list(edges):
    """Ép Edge về chuẩn {'source': str, 'target': str, 'rel': str}"""
    if not isinstance(edges, list): return []
    clean_e = []
    for edge in edges:
        if isinstance(edge, dict):
            src = edge.get('source', '')
            tgt = edge.get('target', '')
            rel = edge.get('rel', 'LIEN_QUAN')
            
            # Gỡ bọc nếu LLM lại nhả Dict thay vì String
            if isinstance(src, dict): src = str(list(src.values())[0]) if src else ''
            if isinstance(tgt, dict): tgt = str(list(tgt.values())[0]) if tgt else ''
            
            if src and tgt:
                clean_e.append({
                    'source': str(src),
                    'target': str(tgt),
                    'rel': str(rel).replace(' ', '_').upper()
                })
    return clean_e

# ==========================================
# 3. HÀM NẠP BATCH (Lệnh Cypher Đã Tối Ưu)
# ==========================================
def insert_complex_batch(tx, batch_data):
    # Dùng coalesce() để không bao giờ bị lỗi nếu thiếu Key
    cypher_query = """
    UNWIND $rows AS row
    
    // 1. TẠO CHUNK
    MERGE (chunk:Chunk {id: row.chunk_id})
    SET chunk.text = row.user_text + ' ' + row.assistant_text
    
    // 2. TẠO ENTITIES
    FOREACH (name IN coalesce(row.ents.Nguoi, []) | MERGE (n:NhanVat {name: name}) MERGE (n)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.DiaDanh, []) | MERGE (d:DiaDanh {name: name}) MERGE (d)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.ToChuc, []) | MERGE (t:ToChuc {name: name}) MERGE (t)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.MocThoiGian, []) | MERGE (m:ThoiGian {name: name}) MERGE (m)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.SuKien, []) | MERGE (s:SuKien {name: name}) MERGE (s)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.VanBan, []) | MERGE (v:VanBan {name: name}) MERGE (v)-[:MENTIONED_IN]->(chunk))
    
    // 3. TẠO NEW NODES
    FOREACH (name IN coalesce(row.new_nodes.SuKien, []) | MERGE (s:SuKien {name: name}) MERGE (s)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.new_nodes.VanBan, []) | MERGE (v:VanBan {name: name}) MERGE (v)-[:MENTIONED_IN]->(chunk))
    
    // 4. TẠO EDGES ĐỘNG
    WITH row, chunk
    UNWIND coalesce(row.edges, []) AS edge
    
    MERGE (source:Entity {name: edge.source}) 
    MERGE (target:Entity {name: edge.target})
    
    WITH source, target, edge
    CALL apoc.create.relationship(source, edge.rel, {}, target) YIELD rel
    RETURN count(*)
    """
    tx.run(cypher_query, rows=batch_data)

# ==========================================
# 4. TIẾN HÀNH ĐẨY DỮ LIỆU
# ==========================================
print("\n Bắt đầu đổ bê tông vào Neo4j (Phiên bản Bọc Thép)...")
BATCH_SIZE = 1000 

with driver.session() as session:
    batch = []
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Nạp Đồ Thị"):
        
        # Parse JSON an toàn bằng Python
        try: ents_raw = json.loads(row['entities_json']) if pd.notna(row['entities_json']) else {}
        except: ents_raw = {}
            
        try: rels_raw = json.loads(row['relationships_json']) if pd.notna(row['relationships_json']) else {}
        except: rels_raw = {}

        # Nếu không có bất kỳ dữ liệu nào thì bỏ qua dòng này
        if not ents_raw and not rels_raw:
            continue
            
        batch.append({
            "chunk_id": f"chunk_{index}", 
            "user_text": str(row['user']),
            "assistant_text": str(row['assistant']),
            "ents": clean_entity_dict(ents_raw),
            "new_nodes": clean_entity_dict(rels_raw.get('new_nodes', {})),
            "edges": clean_edges_list(rels_raw.get('edges', []))
        })
            
        if len(batch) == BATCH_SIZE:
            session.execute_write(insert_complex_batch, batch)
            batch = []
            
    if batch:
        session.execute_write(insert_complex_batch, batch)

driver.close()
print(" VƯỢT ẢI THÀNH CÔNG! Đồ thị đã sạch bong và nằm gọn trong Neo4j!")