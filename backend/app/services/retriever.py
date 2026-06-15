import time
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

# ==========================================
# 1. CẤU HÌNH KẾT NỐI
# ==========================================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "123456789"

print("⏳ Đang nạp Model Embedding (MPS)...")
model = SentenceTransformer('keepitreal/vietnamese-sbert', device='mps')
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# ==========================================
# 2. HÀM TRUY VẤN CHỐNG TRÙNG LẶP (ANTI-DUPLICATE RETRIEVER)
# ==========================================
def retrieve_context(user_query, top_k=3, threshold=0.5): # Đặt ngưỡng 0.5 để nới lỏng kết quả
    query_vector = model.encode(user_query).tolist()
    
    cypher_query = """
    CALL db.index.vector.queryNodes('chunk_embeddings', 500, $vector)
    YIELD node AS chunk, score
    WITH chunk.text AS text, max(score) AS best_score
    RETURN text, best_score
    ORDER BY best_score DESC
    LIMIT $limit
    """
    
    with driver.session() as session:
        results = session.run(cypher_query, vector=query_vector, limit=top_k)
        
        context_list = []
        for record in results:
            score = record["best_score"]
            # 🛡️ CHỐT CHẶN 1: Từ chối các vector điểm thấp
            if score >= threshold:
                context_list.append({
                    "text": record["text"],
                    "score": score
                })
        return context_list

# ==========================================
# 3. CHẠY THỬ NGHIỆM CHATBOT TRÊN TERMINAL
# ==========================================
if __name__ == "__main__":
    print("\n🤖 Hệ thống RAG đã sẵn sàng! Gõ 'exit' để thoát.")
    
    while True:
        user_input = input("\n👤 Bạn hỏi: ")
        if user_input.lower() == 'exit':
            break
            
        start_time = time.time()
        
        # Gọi tầng truy vấn
        retrieved_chunks = retrieve_context(user_input, top_k=3)
        
        print(f"\n🔍 [Kết quả tìm kiếm từ Neo4j] (Tìm xong trong {(time.time() - start_time)*1000:.2f} ms):")
        
        if not retrieved_chunks:
            print("❌ Không tìm thấy thông tin phù hợp.")
            continue
            
        # Hiển thị kết quả đã được lọc trùng
        for idx, chunk in enumerate(retrieved_chunks):
            print(f"\n--- Đoạn trích {idx+1} (Độ khớp: {chunk['score']:.4f}) ---")
            print(chunk['text'])
            
    driver.close()