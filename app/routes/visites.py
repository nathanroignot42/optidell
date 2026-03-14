# app/routes/visites.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.visite import Visite
from app.models.tournee_visite import TourneeVisite
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

router = APIRouter(
    prefix="/visites",
    tags=["visites"]
)

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

class VisiteUpdate(BaseModel):
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    duree_minutes: Optional[int] = None
    type_soin: Optional[str] = None
    notes: Optional[str] = None
    
class VisiteOut(VisiteCreate):
    id: int

    class Config:
        from_attributes = True

@router.post("/", response_model=VisiteOut)
def create_visite(visite: VisiteCreate, db: Session = Depends(get_db)):
    db_visite = Visite(**visite.model_dump())
    db.add(db_visite)
    db.commit()
    db.refresh(db_visite)
    return db_visite

@router.get("/", response_model=List[VisiteOut])
def read_visites(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Visite).offset(skip).limit(limit).all()
    
@router.put("/{visite_id}", response_model=VisiteOut)
def update_visite(visite_id: int, visite: VisiteUpdate, db: Session = Depends(get_db)):

    db_visite = db.query(Visite).filter(Visite.id == visite_id).first()

    if not db_visite:
        raise HTTPException(status_code=404, detail="Visite not found")

    for key, value in visite.model_dump(exclude_unset=True).items():
        setattr(db_visite, key, value)

    db.commit()
    db.refresh(db_visite)

    return db_visite
    
@router.delete("/{visite_id}", response_model=VisiteOut)
def delete_visite(visite_id: int, db: Session = Depends(get_db)):
    db_visite = db.query(Visite).filter(Visite.id == visite_id).first()
    if not db_visite:
        raise HTTPException(status_code=404, detail="Visite not found")
    
    db.query(TourneeVisite).filter(
        TourneeVisite.visite_id == visite_id
    ).delete()
    
    db.delete(db_visite)
    db.flush()
    db.commit()

    return db_visite
    
@router.get("/{visite_id}/tournee")
def get_tournee_visite(visite_id: int, db: Session = Depends(get_db)):

    tv = db.query(TourneeVisite).filter(
        TourneeVisite.visite_id == visite_id
    ).first()

    if tv:
        return {"used": True, "tournee_id": tv.tournee_id}

    return {"used": False}