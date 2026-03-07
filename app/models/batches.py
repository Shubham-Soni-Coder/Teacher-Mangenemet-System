from sqlalchemy import Column, Integer, String
from app.database.base import Base


class Batches(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String(50), nullable=False)
    stream = Column(String(10), nullable=True)
