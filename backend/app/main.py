from fastapi import FastAPI

from app.database.connection import Base, engine
from app.database import models

from app.api import patient, vitals, ecg


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Smart Ambulance Backend",
    version="1.0.0"
)

app.include_router(patient.router)
app.include_router(vitals.router)
app.include_router(ecg.router)


@app.get("/")
def root():
    return {"message": "Smart Ambulance Backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
    