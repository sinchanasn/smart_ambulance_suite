from fastapi import FastAPI, UploadFile, File
import tensorflow as tf
# pyrefly: ignore [missing-import]
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io


app = FastAPI()


# Load model once when server starts
model = tf.keras.models.load_model(
    "utils/ecg_classifier.keras"
)


CLASS_NAMES = {
    0: "needs_review",
    1: "normal",
    2: "possible_stemi"
}


IMG_SIZE = (224,224)


@app.get("/")
def home():
    return {
        "message": "ECG AI Service Running"
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

    img_array = image.img_to_array(img)

    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    img_array = img_array / 255.0


    prediction = model.predict(img_array)


    index = np.argmax(prediction)

    confidence = float(
        np.max(prediction) * 100
    )


    return {
        "prediction": CLASS_NAMES[index],
        "confidence": round(confidence,2)
    }