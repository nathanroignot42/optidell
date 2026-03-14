#add/routes/tournee/
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.visite import Visite
from app.models.tournee import Tournee
from app.models.cabinet import Cabinet
from app.models.tournee_visite import TourneeVisite
from app.services.optimisation import optimiser_tournee_visites
from pydantic import BaseModel
from typing import List
from datetime import date, time

router = APIRouter(tags=["tournee"], prefix="/tournee")

# --------- MODELS PYDANTIC ---------
class TourneeCreate(BaseModel):
    date: date
    id_infirmier: int
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

# --------- CREATE TOURNEE ---------
@router.post("/create_tournee", response_model=TourneeOut)
def create_tournee(tournee: TourneeCreate, db: Session = Depends(get_db)):

    # 1️⃣ création de la tournée
    db_tournee = Tournee(
        date=tournee.date,
        id_infirmier=tournee.id_infirmier,
        latitude_depart=tournee.latitude_depart,
        longitude_depart=tournee.longitude_depart,
        heure_depart=tournee.heure_depart
    )
    db.add(db_tournee)
    db.commit()
    db.refresh(db_tournee)

    # 2️⃣ insertion des visites dans tournee_visite
    for ordre, visite_id in enumerate(tournee.visites):
        db_tv = TourneeVisite(
            tournee_id=db_tournee.id,
            visite_id=visite_id,
            ordre=ordre
        )
        db.add(db_tv)
    db.commit()

    return db_tournee


# --------- OPTIMISER UNE TOURNEE ---------
@router.post("/optimiser/{tournee_id}")
def optimiser_tournee(tournee_id: int, db: Session = Depends(get_db)):

    # 1️⃣ récupérer la tournée
    tournee = db.query(Tournee).filter(Tournee.id == tournee_id).first()
    if not tournee:
        raise HTTPException(status_code=404, detail="Tournée introuvable")

    # 2️⃣ récupérer les relations tournee_visite
    tv_list = (
        db.query(TourneeVisite)
        .filter(TourneeVisite.tournee_id == tournee_id)
        .order_by(TourneeVisite.ordre)
        .all()
    )
    if not tv_list:
        raise HTTPException(status_code=404, detail="Aucune visite dans cette tournée")

    # 3️⃣ récupérer les visites
    visites = []
    for tv in tv_list:
        visite = db.query(Visite).filter(Visite.id == tv.visite_id).first()
        if visite:
            visites.append(visite)

    # 4️⃣ transformer en payload pour optimisation
    visites_payload = []
    for v in visites:
        visites_payload.append(
            VisiteOpt(
            v.latitude,
            v.longitude,
            v.duree_minutes,
            v.heure_debut,
            v.heure_fin,
            v.patient_id
        )
    )

    # 5️⃣ cabinet de départ
    cabinet = db.query(Cabinet).first()

    # 6️⃣ optimisation
    try:
        ordre, route = optimiser_tournee_visites(visites_payload, cabinet)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur optimisation tournée: {str(e)}")
        print("Échec optimisation exacte, fallback simple")
        # fallback: ordre original
        ordre = list(range(len(visites_payload)))
        route = get_osrm_route([(cabinet.latitude, cabinet.longitude)] +
                               [(v["latitude"], v["longitude"]) for v in visites_payload] +
                               [(cabinet.latitude, cabinet.longitude)])

    # 7️⃣ mettre à jour uniquement l'ordre dans la table tournee_visite
    for i, visite_index in enumerate(ordre):
        tv_list[visite_index].ordre = i
    db.commit()

    return {
        "tournee_id": tournee_id,
        "order": ordre,
        "route": route
    }


# --------- LISTER LES VISITES D'UNE TOURNEE ---------
@router.get("/{tournee_id}/visites")
def get_visites_tournee(tournee_id: int, db: Session = Depends(get_db)):
    visites = (
        db.query(TourneeVisite)
        .filter(TourneeVisite.tournee_id == tournee_id)
        .order_by(TourneeVisite.ordre)
        .all()
    )
    return visites


# --------- LISTER LES TOURNEES ---------
@router.get("/read_tournee")
def read_tournees(db: Session = Depends(get_db)):
    return db.query(Tournee).all()