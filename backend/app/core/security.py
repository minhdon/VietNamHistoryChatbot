import bcrypt
import datetime
import jwt
from dotenv import load_dotenv
import os
load_dotenv()  # Load environment variables from .env file

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60*24
def  hash_password(password: str) -> str:
    pwd_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
def check_password_conditions(password: str) -> bool:
    # Kiểm tra độ dài tối thiểu
    if len(password) < 8:
        return False

    # Kiểm tra có ít nhất một chữ cái viết hoa
    if not any(char.isupper() for char in password):
        return False

    # Kiểm tra có ít nhất một chữ cái viết thường
    if not any(char.islower() for char in password):
        return False

    # Kiểm tra có ít nhất một chữ số
    if not any(char.isdigit() for char in password):
        return False

    # Kiểm tra có ít nhất một ký tự đặc biệt
    special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"
    if not any(char in special_characters for char in password):
        return False

    return True
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password[:72].encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False
def create_access_token(data: dict, expires_delta: datetime.timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    from backend.app.models.user import User
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user