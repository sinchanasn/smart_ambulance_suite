from fastapi import FastAPI, UploadFile, File
from PIL import Image
import numpy as np
import io

from ai_edge_litert.interpreter import Interpreter

app = FastAPI()

# Load the lightweight TFLite model
interpreter = Interpreter(
    model_path="ecg_classifier.tflite"
)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

CLASS_NAMES = {
    0: "normal",
    1: "possible_stemi"
}

IMG_SIZE = (224, 224)


@app.get("/")
def home():
    return {
        "message": "ECG AI Service Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "ecg_classifier.tflite"
    }


@app.post("/predict")
async def predict_ecg(
    file: UploadFile = File(...)
):
    contents = await file.read()

    img = Image.open(
        io.BytesIO(contents)
    ).convert("RGB")

    img = img.resize(IMG_SIZE)

    img_array = np.array(
        img,
        dtype=np.float32
    )

    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    img_array = img_array / 255.0

    # Send image to the model
    interpreter.set_tensor(
        input_details[0]["index"],
        img_array
    )

    # Run AI inference
    interpreter.invoke()

    prediction = interpreter.get_tensor(
        output_details[0]["index"]
    )

    print("RAW MODEL OUTPUT:", prediction.tolist())

    index = int(np.argmax(prediction))

    confidence = float(
        np.max(prediction) * 100
    )

    return {
        "prediction": CLASS_NAMES[index],
        "confidence": round(confidence, 2)
    }