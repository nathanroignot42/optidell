# app/models/tournee_visite.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base
from app.models.tournee import Tournee
from app.models.visite import Visite

class TourneeVisite(Base):
    __tablename__ = "tournee_visite"

    id = Column(Integer, primary_key=True, index=True)
    tournee_id = Column(Integer, ForeignKey("tournee.id", ondelete="CASCADE"), nullable=False)
    visite_id = Column(Integer, ForeignKey("visite.id", ondelete="CASCADE"), nullable=False)
    ordre = Column(Integer, nullable=False)

    tournee = relationship(
        "Tournee",
        back_populates="visites",
        passive_deletes=True
    )
    visite = relationship(
        "Visite",
        back_populates="tournees",
        passive_deletes=True
    )