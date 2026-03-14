from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app.models.patient import Patient
from app.routes.auth import get_current_user
from app.models.users import User
from pydantic import BaseModel

router = APIRouter(tags=["patients"], prefix="/patients")

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

    model_config = {"from_attributes": True}

class PatientOut(PatientBase):
    id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=PatientOut)
def create_patient(
    patient: PatientBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_patient = Patient(**patient.model_dump(), user_id=current_user.id)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/", response_model=List[PatientOut])
def read_patients(skip: int = 0, limit: int = 100, 
                  db: Session = Depends(get_db), 
                  current_user: User = Depends(get_current_user)):
    return db.query(Patient)\
             .filter(Patient.cabinet_id == current_user.cabinet_id)\
             .offset(skip)\
             .limit(limit)\
             .all()