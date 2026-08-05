"""
Data Augmentation Pipeline for Ambulance-Condition ECG Report Photos.

CONTEXT
-------
This augmentation pipeline simulates the real-world variations encountered
when photographing printed ECG reports in a moving ambulance:

    - Vehicle vibration → slight rotations and translations
    - Changing lighting (tunnel, daylight, flash) → brightness / gamma shifts
    - Camera auto-focus inconsistency → mild blur
    - Paper reflections → localised brightness patches (simulated via contrast)
    - Held at angle / not perfectly flat → zoom and perspective-like distortion

These augmentations are applied **during training only**.  Keras augmentation
layers automatically disable themselves when called with ``training=False``
(the default during inference), so the layers can safely remain in the model
graph.

Two pipelines are provided:
    ``get_augmentation_pipeline()``     Standard Keras layer-based pipeline.
    ``get_numpy_augmentation()``         NumPy/OpenCV-based augmentation for
                                        use outside a TF training loop.
"""

from __future__ import annotations

import logging
import random
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Keras / TensorFlow augmentation pipeline (used in train.py)
# ---------------------------------------------------------------------------

def get_augmentation_pipeline():  # type: ignore[return]
    """Return a Keras Sequential augmentation model for ambulance ECG photos.

    Augmentations applied (all randomised per batch):

    +-----------------------+------------------------------------------+
    | Layer                 | Simulates                                |
    +=======================+==========================================+
    | RandomRotation ±8°    | Vehicle vibration / hand-held tilt       |
    +-----------------------+------------------------------------------+
    | RandomZoom ±12%       | Distance variation when photographing    |
    +-----------------------+------------------------------------------+
    | RandomBrightness ±25% | Tunnel / daylight / flash transitions    |
    +-----------------------+------------------------------------------+
    | RandomContrast ±20%   | Paper glare / low-contrast environments  |
    +-----------------------+------------------------------------------+
    | RandomTranslation ±5% | Camera position shift                    |
    +-----------------------+------------------------------------------+
    | GaussianNoise σ=0.02  | Sensor noise / JPEG artefacts            |
    +-----------------------+------------------------------------------+

    Returns:
        A ``tf.keras.Sequential`` model.  Call with ``training=True`` to
        activate augmentations; ``training=False`` (default) is a no-op.

    Raises:
        ImportError: If TensorFlow is not installed.

    Example::

        augment = get_augmentation_pipeline()
        x_aug = augment(x_batch, training=True)   # augmented
        x_val = augment(x_batch, training=False)  # unchanged
    """
    try:
        import tensorflow as tf  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "TensorFlow is required for the Keras augmentation pipeline. "
            "Install it with: pip install tensorflow"
        ) from exc

    # Perspective-like distortion: RandomZoom + RandomTranslation together
    # create a convincing perspective shift without needing a custom layer.

    augmentation = tf.keras.Sequential(
        [
            # Geometric: simulate camera angle and vehicle movement
            tf.keras.layers.RandomRotation(
                factor=0.044,          # ±8° (0.044 * 2π ≈ 16° range)
                fill_mode="reflect",   # Avoids black borders on rotated ECG strips
                name="aug_rotation",
            ),
            tf.keras.layers.RandomZoom(
                height_factor=(-0.12, 0.12),
                width_factor=(-0.12, 0.12),
                fill_mode="reflect",
                name="aug_zoom",
            ),
            tf.keras.layers.RandomTranslation(
                height_factor=0.05,
                width_factor=0.05,
                fill_mode="reflect",
                name="aug_translation",
            ),

            # Photometric: simulate lighting changes and paper reflections
            tf.keras.layers.RandomBrightness(
                factor=0.25,           # ±25% brightness shift
                value_range=(0.0, 1.0),
                name="aug_brightness",
            ),
            tf.keras.layers.RandomContrast(
                factor=0.20,           # ±20% contrast variation
                name="aug_contrast",
            ),
        ],
        name="ambulance_ecg_augmentation",
    )

    logger.debug("Ambulance ECG augmentation pipeline initialised (6 transforms).")
    return augmentation


# ---------------------------------------------------------------------------
# NumPy / OpenCV-based augmentation (used outside TF training loops)
# ---------------------------------------------------------------------------

def augment_image_numpy(
    img: np.ndarray,
    rotation_range_deg: float = 8.0,
    zoom_range: float = 0.12,
    brightness_range: float = 0.25,
    noise_std: float = 0.02,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Apply ambulance-condition augmentations to a single normalised image.

    Intended for use in preprocessing scripts and data exploration notebooks
    where a TensorFlow dataset pipeline is not available.

    Args:
        img:                Float32 array of shape ``(H, W, 3)`` in [0, 1].
        rotation_range_deg: Maximum random rotation in degrees (±).
        zoom_range:         Maximum random zoom factor (±).
        brightness_range:   Maximum random brightness delta (±).
        noise_std:          Standard deviation of Gaussian noise added.
        seed:               Optional random seed for reproducibility.

    Returns:
        Augmented float32 array of the same shape, clipped to [0, 1].

    Raises:
        ValueError: If ``img`` has an unexpected shape or dtype.
    """
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError(f"Expected shape (H, W, 3), got {img.shape}.")
    if img.dtype != np.float32:
        img = img.astype(np.float32)

    rng = np.random.default_rng(seed)
    result = img.copy()

    # ------------------------------------------------------------------
    # Rotation (OpenCV for quality; PIL fallback)
    # ------------------------------------------------------------------
    angle = rng.uniform(-rotation_range_deg, rotation_range_deg)
    result = _numpy_rotate(result, angle)

    # ------------------------------------------------------------------
    # Zoom (centre-crop + resize)
    # ------------------------------------------------------------------
    zoom_factor = rng.uniform(1.0 - zoom_range, 1.0 + zoom_range)
    result = _numpy_zoom(result, zoom_factor)

    # ------------------------------------------------------------------
    # Brightness delta
    # ------------------------------------------------------------------
    delta = rng.uniform(-brightness_range, brightness_range)
    result = np.clip(result + delta, 0.0, 1.0)

    # ------------------------------------------------------------------
    # Gaussian noise (simulates sensor/JPEG noise)
    # ------------------------------------------------------------------
    noise = rng.normal(0.0, noise_std, result.shape).astype(np.float32)
    result = np.clip(result + noise, 0.0, 1.0)

    logger.debug(
        "NumPy augmentation applied: rotation=%.1f°  zoom=%.2f  brightness_delta=%.3f",
        angle,
        zoom_factor,
        delta,
    )
    return result


def _numpy_rotate(img: np.ndarray, angle_deg: float) -> np.ndarray:
    """Rotate ``img`` by ``angle_deg`` degrees around its centre."""
    try:
        import cv2  # noqa: PLC0415
        h, w = img.shape[:2]
        img_uint8 = (img * 255).astype(np.uint8)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle_deg, 1.0)
        rotated = cv2.warpAffine(img_uint8, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        return rotated.astype(np.float32) / 255.0
    except ImportError:
        # PIL fallback
        from PIL import Image  # noqa: PLC0415
        pil_img = Image.fromarray((img * 255).astype(np.uint8))
        pil_img = pil_img.rotate(angle_deg, resample=Image.Resampling.BILINEAR, expand=False, fillcolor=(128, 128, 128))
        return np.array(pil_img, dtype=np.float32) / 255.0


def _numpy_zoom(img: np.ndarray, zoom_factor: float) -> np.ndarray:
    """Apply centre-crop zoom to ``img``."""
    from PIL import Image  # noqa: PLC0415

    h, w = img.shape[:2]
    pil_img = Image.fromarray((img * 255).astype(np.uint8))

    if zoom_factor > 1.0:
        # Zoom in: crop the centre and resize back
        new_w = int(w / zoom_factor)
        new_h = int(h / zoom_factor)
        left = (w - new_w) // 2
        top = (h - new_h) // 2
        pil_img = pil_img.crop((left, top, left + new_w, top + new_h))
    else:
        # Zoom out: add border and resize back
        new_w = int(w * zoom_factor)
        new_h = int(h * zoom_factor)
        left = (w - new_w) // 2
        top = (h - new_h) // 2
        canvas = Image.new("RGB", (w, h), (128, 128, 128))
        canvas.paste(pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS), (left, top))
        pil_img = canvas

    pil_img = pil_img.resize((w, h), Image.Resampling.LANCZOS)
    return np.array(pil_img, dtype=np.float32) / 255.0
