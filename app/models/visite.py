# app/models/visite.py
from sqlalchemy import Column, Integer, String, Float, Date, Time
from sqlalchemy.orm import relationship
from app.db import Base

class Visite(Base):
    __tablename__ = "visite"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    heure_debut = Column(Time, nullable=True)
    heure_fin = Column(Time, nullable=True)
    duree_minutes = Column(Integer, nullable=True)
    priorite = Column(Integer, nullable=True)
    type_soin = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    # relation inverse avec TourneeVisite
    tournees = relationship(
        "TourneeVisite",
        back_populates="visite",
        cascade="all, delete-orphan",
        passive_deletes=True
    )