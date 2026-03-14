from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date, time

from app.db import get_db
from app.models.tournee import Tournee
from app.models.tournee_visite import TourneeVisite
from app.models.visite import Visite
from app.models.cabinet import Cabinet
from app.services.optimisation import optimiser_tournee_visites
from app.routes.auth import get_current_user
from app.models.users import User
from pydantic import BaseModel

router = APIRouter(tags=["tournee"], prefix="/tournee")

class TourneeCreate(BaseModel):
    date: date
    latitude_depart: float
    longitude_depart: float
    heure_depart: str
    visites: List[int]

class TourneeOut(BaseModel):
    id: int
    date: date
    id_infirmier: int
    latitude_depart: float
    longitude_depart: float
    heure_depart: time

    class Config:
        orm_mode = True

class VisiteOpt:
    def __init__(self, latitude, longitude, duree_minutes, heure_debut, heure_fin, patient_id):
        self.latitude = latitude
        self.longitude = longitude
        self.duree_minutes = duree_minutes
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
        self.patient_id = patient_id

@router.post("/create_tournee", response_model=TourneeOut)
def create_tournee(
    tournee: TourneeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_tournee = Tournee(
        date=tournee.date,
        id_infirmier=current_user.id,
        latitude_depart=tournee.latitude_depart,
        longitude_depart=tournee.longitude_depart,
        heure_depart=tournee.heure_depart
    )
    db.add(db_tournee)
    db.commit()
    db.refresh(db_tournee)

    for ordre, visite_id in enumerate(tournee.visites):
        db_tv = TourneeVisite(
            tournee_id=db_tournee.id,
            visite_id=visite_id,
            ordre=ordre
        )
        db.add(db_tv)
    db.commit()
    return db_tournee

@router.get("/read_tournee")
def read_tournees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Tournee).filter(Tournee.id_infirmier == current_user.id).all()