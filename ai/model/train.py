"""
MobileNetV2 Transfer Learning Training Script for ECG Report Classification.

CONTEXT
-------
This model classifies **camera photographs of printed ECG reports**, not raw
ECG signal data.  The training pipeline is designed for this specific input
modality and applies ambulance-specific data augmentation.

USAGE
-----
    cd ai/
    python model/train.py

    # With custom configuration:
    IMG_SIZE=224 EPOCHS_PHASE1=15 EPOCHS_PHASE2=10 BATCH_SIZE=16 python model/train.py

DATASET STRUCTURE (required before training)
--------------------------------------------
    dataset/
    ├── train/
    │   ├── normal/            ← camera photos of normal ECG reports
    │   ├── possible_stemi/    ← camera photos of STEMI ECG reports
    │   └── needs_review/      ← camera photos of other abnormal reports
    ├── validation/
    │   ├── normal/
    │   ├── possible_stemi/
    │   └── needs_review/
    └── test/                  ← held-out; NOT used during training
        ├── normal/
        ├── possible_stemi/
        └── needs_review/

ENVIRONMENT VARIABLES (all optional — defaults shown)
------------------------------------------------------
    DATASET_DIR       Path to dataset root              (default: ai/dataset/)
    MODEL_SAVE_PATH   Path to save trained model        (default: ai/model/saved_models/ecg_model.h5)
    IMG_SIZE          Square image size (px)            (default: 224)
    BATCH_SIZE        Training batch size               (default: 16)
    EPOCHS_PHASE1     Phase 1 epochs (frozen base)      (default: 15)
    EPOCHS_PHASE2     Phase 2 epochs (fine-tune)        (default: 10)
    LR_PHASE1         Phase 1 learning rate             (default: 1e-3)
    LR_PHASE2         Phase 2 learning rate             (default: 1e-5)
    FINE_TUNE_LAYERS  How many top base layers to unfreeze in Phase 2 (default: 30)

⚠️  IMPORTANT
    Do NOT start the API (uvicorn api.main:app) to trigger training.
    Training is entirely offline and must be run manually using this script.

⚠️  DISCLAIMER
    This is a prototype ECG image classification system.  It requires a
    properly labelled clinical dataset reviewed by licensed cardiologists for
    real-world medical validation.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve ai/ root so relative imports work when executed directly
# ---------------------------------------------------------------------------
_AI_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_ROOT))

from utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------
NUM_CLASSES = 3
CLASS_NAMES = ["needs_review", "normal", "possible_stemi"]  # alphabetical — matches Keras default


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _resolve_path(env_var: str, default: str) -> Path:
    raw = os.getenv(env_var, str(_AI_ROOT / default))
    return Path(raw)


def _get_config() -> dict:
    """Read all training configuration from environment variables."""
    return {
        "dataset_dir":      _resolve_path("DATASET_DIR", "dataset"),
        "model_save_path":  _resolve_path("MODEL_SAVE_PATH", "model/saved_models/ecg_model.h5"),
        "img_size":         int(os.getenv("IMG_SIZE", "224")),
        "batch_size":       int(os.getenv("BATCH_SIZE", "16")),
        "epochs_phase1":    int(os.getenv("EPOCHS_PHASE1", "15")),
        "epochs_phase2":    int(os.getenv("EPOCHS_PHASE2", "10")),
        "lr_phase1":        float(os.getenv("LR_PHASE1", "1e-3")),
        "lr_phase2":        float(os.getenv("LR_PHASE2", "1e-5")),
        "fine_tune_layers": int(os.getenv("FINE_TUNE_LAYERS", "30")),
    }


# ---------------------------------------------------------------------------
# Model builder
# ---------------------------------------------------------------------------

def build_model(num_classes: int, img_size: int = 224):
    """Construct the MobileNetV2 transfer learning model.

    Architecture:
        ┌────────────────────────────────────────┐
        │  Input (H × W × 3)                    │
        │  MobileNetV2 (frozen, ImageNet weights)│
        │  GlobalAveragePooling2D               │
        │  BatchNormalization                   │
        │  Dropout(0.4)                         │
        │  Dense(256, relu)                     │
        │  Dropout(0.3)                         │
        │  Dense(num_classes, softmax)          │
        └────────────────────────────────────────┘

    Args:
        num_classes: Number of output classes (should be 3).
        img_size:    Side length for the square input image.

    Returns:
        Tuple of ``(model, base_model)`` — the full Keras model and the
        MobileNetV2 base (needed for Phase 2 unfreezing).
    """
    import tensorflow as tf  # noqa: PLC0415

    logger.info("Building MobileNetV2 (img_size=%d × %d, classes=%d) …", img_size, img_size, num_classes)

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(img_size, img_size, 3),
        include_top=False,
        weights="imagenet",   # Pre-trained on ImageNet
    )
    base_model.trainable = False  # Frozen for Phase 1

    inputs = tf.keras.Input(shape=(img_size, img_size, 3), name="ecg_input")

    # Run base in inference mode during Phase 1 (keeps BatchNorm frozen)
    x = base_model(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
    x = tf.keras.layers.BatchNormalization(name="bn_head")(x)
    x = tf.keras.layers.Dropout(0.4, name="drop1")(x)
    x = tf.keras.layers.Dense(256, activation="relu", name="fc1")(x)
    x = tf.keras.layers.Dropout(0.3, name="drop2")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="ecg_mobilenetv2")
    logger.info("Model built. Trainable params: %s", f"{model.count_params():,}")
    return model, base_model


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def _load_split(split_dir: Path, img_size: int, batch_size: int, augment_fn=None):
    """Load a single dataset split from a directory.

    Args:
        split_dir:   Path to the split directory (``train/``, ``validation/``, etc.)
        img_size:    Target image size.
        batch_size:  Batch size.
        augment_fn:  Optional callable ``(x, y) → (x, y)`` to apply augmentation.

    Returns:
        A ``tf.data.Dataset`` of ``(image_batch, label_batch)`` tuples.
    """
    import tensorflow as tf  # noqa: PLC0415

    if not split_dir.exists():
        logger.error("Split directory not found: %s", split_dir)
        sys.exit(1)

    ds = tf.keras.utils.image_dataset_from_directory(
        str(split_dir),
        image_size=(img_size, img_size),
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=(augment_fn is not None),  # Only shuffle training set
        seed=42,
    )

    class_names = ds.class_names
    num_classes = len(class_names)
    logger.info("  Loaded '%s': classes=%s  batches=%d", split_dir.name, class_names, len(ds))

    # Normalise to [0, 1]
    normalise = tf.keras.layers.Rescaling(1.0 / 255)
    AUTOTUNE = tf.data.AUTOTUNE

    if augment_fn is not None:
        ds = ds.map(lambda x, y: (augment_fn(normalise(x), training=True), y), num_parallel_calls=AUTOTUNE)
    else:
        ds = ds.map(lambda x, y: (normalise(x), y), num_parallel_calls=AUTOTUNE)

    return ds.prefetch(AUTOTUNE), class_names, num_classes


# ---------------------------------------------------------------------------
# Training pipeline
# ---------------------------------------------------------------------------

def train() -> None:
    """Run the full two-phase training pipeline and save the trained model.

    Phase 1 — Train head only (frozen MobileNetV2 base):
        Learning rate: LR_PHASE1 (default 1e-3)
        Epochs:        EPOCHS_PHASE1 (default 15)

    Phase 2 — Fine-tune (top FINE_TUNE_LAYERS of base unfrozen):
        Learning rate: LR_PHASE2 (default 1e-5, conservative)
        Epochs:        EPOCHS_PHASE2 (default 10)

    Best checkpoint is saved at each phase; final model saved on completion.

    ⚠️ DISCLAIMER: This is a prototype system.  A clinically validated labelled
    dataset is required before deployment in any medical setting.
    """
    import tensorflow as tf  # noqa: PLC0415
    from preprocessing.augment import get_augmentation_pipeline  # noqa: E402

    config = _get_config()

    logger.info("=" * 60)
    logger.info("Smart Ambulance ECG Training Pipeline")
    logger.info("INPUT: Camera photographs of printed ECG reports")
    logger.info("=" * 60)
    logger.info("Configuration:")
    for k, v in config.items():
        logger.info("  %-20s = %s", k, v)

    # ------------------------------------------------------------------
    # Validate dataset structure
    # ------------------------------------------------------------------
    dataset_dir: Path = config["dataset_dir"]
    train_dir   = dataset_dir / "train"
    val_dir     = dataset_dir / "validation"
    test_dir    = dataset_dir / "test"

    for split_path, split_name in [(train_dir, "train"), (val_dir, "validation")]:
        if not split_path.exists():
            logger.error(
                "Required dataset split '%s' not found at: %s\n"
                "See ai/dataset/README.md for dataset preparation instructions.",
                split_name,
                split_path,
            )
            sys.exit(1)

    # ------------------------------------------------------------------
    # Load datasets
    # ------------------------------------------------------------------
    logger.info("Loading datasets …")
    augment = get_augmentation_pipeline()
    img_size: int = config["img_size"]
    batch_size: int = config["batch_size"]

    train_ds, class_names, num_classes = _load_split(train_dir, img_size, batch_size, augment_fn=augment)
    val_ds, _, _ = _load_split(val_dir, img_size, batch_size, augment_fn=None)

    logger.info("Classes (%d): %s", num_classes, class_names)

    # ------------------------------------------------------------------
    # Build model
    # ------------------------------------------------------------------
    model, base_model = build_model(num_classes=num_classes, img_size=img_size)
    model_save_path: Path = config["model_save_path"]
    model_save_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Shared callbacks
    # ------------------------------------------------------------------
    checkpoint_cb = tf.keras.callbacks.ModelCheckpoint(
        filepath=str(model_save_path),
        save_best_only=True,
        monitor="val_accuracy",
        mode="max",
        verbose=1,
    )
    early_stop_cb = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=5,
        restore_best_weights=True,
        verbose=1,
    )
    reduce_lr_cb = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1,
    )
    tensorboard_cb = tf.keras.callbacks.TensorBoard(
        log_dir=str(model_save_path.parent / "logs"),
        histogram_freq=1,
    )

    # ------------------------------------------------------------------
    # Phase 1: Train head only (MobileNetV2 base frozen)
    # ------------------------------------------------------------------
    logger.info("")
    logger.info("=== PHASE 1: Training head layers (base frozen) ===")
    logger.info("    Epochs: %d   LR: %g", config["epochs_phase1"], config["lr_phase1"])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config["lr_phase1"]),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    history_p1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config["epochs_phase1"],
        callbacks=[checkpoint_cb, early_stop_cb, reduce_lr_cb, tensorboard_cb],
        verbose=1,
    )

    logger.info(
        "Phase 1 complete. Best val_accuracy: %.4f",
        max(history_p1.history.get("val_accuracy", [0.0])),
    )

    # ------------------------------------------------------------------
    # Phase 2: Fine-tune top layers of the base model
    # ------------------------------------------------------------------
    fine_tune_layers: int = config["fine_tune_layers"]
    logger.info("")
    logger.info("=== PHASE 2: Fine-tuning (top %d base layers) ===", fine_tune_layers)
    logger.info("    Epochs: %d   LR: %g", config["epochs_phase2"], config["lr_phase2"])

    base_model.trainable = True
    for layer in base_model.layers[:-fine_tune_layers]:
        layer.trainable = False

    trainable_count = sum(1 for l in base_model.layers if l.trainable)
    logger.info("  Trainable base layers: %d / %d", trainable_count, len(base_model.layers))

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config["lr_phase2"]),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    history_p2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config["epochs_phase2"],
        callbacks=[checkpoint_cb, early_stop_cb, reduce_lr_cb, tensorboard_cb],
        verbose=1,
    )

    logger.info(
        "Phase 2 complete. Best val_accuracy: %.4f",
        max(history_p2.history.get("val_accuracy", [0.0])),
    )

    # ------------------------------------------------------------------
    # Save final model (.h5 format)
    # ------------------------------------------------------------------
    model.save(str(model_save_path))
    logger.info("")
    logger.info("✓ Model saved to: %s", model_save_path)
    logger.info("")
    logger.info("⚠️  REMINDER: This is a prototype system.")
    logger.info("   Clinical validation with labelled data from a cardiologist is required")
    logger.info("   before this model can be used in a real medical setting.")

    # ------------------------------------------------------------------
    # Optional test-set evaluation
    # ------------------------------------------------------------------
    if test_dir.exists():
        logger.info("")
        logger.info("Test set found — running final held-out evaluation …")
        test_ds, _, _ = _load_split(test_dir, img_size, batch_size, augment_fn=None)
        loss, acc = model.evaluate(test_ds, verbose=1)
        logger.info("Test set → loss=%.4f  accuracy=%.4f", loss, acc)
    else:
        logger.info(
            "No test/ directory found. Skipping held-out evaluation.\n"
            "Add images to dataset/test/ and re-run for final metrics."
        )


if __name__ == "__main__":
    train()
