# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine, get_db  # get_db doit retourner ta session SQLAlchemy
from app.routes import patients, visites, tournee, cabinets
from app.auth_service import authenticate_user  # notre service d'auth
from sqlalchemy.orm import Session

# 🔹 Créer les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

# 🔹 Instance FastAPI
app = FastAPI(title="API Tournées Infirmières")

# 🔹 Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À remplacer par ton URL Flutter en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Routes existantes
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(visites.router)
app.include_router(tournee.router)
app.include_router(cabinets.router)