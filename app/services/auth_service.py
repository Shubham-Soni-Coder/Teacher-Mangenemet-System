from sqlalchemy.orm import Session
from datetime import datetime
from app.models import User
from app.core.security import hash_password, verify_password
from app.core.exceptions import CustomException
from app.schemas import UserCreate


def login_user(db: Session, gmail: str, password: str, session: dict):
    user = db.query(User).filter(User.gmail_id == gmail).first()
    if not user:
        raise CustomException(status_code=400, detail="User not found")
    if not verify_password(password, user.hashed_password):
        raise CustomException(status_code=400, detail="Invalid password")
    return user
