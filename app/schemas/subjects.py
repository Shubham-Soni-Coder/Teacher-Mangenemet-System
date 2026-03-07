from pydantic import BaseModel
from typing import Optional


class SubjectCreate(BaseModel):
    name: str


class BatchSubjectCreate(BaseModel):
    batch_id: int
    subject_id: int
    category: str
    stream: Optional[str] = None
    is_compulsory: bool = False
    is_main: bool = False


class StudentSubjectCreate(BaseModel):
    student_id: int
    subject_id: int
