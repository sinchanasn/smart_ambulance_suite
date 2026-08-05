"""
Inference engine for ECG report image classification.

``run_prediction`` is the single public entry-point used by the API route.
It preprocesses a camera photograph of a printed ECG report, runs a forward
pass through the loaded MobileNetV2 model, and returns a structured
prediction result including a clinical action message.

IMPORTANT
---------
This module analyses photographs of printed ECG reports captured by a camera.
It does NOT process raw ECG signal data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from model.loader import get_model
from preprocessing.preprocess import preprocess_ecg_image
from utils.logger import get_logger

if TYPE_CHECKING:
    from api.schemas import PredictionResponse

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Load class metadata from labels.json (co-located with this file)
# ---------------------------------------------------------------------------
_LABELS_PATH = Path(__file__).parent / "labels.json"

with _LABELS_PATH.open("r", encoding="utf-8") as _f:
    _LABELS: dict[str, dict] = json.load(_f)


def run_prediction(image_bytes: bytes) -> "PredictionResponse":
    """Classify a camera photograph of a printed ECG report.

    Pipeline:
        1. Preprocess ``image_bytes`` through the full camera-photo pipeline
           (deskew, CLAHE, denoise, resize → 1×224×224×3 float32).
        2. Run ``model.predict()`` to obtain class probability scores.
        3. Select the class with the highest probability (argmax).
        4. Map the class index to label, display name, and message via
           ``labels.json``.
        5. Return a :class:`~api.schemas.PredictionResponse`.

    Args:
        image_bytes: Raw bytes of the uploaded ECG report image (PNG / JPG).

    Returns:
        A :class:`~api.schemas.PredictionResponse` containing:
            - ``prediction``  Snake-case label (e.g. ``"possible_stemi"``)
            - ``confidence``  Confidence score rounded to 4 dp
            - ``message``     Clinical action message
            - ``class_id``    Integer class index
            - ``display``     Human-friendly display name

    Raises:
        ValueError:  If the image cannot be decoded or pre-processed.
        RuntimeError: If the model is not loaded or inference fails.
    """
    # Deferred import to avoid circular import at module load time
    from api.schemas import PredictionResponse  # noqa: PLC0415

    logger.info(
        "Running ECG prediction on %.1f KB image …", len(image_bytes) / 1024
    )

    # ------------------------------------------------------------------
    # Step 1: Preprocess (camera-photo-aware pipeline)
    # ------------------------------------------------------------------
    input_tensor: np.ndarray = preprocess_ecg_image(image_bytes)

    # ------------------------------------------------------------------
    # Step 2: Inference
    # ------------------------------------------------------------------
    try:
        model = get_model()
        predictions: np.ndarray = model.predict(input_tensor, verbose=0)  # (1, N)
    except Exception as exc:
        logger.error("Model inference failed: %s", exc)
        raise RuntimeError(f"Inference error: {exc}") from exc

    # ------------------------------------------------------------------
    # Step 3: Select winning class
    # ------------------------------------------------------------------
    class_probabilities: np.ndarray = predictions[0]  # (N,)
    class_id: int = int(np.argmax(class_probabilities))
    confidence: float = round(float(class_probabilities[class_id]), 4)

    # ------------------------------------------------------------------
    # Step 4: Map to label metadata
    # ------------------------------------------------------------------
    class_meta: dict = _LABELS.get(str(class_id), {
        "label": "unknown",
        "display": "Unknown",
        "message": "Classification failed — unknown class index.",
    })

    label: str = class_meta.get("label", "unknown")
    display: str = class_meta.get("display", "Unknown")
    message: str = class_meta.get("message", "No clinical message available.")

    logger.info(
        "Prediction: class_id=%d  label='%s'  confidence=%.4f",
        class_id,
        label,
        confidence,
    )

    return PredictionResponse(
        prediction=label,
        confidence=confidence,
        message=message,
        class_id=class_id,
        display=display,
    )
