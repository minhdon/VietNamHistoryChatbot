import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app.database.session import engine, SessionLocal
from backend.app.schema.user import User
try:
    db = SessionLocal()
    user = db.query(User).filter(User.username == "test").first()
    print("Success:", user)
except Exception as e:
    print("Error:", e)
