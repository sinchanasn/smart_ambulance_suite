import os
import uuid

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

# pyrefly: ignore [missing-import]
from app.database.connection import get_db
from app.database.models import ECG, Patient
from app.database.schemas import ECGResponse, ECGUploadResponse

# AI Integration: import the isolated AI service client.
# This is the ONLY import needed to enable AI predictions on ECG uploads.
# The ai_client module handles all HTTP communication with the AI microservice.
from app.services.ai_client import call_ai_predict

router = APIRouter(prefix="/ecg", tags=["ecg"])

UPLOAD_DIR = "uploads/ecg"
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _get_patient_or_404(patient_id: int, db: Session) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found",
        )
    return patient


@router.post(
    "/",
    response_model=ECGUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an ECG image for a patient",
)
async def upload_ecg(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Verify the patient exists, validate the file type, save the image, and store its path."""
    _get_patient_or_404(patient_id, db)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if file.content_type not in ALLOWED_CONTENT_TYPES or ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PNG, JPG, and JPEG images are allowed.",
        )

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    new_ecg = ECG(
        patient_id=patient_id,
        image_path=file_path,
        original_filename=file.filename,
        status="UPLOADED",
    )
    db.add(new_ecg)
    db.commit()
    db.refresh(new_ecg)

    # -----------------------------------------------------------------------
    # AI INTEGRATION POINT
    # After persisting the ECG record, call the AI microservice to classify
    # the uploaded image.  If the AI service is unavailable or returns an
    # error, prediction will be None and the upload still succeeds.
    # The prediction result is written back to the same ECG record.
    # -----------------------------------------------------------------------
    prediction_result = await call_ai_predict(contents, file.filename or "ecg.png")
    if prediction_result:
        new_ecg.prediction = prediction_result.get("prediction")
        new_ecg.confidence = prediction_result.get("confidence")
        new_ecg.status = "ANALYSED"
        db.commit()
        db.refresh(new_ecg)
    # -----------------------------------------------------------------------
    # END AI INTEGRATION POINT
    # -----------------------------------------------------------------------

    return ECGUploadResponse(
        message="ECG scan uploaded successfully",
        patient_id=patient_id,
        ecg_id=new_ecg.id,
        image_path=new_ecg.image_path,
        prediction=new_ecg.prediction,
        confidence=new_ecg.confidence,
        status=new_ecg.status,
    )


@router.get(
    "/{patient_id}",
    response_model=ECGResponse,
    summary="Get the most recent ECG record for a patient",
)
async def get_latest_ecg(patient_id: int, db: Session = Depends(get_db)):
    """Return the most recent ECG record for the given patient."""
    _get_patient_or_404(patient_id, db)

    latest = (
        db.query(ECG)
        .filter(ECG.patient_id == patient_id)
        .order_by(ECG.uploaded_at.desc())
        .first()
    )
    if latest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ECG records found for patient {patient_id}",
        )
    return latest