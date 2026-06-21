from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.core.security import get_current_user
from backend.app.utils.db_neo4j import neo4j_db
from backend.app.services.retriever import model as embedding_model
from backend.app.services.ingestion import split_into_chunks, extract_graph_elements_ollama, insert_chunk_to_neo4j
from pydantic import BaseModel
import uuid

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

# Admin middleware simulation
def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.username != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have enough privileges"
        )
    return current_user

# --- User Management ---

@router.get("/users")
def get_all_users(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "created_at": u.created_at} for u in users]

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username == 'admin':
        raise HTTPException(status_code=400, detail="Cannot delete admin user")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# --- Neo4j Document Management ---

class ChunkCreate(BaseModel):
    text: str

class ChunkUpdate(BaseModel):
    text: str

@router.get("/neo4j/chunks")
def get_neo4j_chunks(current_admin: User = Depends(get_current_admin)):
    query = """
    MATCH (c:Chunk)
    RETURN c.id AS id, c.text AS text
    ORDER BY toInteger(c.id) DESC
    LIMIT 100
    """
    results = neo4j_db.query(query)
    return results

@router.post("/neo4j/chunks")
def create_neo4j_chunk(chunk: ChunkCreate, current_admin: User = Depends(get_current_admin)):
    # Find max numeric ID (supporting both integer and string IDs in DB)
    query_max_id = """
    MATCH (c:Chunk)
    WHERE toString(c.id) =~ '^[0-9]+$'
    RETURN max(toInteger(c.id)) AS max_id
    """
    res_id = neo4j_db.query(query_max_id)
    current_max_id = res_id[0].get("max_id") if (res_id and res_id[0].get("max_id") is not None) else 0

    # 1. Split text into chunks
    chunks_text = split_into_chunks(chunk.text, max_chars=500)
    
    results_out = []
    
    for idx, text_segment in enumerate(chunks_text):
        new_id_int = current_max_id + 1 + idx
        chunk_id = str(new_id_int)
        
        # Định dạng lại text theo cấu trúc Hỏi - Đáp để đồng bộ với 12,000 chunks cũ
        # Giúp model vietnamese-sbert nhận diện vector chính xác hơn
        formatted_text = f"Hỏi: Nội dung của tài liệu này là gì?\nĐáp: {text_segment}"
        
        # 2. Calculate embedding
        try:
            embedding = embedding_model.encode(formatted_text).tolist()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {e}")
            
        # 3. Extract nodes and edges with Ollama
        extracted_data = extract_graph_elements_ollama(formatted_text)
        
        # 4. Insert into Neo4j
        try:
            insert_chunk_to_neo4j(chunk_id, formatted_text, embedding, extracted_data)
            results_out.append({"id": chunk_id, "text": formatted_text})
        except Exception as e:
            print(f"Error inserting chunk {chunk_id}: {e}")
            
    if not results_out:
        raise HTTPException(status_code=500, detail="Failed to create document in Neo4j")
        
    return results_out[0] # Return the first chunk for UI representation

@router.put("/neo4j/chunks/{chunk_id}")
def update_neo4j_chunk(chunk_id: str, chunk: ChunkUpdate, current_admin: User = Depends(get_current_admin)):
    # Calculate new embedding
    try:
        embedding = embedding_model.encode(chunk.text).tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {e}")

    query = """
    MATCH (c:Chunk {id: $chunk_id})
    SET c.text = $text, c.embedding = $embedding
    RETURN c.id AS id, c.text AS text
    """
    results = neo4j_db.query(query, {"chunk_id": chunk_id, "text": chunk.text, "embedding": embedding})
    if not results:
        raise HTTPException(status_code=404, detail="Document not found")
    return results[0]
