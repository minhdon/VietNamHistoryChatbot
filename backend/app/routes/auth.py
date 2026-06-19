from backend.app.core.security import hash_password
from backend.app.services.auth import authenticate_user
from backend.app.schema.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.crud.user import create_user

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)
@router.post("/login")
def authenticate_user_route(user: User, db: Session = Depends(get_db)):
    return authenticate_user(db, user)
@router.post("/register")
def register_user(user: User, db: Session = Depends(get_db)):
    return create_user(db, user)
        
