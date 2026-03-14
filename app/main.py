# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.routes import patients, visites, tournee, cabinets

# Créer les tables si nécessaire
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Tournées Infirmières")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # remplacer par ton URL Flutter en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(patients.router)
app.include_router(visites.router)
app.include_router(tournee.router)
app.include_router(cabinets.router)