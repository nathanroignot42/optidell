# app/models/cabinet.py
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class Cabinet(Base):
    __tablename__ = "cabinets"

    id = Column(Integer, primary_key=True, index=True)
    adresse = Column(String(255), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    patients = relationship("Patient", back_populates="cabinet")