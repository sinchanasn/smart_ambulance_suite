from fastapi import FastAPI, UploadFile, File
from PIL import Image
import numpy as np
import io

from ai_edge_litert.interpreter import Interpreter

app = FastAPI()

# ============================================================
# Load TFLite model
# ============================================================

interpreter = Interpreter(
    model_path="ecg_classifier.tflite"
)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# ============================================================
# TEMPORARY CLASS MAPPING
# ============================================================
# We are intentionally NOT assigning medical meanings yet.
# The deployed TFLite model appears to have 3 output classes,
# while train.py currently defines a 2-class model.
#
# We will identify the real class mapping before assigning
# "normal" or "possible_stemi".

CLASS_NAMES = {
    0: "class_0",
    1: "class_1",
    2: "class_2"
}

IMG_SIZE = (224, 224)


# ============================================================
# Home
# ============================================================

@app.get("/")
def home():
    return {
        "message": "ECG AI Service Running"
    }


# ============================================================
# Health check
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "ecg_classifier.tflite"
    }


# ============================================================
# ECG Prediction
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
    # Convert image to NumPy array
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

    # Normalize
    img_array = img_array / 255.0

    # --------------------------------------------------------
    # Send image to TFLite model
    # --------------------------------------------------------

    interpreter.set_tensor(
        input_details[0]["index"],
        img_array
    )

    # --------------------------------------------------------
    # Run inference
    # --------------------------------------------------------

    interpreter.invoke()

    prediction = interpreter.get_tensor(
        output_details[0]["index"]
    )

    # --------------------------------------------------------
    # DEBUG INFORMATION
    # --------------------------------------------------------

    print(
        "MODEL OUTPUT SHAPE:",
        output_details[0]["shape"]
    )

    print(
        "RAW MODEL OUTPUT:",
        prediction.tolist()
    )

    # --------------------------------------------------------
    # Get predicted class
    # --------------------------------------------------------

    index = int(
        np.argmax(prediction)
    )

    confidence = float(
        np.max(prediction) * 100
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "prediction": CLASS_NAMES[index],
        "confidence": round(confidence, 2)
    }