# server/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    qty = Column(Integer, default=0)
    updated_at = Column(Integer, default=func.now())
