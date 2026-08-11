from fastapi import FastAPI, UploadFile, File
from PIL import Image
import tensorflow as tf
import numpy as np
import io
import os

app = FastAPI()

# ============================================================
# LOAD VALID KERAS MODEL
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "ecg_classifier.keras"
)

model = tf.keras.models.load_model(MODEL_PATH)

print("ECG Keras model loaded successfully")
print("Model input shape:", model.input_shape)
print("Model output shape:", model.output_shape)

# ============================================================
# CLASS MAPPING
# ============================================================

CLASS_NAMES = {
    0: "normal",
    1: "possible_stemi"
}

IMG_SIZE = (224, 224)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "ECG AI Service Running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "ecg_classifier.keras"
    }


# ============================================================
# ECG PREDICTION
# ============================================================

@app.post("/predict")
async def predict_ecg(
    file: UploadFile = File(...)
):

    contents = await file.read()

    # --------------------------------------------------------
    # Load image
    # --------------------------------------------------------

    img = Image.open(
        io.BytesIO(contents)
    ).convert("RGB")

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    img = img.resize(IMG_SIZE)

    # --------------------------------------------------------
    # Convert to NumPy
    # --------------------------------------------------------

    img_array = np.array(
        img,
        dtype=np.float32
    )

    # Add batch dimension
    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    # Normalize exactly as training
    img_array = img_array / 255.0

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model.predict(
        img_array,
        verbose=0
    )[0]

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print("RAW MODEL OUTPUT:", prediction.tolist())

    # --------------------------------------------------------
    # Get predicted class
    # --------------------------------------------------------

    index = int(
        np.argmax(prediction)
    )

    confidence = float(
        prediction[index] * 100
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "prediction": CLASS_NAMES[index],
        "confidence": round(confidence, 2),
        "normal_probability": round(
            float(prediction[0]) * 100,
            2
        ),
        "possible_stemi_probability": round(
            float(prediction[1]) * 100,
            2
        )
    }