from pydantic import BaseModel
from typing import Optional, List


class BatchesCreate(BaseModel):
    batch_name: str
    stream: Optional[str] = None


class BatchesSubjectCreate(BaseModel):
    batch_id: int
    subject_id: int
    category: str
    stream: Optional[str] = None
    is_compulsory: Optional[bool] = False
    is_main: Optional[bool] = False


class BatchesStudentSelect(BaseModel):
    subjects_id: List[int]
