from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Date,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime


class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Status: 'draft', 'published', 'closed'
    status = Column(String(50), default="published")

    batch = relationship("Batches")
    subject = relationship("Subject")
    teacher = relationship("Teacher")


class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homework.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    submission_date = Column(DateTime, default=datetime.utcnow)
    content = Column(Text, nullable=True)  # Text or File Path
    is_reviewed = Column(Boolean, default=False)
    grade = Column(String(10), nullable=True)
    feedback = Column(Text, nullable=True)

    homework = relationship("Homework", backref="submissions")
    student = relationship("Student")
