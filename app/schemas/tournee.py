# app/schemas/tournee.py
from pydantic import BaseModel
from typing import List
from datetime import date

class TourneeCreate(BaseModel):
    date: date
    id_infirmier: int
    heure_depart: str
    latitude_depart: float
    longitude_depart: float
    visites: List[int]  # ⚡ Liste d'IDs de visites à inclure dans la tournée

class TourneeOut(TourneeCreate):
    id: int

    class Config:
        orm_mode = True