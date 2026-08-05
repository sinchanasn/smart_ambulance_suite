import tensorflow as tf
# pyrefly: ignore [missing-import]
from tensorflow.keras.preprocessing import image
import numpy as np
import sys


# Load trained model
MODEL_PATH = "ecg_classifier.keras"

model = tf.keras.models.load_model(MODEL_PATH)

print("Model loaded successfully")


# Class mapping from training output
CLASS_NAMES = {
    0: "needs_review",
    1: "normal",
    2: "possible_stemi"
}


# Image settings (same as training)
IMG_SIZE = (224, 224)


def predict_ecg(image_path):

    # Load image
    img = image.load_img(
        image_path,
        target_size=IMG_SIZE
    )

    # Convert image to array
    img_array = image.img_to_array(img)

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Normalize pixel values
    img_array = img_array / 255.0


    # Prediction
    prediction = model.predict(img_array)


    # Get highest probability class
    predicted_index = np.argmax(prediction)

    confidence = np.max(prediction) * 100


    result = {
        "prediction": CLASS_NAMES[predicted_index],
        "confidence": round(float(confidence), 2)
    }

    return result



# Run from terminal
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        exit()

    image_path = sys.argv[1]

    result = predict_ecg(image_path)

    print("\nECG Prediction")
    print("----------------")
    print("Class:", result["prediction"])
    print("Confidence:", result["confidence"], "%")