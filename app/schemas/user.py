from pydantic import BaseModel
from datetime import datetime


class Usermodel(BaseModel):
    id: int
    gmail_id: str
    hashed_password: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    gmail_id: str
    hashed_password: str
    role: str
    is_active: bool
