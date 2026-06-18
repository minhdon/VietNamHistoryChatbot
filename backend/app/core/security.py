from passlib.context import CryptContext
import datetime
import jwt
from dotenv import load_dotenv

SECRET_KEY=load_dotenv().get("JWT_SECRET_KEY", "default_secret_key")
ALGORITHM="HS256"
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES=60*24
def  hash_password(password: str) -> str:
    return pwd_context.hash(password)
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
    return pwd_context.verify(plain_password, hashed_password)
def create_access_token(data: dict, expires_delta: datetime.timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt