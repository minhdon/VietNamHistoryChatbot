from backend.app.models.user import User
from backend.app.models.chat_session import ChatSession
from backend.app.schema.user import User as RequestUser
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.core.security import hash_password,check_password_conditions
def create_user(db: Session, request_user: RequestUser):
    # Kiểm tra xem username đã tồn tại chưa
    existing_user = db.query(User).filter(User.username == request_user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Kiểm tra điều kiện mật khẩu
    if not check_password_conditions(request_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet the required conditions"
        )

    # Tạo người dùng mới
    new_user = User(
        username=request_user.username,
        password=hash_password(request_user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return status.HTTP_201_CREATED, {"id": new_user.id, "username": new_user.username}