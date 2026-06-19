from backend.app.models.user import User
from sqlalchemy.orm import Session
from backend.app.core.security import verify_password,hash_password,create_access_token
from datetime import timedelta
from backend.app.schema.user import User as RequestUser
from fastapi import HTTPException, status

def authenticate_user(db: Session, request_user: RequestUser):
    user = db.query(User).filter(User.username == request_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(request_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60*24)  # Token expires in 24 hours
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username}
    }
