from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import các APIRouter từ thư mục routes
from app.routes import health, chatbot

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="History Graph-RAG Enterprise API",
    description="Hệ thống API phân mảnh (Modular Architecture) cho Chatbot Lịch Sử",
    version="2.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ĐĂNG KÝ CÁC ROUTES VÀO HỆ THỐNG APP CHÍNH
app.include_router(health.router)
app.include_router(chatbot.router)

@app.get("/")
def index():
    return {"message": "Welcome to History Graph-RAG Gateway. Go to /docs for API documentation."}

# Khởi chạy Uvicorn Server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)