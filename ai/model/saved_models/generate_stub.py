"""
Script to generate a demo MobileNetV2 model stub with random weights.

Run this once to create a working model file so the AI service can start
and return predictions immediately — without requiring real training data.

Usage:
    python model/saved_models/generate_stub.py

The stub model outputs valid class probabilities but predictions will be
random.  Replace the saved model with a trained version using:
    python model/train.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure ai/ is on the path
_AI_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_AI_ROOT))

OUTPUT_PATH = Path(__file__).parent / "ecg_model.keras"
NUM_CLASSES = 3
IMG_SIZE = 224


def generate_stub_model() -> None:
    """Build and save a random-weight MobileNetV2 head as the stub model."""
    try:
        import tensorflow as tf  # noqa: PLC0415
    except ImportError:
        print("ERROR: TensorFlow not installed.  Run: pip install tensorflow")
        sys.exit(1)

    print(f"Building MobileNetV2 stub model (classes={NUM_CLASSES}) …")

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights=None,  # Random weights — no internet access required
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3), name="ecg_input")
    x = base_model(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
    x = tf.keras.layers.BatchNormalization(name="bn")(x)
    x = tf.keras.layers.Dropout(0.4, name="dropout")(x)
    x = tf.keras.layers.Dense(128, activation="relu", name="fc")(x)
    outputs = tf.keras.layers.Dense(NUM_CLASSES, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="ecg_mobilenetv2_stub")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(OUTPUT_PATH))
    print(f"Stub model saved to '{OUTPUT_PATH}'.")
    print("NOTE: This model uses random weights — replace it with a trained model.")


if __name__ == "__main__":
    generate_stub_model()
