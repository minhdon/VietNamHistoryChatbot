import re
import json
import requests
import unicodedata
from backend.app.utils.db_neo4j import neo4j_db

OLLAMA_URL = "http://localhost:11434"

def split_into_chunks(text: str, max_chars: int = 500) -> list[str]:
    """Splits a long text into smaller chunks by punctuation."""
    # Split by common sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
            
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def clean_rel_name(text):
    if not text:
        return "LIEN_QUAN"
    text = str(text).replace('đ', 'd').replace('Đ', 'D')
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '_', text).upper().strip('_')
    return cleaned if cleaned else "LIEN_QUAN"

def extract_graph_elements_ollama(text: str):
    """Uses Ollama to extract Entities and Edges from a chunk of text."""
    prompt = f"""Bạn là chuyên gia trích xuất Đồ thị Tri thức Lịch sử.
    
    NHIỆM VỤ CỦA BẠN:
    Đọc đoạn văn bản dưới đây và trích xuất ra các Thực thể (Entities) và Mối quan hệ (Edges).
    
    THỰC THỂ (Entities) thuộc các loại sau:
    - "Nguoi": Tên nhân vật lịch sử
    - "DiaDanh": Tên địa lý, địa điểm
    - "ThoiGian": Mốc thời gian (ví dụ: Năm 1884, Ngày 2/9/1945)
    - "ToChuc": Tên tổ chức, đảng phái, quân đội
    - "SuKien": Tên sự kiện, chiến dịch, phong trào
    - "VanBan": Tên văn bản, hiệp định, chiếu chỉ
    
    MỐI QUAN HỆ (Edges):
    - Vẽ các mối quan hệ nối các thực thể vừa tìm được.
    - Tên quan hệ (rel) phải là MỘT ĐỘNG TỪ/CỤM ĐỘNG TỪ TIẾNG VIỆT NGẮN GỌN (Ví dụ: nhường ngôi, thành lập, gia nhập, ký kết, đánh bại).
    - Tuyệt đối KHÔNG nhét tên riêng vào tên quan hệ.
    
    MẪU JSON ĐẦU RA BẮT BUỘC:
    {{
        "entities": {{
            "Nguoi": ["Tên 1", "Tên 2"],
            "DiaDanh": [],
            "ThoiGian": [],
            "ToChuc": [],
            "SuKien": [],
            "VanBan": []
        }},
        "edges": [
            {{"source": "Tên 1", "rel": "tên quan hệ", "target": "Tên 2"}}
        ]
    }}

    VĂN BẢN GỐC: "{text}"
    """

    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        result_text = response.json().get('response', '{}')
        
        match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if not match: return {"entities": {}, "edges": []}
        
        data = json.loads(match.group(0))
        
        # Clean edge relationship names
        if "edges" in data:
            for edge in data["edges"]:
                if "rel" in edge:
                    edge["rel"] = clean_rel_name(edge["rel"])
                    
        return data
    except Exception as e:
        print(f"Lỗi khi gọi Ollama: {e}")
        return {"entities": {}, "edges": []}

def insert_chunk_to_neo4j(chunk_id: str, text: str, embedding: list, extracted_data: dict):
    """Inserts a Chunk, its Entities, and Edges into Neo4j."""
    entities = extracted_data.get("entities", {})
    edges = extracted_data.get("edges", [])
    
    # Ensure entities dictionary has all expected keys
    ents = {
        "Nguoi": entities.get("Nguoi", []),
        "DiaDanh": entities.get("DiaDanh", []),
        "ToChuc": entities.get("ToChuc", []),
        "ThoiGian": entities.get("ThoiGian", []),
        "SuKien": entities.get("SuKien", []),
        "VanBan": entities.get("VanBan", [])
    }

    # Prepare data for UNWIND
    row = {
        "chunk_id": chunk_id,
        "text": text,
        "embedding": embedding,
        "ents": ents,
        "edges": edges
    }

    # 1. Query tạo Chunk và các Entities (không cần APOC)
    base_query = """
    UNWIND $rows AS row
    MERGE (chunk:Chunk {id: row.chunk_id})
    SET chunk.text = row.text, chunk.embedding = row.embedding
    
    FOREACH (name IN coalesce(row.ents.Nguoi, []) | MERGE (n:NhanVat:Entity {name: name}) MERGE (n)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.DiaDanh, []) | MERGE (d:DiaDanh:Entity {name: name}) MERGE (d)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.ToChuc, []) | MERGE (t:ToChuc:Entity {name: name}) MERGE (t)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.ThoiGian, []) | MERGE (m:ThoiGian:Entity {name: name}) MERGE (m)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.SuKien, []) | MERGE (s:SuKien:Entity {name: name}) MERGE (s)-[:MENTIONED_IN]->(chunk))
    FOREACH (name IN coalesce(row.ents.VanBan, []) | MERGE (v:VanBan:Entity {name: name}) MERGE (v)-[:MENTIONED_IN]->(chunk))
    RETURN chunk.id
    """
    
    res = neo4j_db.query(base_query, {"rows": [row]})
    if res is None:
        raise Exception("Failed to insert chunk and entities into Neo4j")
        
    # 2. Tạo Edges riêng biệt để không dùng APOC
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        rel = edge.get("rel")
        
        if source and target and rel:
            # Tạo string cypher động vì rel type không thể dùng tham số trong cypher cơ bản
            # Lưu ý bảo mật: rel đã được clean_rel_name xử lý, chỉ chứa A-Z, 0-9, _ nên an toàn
            edge_query = f"""
            MERGE (s:Entity {{name: $source}})
            MERGE (t:Entity {{name: $target}})
            MERGE (s)-[:{rel}]->(t)
            """
            neo4j_db.query(edge_query, {"source": source, "target": target})
