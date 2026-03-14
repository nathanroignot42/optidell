# app/models/users.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nom = Column(String, nullable=True)
    prenom = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations (ex: tournées créées par cet utilisateur)
    tournees = relationship("Tournee", back_populates="infirmier")
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False)