from pydantic import BaseModel
from datetime import date
from typing import Optional


# For creting a new Homework(Frontend)
class HomeworkCreate(BaseModel):
    title: str
    batch_id: int
    due_date: date
    description: Optional[str] = None


# For get the data from the backend
class HomeworkResponse(HomeworkCreate):
    id: int
    teacher_id: int
    subject_id: int
    status: str

    class Config:
        from_attributes = True
