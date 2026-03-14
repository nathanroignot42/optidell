# app/routes/tournee_visite.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models.tournee_visite import TourneeVisite
from app.models.tournee import Tournee
from app.routes.auth import get_current_user
from app.models.users import User
from pydantic import BaseModel

router = APIRouter(tags=["tournee_visite"], prefix="/tournee_visite")

# -------------------
# Pydantic Models
# -------------------
class TourneeVisiteOut(BaseModel):
    id: int
    tournee_id: int
    visite_id: int
    ordre: int

    class Config:
        orm_mode = True

# -------------------
# Routes
# -------------------
@router.get("/{tournee_id}/visites", response_model=List[TourneeVisiteOut])
def get_visites_tournee(
    tournee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Vérifie que la tournée appartient bien à l'utilisateur
    tournee = db.query(Tournee).filter(
        Tournee.id == tournee_id,
        Tournee.id_infirmier == current_user.id
    ).first()
    if not tournee:
        raise HTTPException(status_code=404, detail="Tournée introuvable ou non autorisée")

    visites = (
        db.query(TourneeVisite)
        .filter(TourneeVisite.tournee_id == tournee_id)
        .order_by(TourneeVisite.ordre)
        .all()
    )
    if not visites:
        raise HTTPException(status_code=404, detail="Aucune visite trouvée pour cette tournée")

    return visites