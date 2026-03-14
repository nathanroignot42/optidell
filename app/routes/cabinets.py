from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models.cabinet import Cabinet
from app.routes.auth import get_current_user
from app.models.users import User
from pydantic import BaseModel

router = APIRouter(tags=["cabinets"], prefix="/cabinets")

class CabinetCreate(BaseModel):
    adresse: str
    latitude: float
    longitude: float

class CabinetOut(CabinetCreate):
    id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=CabinetOut)
def create_cabinet(
    cabinet: CabinetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_cabinet = Cabinet(**cabinet.model_dump(), user_id=current_user.id)
    db.add(db_cabinet)
    db.commit()
    db.refresh(db_cabinet)
    return db_cabinet

@router.get("/", response_model=List[CabinetOut])
def read_cabinets(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Cabinet).filter(Cabinet.id == current_user.cabinet_id).offset(skip).limit(limit).all()