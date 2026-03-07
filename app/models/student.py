from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    roll_no = Column(Integer, nullable=True)
    name = Column(String, nullable=True)
    father_name = Column(String, nullable=True)
    mother_name = Column(String, nullable=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)

    batch = relationship("Batches", backref="students")
    User_ = relationship("User")
