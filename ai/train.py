import tensorflow as tf
# pyrefly: ignore [missing-import]
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Dataset paths
TRAIN_DIR = "dataset/train"
TEST_DIR = "dataset/test"

# Image settings
IMG_SIZE = (224, 224)
BATCH_SIZE = 16

# Load images
train_gen = ImageDataGenerator(rescale=1./255)
test_gen = ImageDataGenerator(rescale=1./255)

train_data = train_gen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

test_data = test_gen.flow_from_directory(
    TEST_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

print(train_data.class_indices)

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam


base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224,224,3)
)

base_model.trainable = False


model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.3),
    Dense(128, activation="relu"),
    Dense(3, activation="softmax")
])


model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)


model.summary()


history = model.fit(
    train_data,
    epochs=10,
    validation_data=test_data
)


model.save("ecg_classifier.keras")

print("Model saved successfully")