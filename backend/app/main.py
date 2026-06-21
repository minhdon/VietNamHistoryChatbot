from fastapi import FastAPI
from backend.app.database.session import SessionLocal
from backend.app.models.user import User
from backend.app.core.security import hash_password
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import các APIRouter từ thư mục routes
from backend.app.routes import health
from backend.app.routes import chatbot
from backend.app.routes import ocr
from backend.app.routes import auth
from backend.app.routes import admin

def init_db():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Creating default admin user...")
            new_admin = User(
                username="admin",
                password=hash_password("123")
            )
            db.add(new_admin)
            db.commit()
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        db.close()

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="History Graph-RAG Enterprise API",
    description="Hệ thống API phân mảnh (Modular Architecture) cho Chatbot Lịch Sử",
    version="2.0.0",
    on_startup=[init_db]
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
app.include_router(admin.router)
@app.get("/")
def index():
    return {"message": "Welcome to History Graph-RAG Gateway. Go to /docs for API documentation."}

# Khởi chạy Uvicorn Server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)