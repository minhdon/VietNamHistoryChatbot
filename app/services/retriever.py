import requests
import logging
from app.utils.db_neo4j import neo4j_db
from sentence_transformers import SentenceTransformer
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL cua Ollama (Giong het luc ban nap du lieu)
model = SentenceTransformer('keepitreal/vietnamese-sbert', device='mps')

def get_query_embedding(text):
    vector = model.encode(text)
    return vector.tolist()

def retrieve_context(user_question: str, top_k: int = 3):
    """
    Nhan cau hoi tu user, chuyen thanh vector bang OLLAMA va tim tren Neo4j.
    """
    logger.info(f"Dang tao vector bang OLLAMA cho cau hoi: '{user_question}'")
    
    # Tao vector tu cau hoi
    question_vector = get_query_embedding(user_question)
    
    if not question_vector:
        logger.error("Khong tao duoc vector tu Ollama.")
        return []
    
    # Truy van Neo4j
    cypher_query = """
    CALL db.index.vector.queryNodes('chunk_embeddings', $top_k, $question_vector)
    YIELD node, score
    RETURN node.id AS chunk_id, node.text AS text, score
    """
    
    parameters = {
        "top_k": top_k,
        "question_vector": question_vector
    }
    
    logger.info("Dang tim kiem ngu canh trong Neo4j...")
    results = neo4j_db.query(cypher_query, parameters)
    
    return results

if __name__ == "__main__":
    test_question = "Hiệp định Paris năm 1973 được ký kết vào ngày nào?"
    
    contexts = retrieve_context(test_question)
    
    print("\nKET QUA TIM KIEM:")
    if not contexts:
        print("Khong tim thay ket qua.")
    else:
        for idx, res in enumerate(contexts):
            # Nomic thường có score cosine rất cao, > 0.7 mới là tốt
            print(f"--- Top {idx + 1} | Do tuong dong (Score): {res['score']:.4f} ---")
            print(f"Chunk ID: {res['chunk_id']}")
            print(f"Noi dung: {res['text']}\n")