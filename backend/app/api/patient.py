from typing import List

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

# pyrefly: ignore [missing-import]
from app.database.connection import get_db
from app.database.models import Patient
from app.database.schemas import PatientCreate, PatientResponse, PatientCreateResponse

router = APIRouter(prefix="/patient", tags=["patients"])


@router.post(
    "/",
    response_model=PatientCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create patient record",
)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Register a new emergency patient record."""
    new_patient = Patient(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return PatientCreateResponse(
        message="Patient record created successfully",
        patient_id=new_patient.id,
    )


@router.get(
    "/",
    response_model=List[PatientResponse],
    summary="List all patient records",
)
async def list_patients(db: Session = Depends(get_db)):
    """Retrieve all patient emergency records."""
    return db.query(Patient).all()


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient by ID",
)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Retrieve specific patient details by ID."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found",
        )
    return patient