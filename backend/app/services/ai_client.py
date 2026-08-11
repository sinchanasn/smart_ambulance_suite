"""
AI Service HTTP Client for the Smart Ambulance Backend.

This module provides an isolated, async HTTP client that the backend uses to
call the AI microservice's ``POST /predict`` endpoint after an ECG image is
uploaded.

Design principles
-----------------
* **Isolation**: This file is the *only* place in the backend that knows
  about the AI service URL or protocol.  All other backend code remains
  unchanged.
* **Graceful degradation**: On any network or AI service error, the function
  returns ``None`` so the caller can store the ECG record without a
  prediction rather than failing the entire upload request.
* **No side effects**: This module does not access the database, send
  notifications, or modify application state.

Configuration (via environment variables or backend .env)
---------------------------------------------------------
    AI_SERVICE_URL  Base URL of the AI microservice
                    (default: ``http://localhost:8001``).
    AI_TIMEOUT_SEC  HTTP request timeout in seconds (default: ``30``).

Integration point
-----------------
Import and call ``call_ai_predict`` inside the ECG upload route
(``backend/app/api/ecg.py``) immediately after the ECG record is saved to
the database:

    from app.services.ai_client import call_ai_predict

    # --- AI INTEGRATION POINT ---
    prediction_result = await call_ai_predict(image_bytes, file.filename)
    if prediction_result:
        new_ecg.prediction = prediction_result["prediction"]
        new_ecg.confidence = prediction_result["confidence"]
        db.commit()
    # --- END AI INTEGRATION ---
"""

from __future__ import annotations

import logging
import os
from typing import Optional

# pyrefly: ignore [missing-import]
import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://localhost:8001").rstrip("/")
_AI_TIMEOUT_SEC: float = float(os.getenv("AI_TIMEOUT_SEC", "120"))

# Full URL for the prediction endpoint
_PREDICT_ENDPOINT: str = f"{_AI_SERVICE_URL}/predict"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def call_ai_predict(
    image_bytes: bytes,
    filename: str,
) -> Optional[dict]:
    """Send an ECG image to the AI service and return the prediction result.

    This is the **sole integration point** between the backend and the AI
    microservice.  The backend ECG upload route should call this function
    after saving the ECG record to the database.

    Args:
        image_bytes: Raw bytes of the uploaded ECG image (already read by the
                     backend route — no double-read).
        filename:    Original filename of the upload, used as the multipart
                     field name so the AI service can infer the MIME type.

    Returns:
        A dictionary with the AI prediction on success::

            {
                "prediction": "Possible STEMI",
                "confidence": 0.94,
                "class_id": 1
            }

        Returns ``None`` if the AI service is unreachable, returns a non-200
        status, or times out.  The caller should handle ``None`` gracefully
        (store the ECG without a prediction).

    Note:
        This function is intentionally non-raising.  All exceptions are
        caught and logged so the ECG upload never fails because of an AI
        service outage.
    """
    logger.info(
        "Calling AI predict endpoint at '%s' for file '%s' (%.1f KB) …",
        _PREDICT_ENDPOINT,
        filename,
        len(image_bytes) / 1024,
    )

    try:
        async with httpx.AsyncClient(timeout=_AI_TIMEOUT_SEC) as client:
            response = await client.post(
                _PREDICT_ENDPOINT,
                files={"file": (filename, image_bytes, _guess_content_type(filename))},
            )
            response.raise_for_status()

        payload: dict = response.json()

        logger.info(
            "AI prediction received: prediction='%s'  confidence=%.4f  class_id=%d",
            payload.get("prediction"),
            payload.get("confidence", 0.0),
            payload.get("class_id", -1),
        )
        return payload

    except httpx.ConnectError:
        logger.warning(
            "AI service is unreachable at '%s'. "
            "ECG will be stored without a prediction.",
            _AI_SERVICE_URL,
        )
    except httpx.TimeoutException:
        logger.warning(
            "AI service request timed out after %.1f seconds. "
            "ECG will be stored without a prediction.",
            _AI_TIMEOUT_SEC,
        )
    except httpx.HTTPStatusError as exc:
        logger.error(
            "AI service returned HTTP %d for '%s': %s",
            exc.response.status_code,
            _PREDICT_ENDPOINT,
            exc.response.text[:200],
        )
    except Exception as exc:  # noqa: BLE001 — intentional catch-all for resilience
        logger.error(
            "Unexpected error calling AI service: %s — %s",
            type(exc).__name__,
            exc,
        )

    return None


async def check_ai_health() -> bool:
    """Ping the AI service health endpoint.

    Returns:
        ``True`` if the AI service responds with HTTP 200, ``False`` otherwise.
        Useful for backend startup checks or monitoring endpoints.
    """
    health_url = f"{_AI_SERVICE_URL}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(health_url)
            return response.status_code == 200
    except Exception as exc:  # noqa: BLE001
        logger.debug("AI health check failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _guess_content_type(filename: str) -> str:
    """Return a MIME type string based on the file extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
    }.get(ext, "application/octet-stream")
