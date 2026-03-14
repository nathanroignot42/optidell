# app/routes/patients.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.patient import Patient
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(tags=["patients"], prefix="/patients")

# Pydantic v2: utiliser from_attributes
class PatientBase(BaseModel):
    nom: str
    prenom: Optional[str] = None
    adresse: str
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    telephone: Optional[str] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}  # v2

class PatientOut(PatientBase):
    id: int

# CRUD
@router.post("/", response_model=PatientOut)
def create_patient(patient: PatientBase, db: Session = Depends(get_db)):
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/", response_model=List[PatientOut])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Patient).offset(skip).limit(limit).all()