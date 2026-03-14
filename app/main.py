# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine, get_db
from app.routes import patients, visites, tournee, cabinets
from app.auth import authenticate_user
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Tournées Infirmières")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authenticate_user.router)
app.include_router(patients.router)
app.include_router(visites.router)
app.include_router(tournee.router)
app.include_router(cabinets.router)