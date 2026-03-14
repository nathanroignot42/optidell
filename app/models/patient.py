# app/models/patient.py
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())