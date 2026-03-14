# app/models/tournee.py
from sqlalchemy import Column, Integer, Float, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Tournee(Base):
    __tablename__ = "tournee"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    id_infirmier = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    latitude_depart = Column(Float, nullable=True)
    longitude_depart = Column(Float, nullable=True)
    heure_depart = Column(Time, nullable=False)

    # relation inverse avec TourneeVisite
    visites = relationship("TourneeVisite", back_populates="tournee", cascade="all, delete-orphan")
    infirmier = relationship("User", back_populates="tournees")