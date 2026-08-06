"""
ECG Report Image Preprocessing Pipeline.

CONTEXT
-------
This module preprocesses **camera photographs of printed ECG reports**, not
raw ECG signal data.  Images are captured in real ambulance conditions and
may contain:

    - Variable lighting (flash, overhead fluorescent, daylight)
    - Camera tilt / slight rotation
    - Paper texture, creases, and print quality variation
    - Motion blur from a moving vehicle
    - JPEG compression artefacts

The preprocessing pipeline corrects for these conditions before passing the
image to the MobileNetV2 classifier.

PIPELINE (inference)
--------------------
    1.  Decode raw bytes → PIL Image (RGB)
    2.  Convert colour space (RGBA / greyscale → RGB)
    3.  Deskew / rotation correction (Hough-line based, via OpenCV)
    4.  CLAHE contrast enhancement (improves trace visibility)
    5.  Gaussian noise reduction (mild, preserves edges)
    6.  Brightness / gamma normalisation (CLAHE already handles contrast)
    7.  Resize to target dimensions (224 × 224)
    8.  MobileNetV2 pixel normalisation (rescale to [0, 1])
    9.  Add batch dimension → (1, 224, 224, 3)

OpenCV is used for the advanced steps (CLAHE, deskew); PIL handles I/O.
All functions are pure (no global state) and can be unit-tested without
a running model or GPU.
"""

from __future__ import annotations

import io
import logging
import math
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# MobileNetV2 input dimensions
TARGET_WIDTH: int = 224
TARGET_HEIGHT: int = 224
TARGET_CHANNELS: int = 3

# Deskew: maximum angle (degrees) to attempt correction
MAX_DESKEW_ANGLE_DEG: float = 15.0

# CLAHE parameters — conservative to avoid over-enhancement on paper texture
CLAHE_CLIP_LIMIT: float = 2.0
CLAHE_TILE_GRID_SIZE: Tuple[int, int] = (8, 8)

# Gaussian noise-reduction kernel size (must be odd)
DENOISE_KERNEL_SIZE: int = 3


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_pil_rgb(image_bytes: bytes) -> Image.Image:
    """Decode raw bytes and convert to an RGB PIL Image.

    Args:
        image_bytes: Raw image file bytes (PNG / JPG / JPEG).

    Returns:
        An RGB :class:`PIL.Image.Image`.

    Raises:
        ValueError: If the bytes cannot be decoded as a valid image.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()  # Force decode to catch truncated files
    except Exception as exc:
        logger.error("Failed to decode image bytes: %s", exc)
        raise ValueError(f"Cannot decode image: {exc}") from exc

    if img.mode != "RGB":
        logger.debug("Converting image mode %s → RGB", img.mode)
        img = img.convert("RGB")

    return img


def _try_import_cv2():
    """Lazily import OpenCV; return None if not installed."""
    try:
        # pyrefly: ignore [missing-import]
        import cv2  # noqa: PLC0415
        return cv2
    except ImportError:
        logger.warning(
            "OpenCV (cv2) is not installed. Advanced preprocessing steps "
            "(deskew, CLAHE) will be skipped. Install with: pip install opencv-python"
        )
        return None


def _deskew(img_bgr: np.ndarray, cv2) -> np.ndarray:
    """Attempt to correct camera-induced rotation using Hough line detection.

    The ECG print has strong horizontal grid lines.  By detecting dominant
    horizontal lines we can estimate the tilt angle and correct it.

    Strategy:
        1. Convert to greyscale.
        2. Detect edges with Canny.
        3. Find lines with Probabilistic Hough Transform.
        4. Compute median angle of near-horizontal lines.
        5. Rotate the image to correct the tilt (if within ±MAX_DESKEW_ANGLE_DEG).

    Args:
        img_bgr: BGR image array (OpenCV format).
        cv2:     The imported cv2 module.

    Returns:
        Deskewed BGR image array.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1=50, threshold2=150, apertureSize=3)

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=80,
        minLineLength=max(img_bgr.shape[1] // 5, 30),
        maxLineGap=20,
    )

    if lines is None or len(lines) == 0:
        logger.debug("Deskew: no lines detected, skipping.")
        return img_bgr

    angles: list[float] = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 != x1:
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            # Only consider near-horizontal lines (|angle| < 45°)
            if abs(angle) < 45.0:
                angles.append(angle)

    if not angles:
        logger.debug("Deskew: no usable horizontal lines, skipping.")
        return img_bgr

    median_angle = float(np.median(angles))

    if abs(median_angle) > MAX_DESKEW_ANGLE_DEG:
        logger.debug(
            "Deskew: detected angle %.2f° exceeds limit (±%.1f°), skipping.",
            median_angle,
            MAX_DESKEW_ANGLE_DEG,
        )
        return img_bgr

    if abs(median_angle) < 0.5:
        logger.debug("Deskew: angle %.2f° is negligible, skipping.", median_angle)
        return img_bgr

    h, w = img_bgr.shape[:2]
    cx, cy = w // 2, h // 2
    M = cv2.getRotationMatrix2D((cx, cy), median_angle, 1.0)
    rotated = cv2.warpAffine(img_bgr, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    logger.debug("Deskew: corrected %.2f° rotation.", median_angle)
    return rotated


def _apply_clahe(img_bgr: np.ndarray, cv2) -> np.ndarray:
    """Apply CLAHE contrast enhancement to improve ECG trace visibility.

    CLAHE (Contrast Limited Adaptive Histogram Equalisation) is applied to
    the luminance channel (LAB colour space) only, preserving hue and
    saturation so colour artefacts are not introduced.

    Args:
        img_bgr: BGR image array.
        cv2:     The imported cv2 module.

    Returns:
        Contrast-enhanced BGR image array.
    """
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID_SIZE)
    l_enhanced = clahe.apply(l_channel)

    lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
    result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    logger.debug("CLAHE contrast enhancement applied.")
    return result


def _denoise(img_bgr: np.ndarray, cv2) -> np.ndarray:
    """Apply a mild Gaussian blur to reduce camera noise and JPEG artefacts.

    The kernel is intentionally small (3×3) to reduce noise without blurring
    the ECG trace detail that the model needs for classification.

    Args:
        img_bgr: BGR image array.
        cv2:     The imported cv2 module.

    Returns:
        Denoised BGR image array.
    """
    result = cv2.GaussianBlur(
        img_bgr,
        (DENOISE_KERNEL_SIZE, DENOISE_KERNEL_SIZE),
        sigmaX=0,
    )
    logger.debug("Gaussian denoising applied (kernel=%d).", DENOISE_KERNEL_SIZE)
    return result


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def preprocess_ecg_image(
    image_bytes: bytes,
    target_size: Tuple[int, int] = (TARGET_HEIGHT, TARGET_WIDTH),
    apply_deskew: bool = True,
    apply_clahe: bool = True,
    apply_denoise: bool = True,
) -> np.ndarray:
    """Full preprocessing pipeline for a camera photograph of a printed ECG report.

    This function is the single entry-point used by the prediction engine.
    It applies a sequence of image corrections optimised for photos taken in
    ambulance conditions and returns a batch-ready float32 tensor.

    Args:
        image_bytes:  Raw bytes of the uploaded ECG image (PNG / JPG / JPEG).
        target_size:  ``(height, width)`` for the output tensor
                      (default ``(224, 224)`` for MobileNetV2).
        apply_deskew: If ``True``, attempt rotation correction via Hough lines.
                      Requires OpenCV.  Falls back gracefully if cv2 missing.
        apply_clahe:  If ``True``, apply CLAHE contrast enhancement.
                      Requires OpenCV.  Falls back gracefully if cv2 missing.
        apply_denoise: If ``True``, apply mild Gaussian noise reduction.
                       Requires OpenCV.  Falls back gracefully if cv2 missing.

    Returns:
        A ``float32`` NumPy array of shape ``(1, H, W, 3)`` in the range
        ``[0.0, 1.0]``, ready to pass directly to ``model.predict()``.

    Raises:
        ValueError: If ``image_bytes`` cannot be decoded or results in an
                    unexpected shape after processing.
    """
    target_h, target_w = target_size

    # ------------------------------------------------------------------
    # Step 1: Decode and convert to RGB PIL image
    # ------------------------------------------------------------------
    pil_img = _load_pil_rgb(image_bytes)
    logger.debug("Image loaded: size=%s mode=%s", pil_img.size, pil_img.mode)

    # ------------------------------------------------------------------
    # Steps 2–4: OpenCV-based corrections (optional, graceful fallback)
    # ------------------------------------------------------------------
    cv2 = _try_import_cv2()

    if cv2 is not None and (apply_deskew or apply_clahe or apply_denoise):
        # Convert PIL RGB → NumPy BGR for OpenCV
        img_bgr: np.ndarray = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        if apply_deskew:
            img_bgr = _deskew(img_bgr, cv2)

        if apply_clahe:
            img_bgr = _apply_clahe(img_bgr, cv2)

        if apply_denoise:
            img_bgr = _denoise(img_bgr, cv2)

        # Convert back BGR → RGB PIL image
        pil_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

    else:
        # Fallback: mild PIL-based noise reduction (no OpenCV dependency)
        if apply_denoise:
            pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=0.5))
            logger.debug("PIL GaussianBlur fallback applied (cv2 unavailable).")

    # ------------------------------------------------------------------
    # Step 5: Resize to model input dimensions
    # ------------------------------------------------------------------
    if pil_img.size != (target_w, target_h):
        pil_img = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        logger.debug("Image resized to %dx%d.", target_w, target_h)

    # ------------------------------------------------------------------
    # Step 6: Convert to float32 NumPy and normalise to [0, 1]
    # ------------------------------------------------------------------
    img_array: np.ndarray = np.array(pil_img, dtype=np.float32) / 255.0

    # ------------------------------------------------------------------
    # Step 7: Validate output shape
    # ------------------------------------------------------------------
    expected_shape = (target_h, target_w, TARGET_CHANNELS)
    if img_array.shape != expected_shape:
        raise ValueError(
            f"Unexpected array shape after preprocessing: {img_array.shape}. "
            f"Expected {expected_shape}."
        )

    # ------------------------------------------------------------------
    # Step 8: Add batch dimension → (1, H, W, 3)
    # ------------------------------------------------------------------
    return np.expand_dims(img_array, axis=0)
