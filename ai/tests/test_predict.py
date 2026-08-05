"""
Unit tests for model/predict.py.

The Keras model is fully mocked so these tests run without TensorFlow,
a GPU, or a saved model file.  Only the prediction logic is exercised.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
# pyrefly: ignore [missing-import]
import pytest
from PIL import Image

# Ensure ai/ root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_image_bytes(
    width: int = 224,
    height: int = 224,
    mode: str = "RGB",
    fmt: str = "PNG",
) -> bytes:
    """Return in-memory image bytes for test input."""
    img = Image.new(mode, (width, height), (120, 80, 40))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def _make_mock_model(class_id: int = 0, num_classes: int = 3) -> MagicMock:
    """Return a mock Keras model that predicts ``class_id`` with high confidence."""
    probs = np.zeros((1, num_classes), dtype=np.float32)
    probs[0, class_id] = 0.94
    probs[0, (class_id + 1) % num_classes] = 0.04
    probs[0, (class_id + 2) % num_classes] = 0.02

    mock_model = MagicMock()
    mock_model.predict.return_value = probs
    return mock_model


# ---------------------------------------------------------------------------
# Schema / output structure tests
# ---------------------------------------------------------------------------

class TestPredictionSchema:
    """Verify that run_prediction returns a correctly structured PredictionResponse."""

    @patch("model.predict.get_model")
    def test_returns_prediction_response(self, mock_get_model: MagicMock) -> None:
        from api.schemas import PredictionResponse  # noqa: PLC0415
        from model.predict import run_prediction  # noqa: PLC0415

        mock_get_model.return_value = _make_mock_model(class_id=0)
        result = run_prediction(_make_image_bytes())

        assert isinstance(result, PredictionResponse)

    @patch("model.predict.get_model")
    def test_has_all_required_fields(self, mock_get_model: MagicMock) -> None:
        from model.predict import run_prediction  # noqa: PLC0415

        mock_get_model.return_value = _make_mock_model(class_id=1)
        result = run_prediction(_make_image_bytes())

        assert hasattr(result, "prediction")
        assert hasattr(result, "confidence")
        assert hasattr(result, "class_id")

    @patch("model.predict.get_model")
    def test_prediction_is_string(self, mock_get_model: MagicMock) -> None:
        from model.predict import run_prediction  # noqa: PLC0415

        mock_get_model.return_value = _make_mock_model(class_id=0)
        result = run_prediction(_make_image_bytes())
        assert isinstance(result.prediction, str)
        assert len(result.prediction) > 0

    @patch("model.predict.get_model")
    def test_class_id_is_int(self, mock_get_model: MagicMock) -> None:
        from model.predict import run_prediction  # noqa: PLC0415

        mock_get_model.return_value = _make_mock_model(class_id=2)
        result = run_prediction(_make_image_bytes())
        assert isinstance(result.class_id, int)


# ---------------------------------------------------------------------------
# Confidence range tests
# ---------------------------------------------------------------------------

class TestConfidenceRange:
    """Confidence must always be in [0.0, 1.0]."""

    @pytest.mark.parametrize("class_id", [0, 1, 2])
    @patch("model.predict.get_model")
    def test_confidence_in_range(self, mock_get_model: MagicMock, class_id: int) -> None:
        from model.predict import run_prediction  # noqa: PLC0415

        mock_get_model.return_value = _make_mock_model(class_id=class_id)
        result = run_prediction(_make_image_bytes())

        assert 0.0 <= result.confidence <= 1.0

    @patch("model.predict.get_model")
    def test_confidence_matches_mock(self, mock_get_model: MagicMock) -> None:
        from model.predict import run_prediction  # noqa: PLC0415

        mock_get_model.return_value = _make_mock_model(class_id=1)
        result = run_prediction(_make_image_bytes())
        # Class 1 has 0.94 confidence in the mock
        assert abs(result.confidence - 0.94) < 1e-3


# ---------------------------------------------------------------------------
# Label mapping tests
# ---------------------------------------------------------------------------

class TestLabelMapping:
    """Class IDs must map to known label strings from labels.json."""

    EXPECTED_LABELS = {
        0: "Normal",
        1: "Possible STEMI",
        2: "Needs Cardiologist Review",
    }

    @pytest.mark.parametrize("class_id,expected_label", EXPECTED_LABELS.items())
    @patch("model.predict.get_model")
    def test_label_for_class(
        self, mock_get_model: MagicMock, class_id: int, expected_label: str
    ) -> None:
        from model.predict import run_prediction  # noqa: PLC0415

        mock_get_model.return_value = _make_mock_model(class_id=class_id)
        result = run_prediction(_make_image_bytes())

        assert result.class_id == class_id
        assert result.prediction == expected_label


# ---------------------------------------------------------------------------
# Error propagation tests
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Verify that model and preprocessing errors propagate cleanly."""

    @patch("model.predict.get_model")
    def test_invalid_image_raises_value_error(self, mock_get_model: MagicMock) -> None:
        from model.predict import run_prediction  # noqa: PLC0415

        mock_get_model.return_value = _make_mock_model()
        with pytest.raises(ValueError):
            run_prediction(b"not an image")

    @patch("model.predict.get_model")
    def test_model_exception_raises_runtime_error(self, mock_get_model: MagicMock) -> None:
        from model.predict import run_prediction  # noqa: PLC0415

        mock_model = MagicMock()
        mock_model.predict.side_effect = RuntimeError("CUDA OOM")
        mock_get_model.return_value = mock_model

        with pytest.raises(RuntimeError, match="Inference error"):
            run_prediction(_make_image_bytes())
