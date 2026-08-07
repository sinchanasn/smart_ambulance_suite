"""
Unit tests for preprocessing/preprocess.py.

These tests are pure Python — no GPU, no TensorFlow, no model required.
They validate the shape, dtype, and value range of the preprocess function
using synthetic PIL images generated in memory.
"""

from __future__ import annotations

import io

import numpy as np
# pyrefly: ignore [missing-import]
import pytest
from PIL import Image

# Add ai/ to path when running from root
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.preprocess import (
    TARGET_CHANNELS,
    TARGET_HEIGHT,
    TARGET_WIDTH,
    preprocess_ecg_image,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_image_bytes(
    width: int = 300,
    height: int = 200,
    mode: str = "RGB",
    colour: tuple = (128, 64, 32),
    fmt: str = "PNG",
) -> bytes:
    """Create an in-memory image and return its raw bytes."""
    img = Image.new(mode, (width, height), colour)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Output shape tests
# ---------------------------------------------------------------------------

class TestOutputShape:
    """Validate that preprocess_ecg_image always returns (1, 224, 224, 3)."""

    def test_rgb_image_shape(self):
        data = _make_image_bytes(mode="RGB")
        result = preprocess_ecg_image(data)
        assert result.shape == (1, TARGET_HEIGHT, TARGET_WIDTH, TARGET_CHANNELS)

    def test_greyscale_image_shape(self):
        """Greyscale ECG scans should be converted to RGB before processing."""
        data = _make_image_bytes(mode="L", colour=128)
        result = preprocess_ecg_image(data)
        assert result.shape == (1, TARGET_HEIGHT, TARGET_WIDTH, TARGET_CHANNELS)

    def test_rgba_image_shape(self):
        """RGBA images (e.g. PNG with transparency) must be handled."""
        data = _make_image_bytes(mode="RGBA", colour=(200, 100, 50, 255))
        result = preprocess_ecg_image(data)
        assert result.shape == (1, TARGET_HEIGHT, TARGET_WIDTH, TARGET_CHANNELS)

    def test_large_image_is_resized(self):
        """High-resolution input must be downsampled to 224×224."""
        data = _make_image_bytes(width=1024, height=768, mode="RGB")
        result = preprocess_ecg_image(data)
        assert result.shape == (1, 224, 224, 3)

    def test_small_image_is_upscaled(self):
        """Very small input must be upsampled to 224×224."""
        data = _make_image_bytes(width=50, height=50, mode="RGB")
        result = preprocess_ecg_image(data)
        assert result.shape == (1, 224, 224, 3)

    def test_jpeg_image_shape(self):
        data = _make_image_bytes(mode="RGB", fmt="JPEG")
        result = preprocess_ecg_image(data)
        assert result.shape == (1, TARGET_HEIGHT, TARGET_WIDTH, TARGET_CHANNELS)


# ---------------------------------------------------------------------------
# Dtype tests
# ---------------------------------------------------------------------------

class TestOutputDtype:
    """Validate that the output is always float32."""

    def test_output_is_float32(self):
        data = _make_image_bytes()
        result = preprocess_ecg_image(data)
        assert result.dtype == np.float32


# ---------------------------------------------------------------------------
# Value range tests
# ---------------------------------------------------------------------------

class TestValueRange:
    """Pixel values must be normalised to [0.0, 1.0]."""

    def test_values_in_zero_one_range(self):
        data = _make_image_bytes(colour=(0, 128, 255))
        result = preprocess_ecg_image(data)
        assert float(result.min()) >= 0.0
        assert float(result.max()) <= 1.0

    def test_white_image_max_one(self):
        data = _make_image_bytes(colour=(255, 255, 255))
        result = preprocess_ecg_image(data)
        assert abs(float(result.max()) - 1.0) < 1e-5

    def test_black_image_min_zero(self):
        data = _make_image_bytes(colour=(0, 0, 0))
        result = preprocess_ecg_image(data)
        assert abs(float(result.min()) - 0.0) < 1e-5


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Invalid input must raise ValueError, not crash with an unhandled exception."""

    def test_invalid_bytes_raises_value_error(self):
        with pytest.raises(ValueError, match="Cannot decode image"):
            preprocess_ecg_image(b"this is not an image")

    def test_empty_bytes_raises_value_error(self):
        with pytest.raises(ValueError, match="Cannot decode image"):
            preprocess_ecg_image(b"")

    def test_random_bytes_raises_value_error(self):
        import os  # noqa: PLC0415
        junk = os.urandom(256)
        with pytest.raises(ValueError, match="Cannot decode image"):
            preprocess_ecg_image(junk)
