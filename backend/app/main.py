from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import các APIRouter từ thư mục routes
from backend.app.routes import health
from backend.app.routes import chatbot
from backend.app.routes import ocr
from backend.app.routes import auth

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="History Graph-RAG Enterprise API",
    description="Hệ thống API phân mảnh (Modular Architecture) cho Chatbot Lịch Sử",
    version="2.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ĐĂNG KÝ CÁC ROUTES VÀO HỆ THỐNG APP CHÍNH
app.include_router(health.router)
app.include_router(chatbot.router)
app.include_router(ocr.router)
app.include_router(auth.router)
@app.get("/")
def index():
    return {"message": "Welcome to History Graph-RAG Gateway. Go to /docs for API documentation."}

# Khởi chạy Uvicorn Server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)