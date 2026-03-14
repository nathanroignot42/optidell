# app/models/patient.py
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    adresse = Column(String(255), nullable=False)
    code_postal = Column(String(20))
    ville = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    telephone = Column(String(20))
    notes = Column(Text)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    cabinet = relationship("Cabinet", back_populates="patients")