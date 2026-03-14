from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time

from app.db import get_db
from app.models.visite import Visite
from app.models.tournee_visite import TourneeVisite
from app.routes.auth import get_current_user
from app.models.users import User
from pydantic import BaseModel

router = APIRouter(prefix="/visites", tags=["visites"])

class VisiteCreate(BaseModel):
    patient_id: int
    latitude: float
    longitude: float
    date: date
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    duree_minutes: Optional[int] = None
    type_soin: Optional[str] = None
    notes: Optional[str] = None

class VisiteOut(VisiteCreate):
    id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=VisiteOut)
def create_visite(
    visite: VisiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_visite = Visite(**visite.model_dump(), user_id=current_user.id)
    db.add(db_visite)
    db.commit()
    db.refresh(db_visite)
    return db_visite

@router.get("/", response_model=List[VisiteOut])
def read_visites(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Visite).filter(Visite.user_id == current_user.id).offset(skip).limit(limit).all()