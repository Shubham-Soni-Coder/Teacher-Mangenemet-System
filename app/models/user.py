from sqlalchemy import Column, Integer, String, Boolean, DateTime, UniqueConstraint
from app.database.base import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    gmail_id = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    role = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    _table_args__ = (UniqueConstraint("gmail_id", "role", name="uq_gmail_id_role"),)
