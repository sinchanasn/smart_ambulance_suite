"""
FastAPI route for ECG image classification.

This module exposes a single endpoint:

    POST /predict
        Accepts a multipart ``file`` upload (PNG / JPG / JPEG).
        Returns a :class:`~api.schemas.PredictionResponse` JSON object.

The route validates the file type, delegates preprocessing and inference to
``model/predict.py``, and returns the structured result.

Note: This module does NOT implement:
    - Authentication / authorisation
    - Database access
    - WebSocket communication
    - Notification dispatching

Those responsibilities belong to the backend service.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from api.schemas import PredictionResponse
from model.loader import is_model_loaded
from model.predict import run_prediction
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["prediction"])

# ---------------------------------------------------------------------------
# Allowed file types (must match backend ECG upload restrictions)
# ---------------------------------------------------------------------------
_ALLOWED_CONTENT_TYPES: set[str] = {"image/png", "image/jpeg", "image/jpg"}
_ALLOWED_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg"}
_MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_ECG_SIZE_BYTES", str(10 * 1024 * 1024)))  # 10 MB default


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify an ECG image",
    description=(
        "Accepts a PNG, JPG, or JPEG ECG image upload and returns the AI-generated "
        "classification along with a confidence score.\n\n"
        "**Response fields:**\n"
        "- `prediction`: Human-readable label (Normal / Possible STEMI / Needs Cardiologist Review)\n"
        "- `confidence`: Model confidence in range [0.0, 1.0]\n"
        "- `class_id`: Integer class index (0, 1, or 2)"
    ),
)
async def predict_ecg(
    file: UploadFile = File(..., description="ECG image file (PNG / JPG / JPEG, max 10 MB)"),
) -> PredictionResponse:
    """Classify an uploaded ECG image using the MobileNetV2 model.

    Args:
        file: The multipart-uploaded ECG image file.

    Returns:
        A :class:`~api.schemas.PredictionResponse` with the predicted label,
        confidence score, and class ID.

    Raises:
        503 Service Unavailable: If the model has not been loaded yet.
        400 Bad Request: If the file type is invalid.
        413 Request Entity Too Large: If the file exceeds the size limit.
        500 Internal Server Error: If inference fails unexpectedly.
    """
    # ------------------------------------------------------------------
    # Guard: model must be loaded before accepting requests
    # ------------------------------------------------------------------
    if not is_model_loaded():
        logger.error("Prediction request received but model is not loaded.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI model is not yet available. Please try again shortly.",
        )

    # ------------------------------------------------------------------
    # Validate file type
    # ------------------------------------------------------------------
    filename: str = file.filename or ""
    ext: str = os.path.splitext(filename)[1].lower()

    if file.content_type not in _ALLOWED_CONTENT_TYPES or ext not in _ALLOWED_EXTENSIONS:
        logger.warning(
            "Rejected file '%s' with content_type='%s'", filename, file.content_type
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid file type '{file.content_type}'. "
                "Only PNG, JPG, and JPEG images are supported."
            ),
        )

    # ------------------------------------------------------------------
    # Read and size-check file
    # ------------------------------------------------------------------
    image_bytes: bytes = await file.read()

    if len(image_bytes) > _MAX_FILE_SIZE_BYTES:
        size_mb = len(image_bytes) / (1024 * 1024)
        logger.warning("Rejected oversized file: %.2f MB (max %d bytes)", size_mb, _MAX_FILE_SIZE_BYTES)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({size_mb:.1f} MB). Maximum allowed size is 10 MB.",
        )

    logger.info("Received ECG file '%s' (%.1f KB)", filename, len(image_bytes) / 1024)

    # ------------------------------------------------------------------
    # Run prediction
    # ------------------------------------------------------------------
    try:
        result: PredictionResponse = run_prediction(image_bytes)
    except ValueError as exc:
        logger.error("Image preprocessing failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not process image: {exc}",
        ) from exc
    except RuntimeError as exc:
        logger.error("Inference failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during ECG analysis. Please try again.",
        ) from exc

    logger.info(
        "Prediction returned: class_id=%d  label='%s'  confidence=%.4f",
        result.class_id,
        result.prediction,
        result.confidence,
    )

    return result
