from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(
    prefix="/api",
    tags=["System Health & Models"]
)

OLLAMA_URL = "http://localhost:11434"

from app.services.retriever import retrieve_context 

@router.get("/health/services")
def check_services_health():
    """Kiểm tra xem kết nối tới Ollama và Neo4j có ổn định không"""
    status = {"ollama": "Down", "neo4j": "Down", "overall": "Unhealthy"}
    
    try:
        ollama_res = requests.get(f"{OLLAMA_URL}/", timeout=2)
        if ollama_res.status_code == 200:
            status["ollama"] = "Up"
    except:
        pass
        
    try:
        retrieve_context("", top_k=1, threshold=0.9)
        status["neo4j"] = "Up"
    except:
        pass
        
    if status["ollama"] == "Up" and status["neo4j"] == "Up":
        status["overall"] = "Healthy"
        
    return status

@router.get("/models")
def get_available_models():
    """Trả về danh sách các model LLM đang có trong Ollama local"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            model_names = [model.get("name") for model in models_data]
            return {"models": model_names, "current_default": "llama3.1"}
        else:
            raise HTTPException(status_code=502, detail="Lỗi từ Ollama.")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama Server chưa bật: {str(e)}")