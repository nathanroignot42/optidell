# app/routes/cabinets.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.cabinet import Cabinet
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter(tags=["cabinets"], prefix="/cabinets")

class CabinetCreate(BaseModel):
    adresse: str
    latitude: float
    longitude: float

class CabinetOut(CabinetCreate):
    id: int

@router.post("/", response_model=CabinetOut)
def create_cabinet(cabinet: CabinetCreate, db: Session = Depends(get_db)):
    db_cabinet = Cabinet(**cabinet.model_dump())
    db.add(db_cabinet)
    db.commit()
    db.refresh(db_cabinet)
    return db_cabinet

@router.get("/", response_model=List[CabinetOut])
def read_cabinets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Cabinet).offset(skip).limit(limit).all()