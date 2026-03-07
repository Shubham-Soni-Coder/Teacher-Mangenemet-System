from pydantic import BaseModel, ConfigDict
from datetime import datetime, time


# ------------Base---------
class ClassBase(BaseModel):
    name: str
    subject: str

    teacher_id: int
    batch_id: int

    start_time: datetime
    end_time: datetime


class ClassScheduleBase(BaseModel):
    batch_id: int
    teacher_id: int
    subject_id: int
    day_of_week: int
    name: str
    start_time: time
    end_time: time


# --------Create-------
class ClassCreate(ClassBase):
    pass


class ClassScheduleCreate(ClassScheduleBase):
    pass


# --------Update--------
class ClassUpdate(ClassBase):
    subject: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


# ------Respone----------
class ClassOut(ClassBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
