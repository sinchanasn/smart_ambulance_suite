"""
Singleton model loader for the Smart Ambulance AI Service.

The Keras model is loaded **once** at application startup and cached in
memory.  Subsequent calls to ``get_model()`` return the cached instance
without any I/O overhead.

Environment variables:
    MODEL_PATH  Path to the saved Keras model file
                (default: ``model/saved_models/ecg_model.keras``).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level cache — populated on first call to load_model()
# ---------------------------------------------------------------------------
_model = None  # type: ignore[assignment]


def _get_model_path() -> Path:
    """Resolve the model path from environment or use the default."""
    raw_path = os.getenv(
        "MODEL_PATH",
        str(Path(__file__).parent / "saved_models" / "ecg_model.keras"),
    )
    return Path(raw_path)


def load_model() -> None:
    """Load the Keras model from disk into the module-level cache.

    This function is intended to be called **once** during application
    startup (e.g. in a FastAPI ``lifespan`` handler).  It is idempotent —
    calling it more than once has no effect after the first successful load.

    Raises:
        FileNotFoundError: If the model file does not exist at the
            configured ``MODEL_PATH``.
        RuntimeError: If TensorFlow fails to load the model.
    """
    global _model  # noqa: PLW0603

    if _model is not None:
        logger.debug("Model already loaded — skipping reload.")
        return

    model_path = _get_model_path()

    if not model_path.exists():
        raise FileNotFoundError(
            f"ECG model file not found at '{model_path}'. "
            "Run `python model/train.py` to train and save the model, "
            "or place a pre-trained model at the configured MODEL_PATH."
        )

    try:
        import tensorflow as tf  # noqa: PLC0415
        logger.info("Loading ECG model from '%s' …", model_path)
        _model = tf.keras.models.load_model(str(model_path))
        logger.info("ECG model loaded successfully.")
    except Exception as exc:
        logger.error("Failed to load ECG model: %s", exc)
        raise RuntimeError(f"Model load failed: {exc}") from exc


def get_model():  # type: ignore[return]
    """Return the cached Keras model instance.

    Returns:
        The loaded ``tf.keras.Model``.

    Raises:
        RuntimeError: If ``load_model()`` has not been called yet.
    """
    if _model is None:
        raise RuntimeError(
            "Model is not loaded. Ensure ``load_model()`` is called at "
            "application startup before handling prediction requests."
        )
    return _model


def is_model_loaded() -> bool:
    """Return ``True`` if the model has been successfully loaded."""
    return _model is not None
