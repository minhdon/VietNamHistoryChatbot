from backend.app.services.auth import authenticate_user
from backend.app.schema.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db

def authenticate_user_route(user: User, db: Session = Depends(get_db)):
    return authenticate_user(db, user)