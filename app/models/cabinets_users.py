# app/models/cabinets_users.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base
from app.models.users import User
from app.models.cabinet import Cabinet  # Assure-toi d'avoir ce modèle

class CabinetUser(Base):
    __tablename__ = "cabinets_users"
    __table_args__ = (UniqueConstraint("user_id", "cabinet_id", name="uq_user_cabinet"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id", ondelete="CASCADE"), nullable=False)

    # Relations SQLAlchemy
    user = relationship("User", backref="cabinets_assoc")
    cabinet = relationship("Cabinet", backref="users_assoc")