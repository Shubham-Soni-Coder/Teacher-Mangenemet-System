from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)


class BatchSubject(Base):
    __tablename__ = "batch_subjects"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    category = Column(String(20), nullable=False)
    stream = Column(String(20))

    is_compulsory = Column(Boolean, default=False)
    is_main = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("batch_id", "subject_id", name="uix_batch_subject"),
    )


class StudentSubject(Base):
    __tablename__ = "student_subjects"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uix_student_subject"),
    )
    student = relationship("Student", backref="student_subjects")
    subject = relationship("Subject")
