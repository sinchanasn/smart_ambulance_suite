# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

# pyrefly: ignore [missing-import]
from app.database.connection import get_db
from app.database.models import Vitals, Patient
from app.database.schemas import VitalsCreate, VitalsUpdate, VitalsResponse

router = APIRouter(prefix="/vitals", tags=["vitals"])


def _get_patient_or_404(patient_id: int, db: Session) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found",
        )
    return patient


def _get_latest_vitals(patient_id: int, db: Session) -> Vitals | None:
    return (
        db.query(Vitals)
        .filter(Vitals.patient_id == patient_id)
        .order_by(Vitals.timestamp.desc())
        .first()
    )


@router.post(
    "/",
    response_model=VitalsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record vital signs",
)
async def record_vitals(vitals: VitalsCreate, db: Session = Depends(get_db)):
    """Validate input, verify the patient exists, then store a new vitals reading."""
    _get_patient_or_404(vitals.patient_id, db)

    new_vitals = Vitals(**vitals.model_dump())
    db.add(new_vitals)
    db.commit()
    db.refresh(new_vitals)
    return new_vitals


@router.get(
    "/{patient_id}",
    response_model=VitalsResponse,
    summary="Get the latest vitals for a patient",
)
async def get_latest_vitals(patient_id: int, db: Session = Depends(get_db)):
    """Return the most recent vitals reading for the given patient."""
    _get_patient_or_404(patient_id, db)

    latest = _get_latest_vitals(patient_id, db)
    if latest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No vitals found for patient {patient_id}",
        )
    return latest


@router.put(
    "/{patient_id}",
    response_model=VitalsResponse,
    summary="Update the latest vitals for a patient",
)
async def update_latest_vitals(
    patient_id: int, vitals_update: VitalsUpdate, db: Session = Depends(get_db)
):
    """Update the most recent vitals record for the given patient."""
    _get_patient_or_404(patient_id, db)

    latest = _get_latest_vitals(patient_id, db)
    if latest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existing vitals to update for patient {patient_id}. Use POST to create one.",
        )

    for field, value in vitals_update.model_dump().items():
        setattr(latest, field, value)

    db.commit()
    db.refresh(latest)
    return latest