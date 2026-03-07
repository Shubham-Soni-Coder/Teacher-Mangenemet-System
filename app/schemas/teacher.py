from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TeacherCreate(BaseModel):
    user_id: int
    full_name: str
    department: str
    is_active: bool
    created_at: datetime


class TeacherBase(BaseModel):
    full_name: str
    department: str
