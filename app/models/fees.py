from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    UniqueConstraint,
    Float,
)
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime


class FeesStructure(Base):
    __tablename__ = "fees_structure"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    academic_year = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    components = relationship(
        "FeesComponent", back_populates="fees_structure", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("batch_id", "academic_year", name="uq_batch_year"),
    )


class FeesComponent(Base):
    __tablename__ = "fees_components"
    id = Column(Integer, primary_key=True, index=True)
    fees_structure_id = Column(Integer, ForeignKey("fees_structure.id"), nullable=False)
    component_name = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)

    fees_structure = relationship("FeesStructure", back_populates="components")

    __table_args__ = (
        UniqueConstraint(
            "fees_structure_id", "component_name", name="uq_structure_component"
        ),
    )


class StudentFeesDue(Base):
    __tablename__ = "student_fes_due"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "month", "year", name="uq_student_month_year"),
    )


class FeesPayment(Base):
    __tablename__ = "fee_payments"
    id = Column(Integer, primary_key=True, index=True)

    due_id = Column(Integer, ForeignKey("student_fes_due.id"), nullable=False)

    amount_paid = Column(Float, nullable=False)
    payment_data = Column(DateTime, default=datetime.utcnow)

    discount_amount = Column(Float, default=0)
    fine_amount = Column(Float, default=0)
    method = Column(String, nullable=True)

    is_late = Column(Boolean, default=False)
