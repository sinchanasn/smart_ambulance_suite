# Smart Ambulance AI Service

> **MobileNetV2-based ECG classification microservice** for the Smart Ambulance Suite.
> Runs as an independent FastAPI service on **port 8001** and is called by the backend
> after an ECG image is uploaded.

---

## Architecture

```
Frontend
   ↓  POST /ecg/   (multipart image)
Backend API  (FastAPI, port 8000)
   ↓  POST /predict  (httpx, async)
AI Service   (FastAPI, port 8001)  ← this module
   ↓  JSON: { prediction, confidence, class_id }
Backend stores prediction → ECG.prediction + ECG.confidence
   ↓
Hospital Dashboard reads ECGResponse with prediction fields
```

---

## ECG Classification Labels

| class_id | Label | Description |
|---|---|---|
| 0 | Normal | No significant abnormality detected |
| 1 | Possible STEMI | Potential ST-elevation myocardial infarction |
| 2 | Needs Cardiologist Review | Abnormality detected, expert review required |

---

## Quick Start

### 1. Install dependencies

```bash
cd ai/
pip install -r requirements.txt
```

### 2. Generate a demo model stub (no training data needed)

```bash
python model/saved_models/generate_stub.py
```

> This creates a random-weight MobileNetV2 model so the service starts immediately.
> Replace it with a trained model when real ECG data is available.

### 3. Start the AI service

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

Or using the built-in runner:

```bash
python api/main.py
```

### 4. Test the endpoint

```bash
curl -X POST http://localhost:8001/predict \
     -F "file=@/path/to/ecg.png"
```

**Response:**
```json
{
  "prediction": "Possible STEMI",
  "confidence": 0.94,
  "class_id": 1
}
```

### 5. Check health

```bash
curl http://localhost:8001/health
```

---

## Training a Real Model

### Dataset structure

Place ECG images under `ai/dataset/` in subdirectories named after each class:

```
ai/dataset/
├── Normal/
│   ├── ecg_001.png
│   └── …
├── Possible_STEMI/
│   ├── ecg_042.jpg
│   └── …
└── Needs_Cardiologist_Review/
    ├── ecg_099.jpeg
    └── …
```

### Run training

```bash
cd ai/
python model/train.py
```

Training runs in two phases:
1. **Phase 1** (10 epochs): Frozen MobileNetV2 base, trains top layers only.
2. **Phase 2** (10 epochs): Unfreezes top-30 base layers for fine-tuning at a lower learning rate.

The best checkpoint is saved to `model/saved_models/ecg_model.keras`.

### Environment variables for training

| Variable | Default | Description |
|---|---|---|
| `DATASET_DIR` | `dataset/` | Path to training image directory |
| `MODEL_PATH` | `model/saved_models/ecg_model.keras` | Model save location |
| `BATCH_SIZE` | `32` | Training batch size |
| `IMG_SIZE` | `224` | Image dimension (square) |

---

## Running Tests

```bash
cd ai/
pytest tests/ -v
```

Test coverage:
- `test_preprocess.py` — 13 tests: shape, dtype, range, colour mode conversion, error handling (no TensorFlow required)
- `test_predict.py` — 12 tests: schema, confidence range, label mapping, error propagation (model fully mocked)

---

## Configuration

Copy `.env.example` to `.env` and adjust:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `AI_SERVICE_HOST` | `0.0.0.0` | Bind address |
| `AI_SERVICE_PORT` | `8001` | Bind port |
| `AI_LOG_LEVEL` | `INFO` | Log verbosity |
| `MODEL_PATH` | `model/saved_models/ecg_model.keras` | Keras model path |
| `MAX_ECG_SIZE_BYTES` | `10485760` (10 MB) | Max upload size |
| `AI_CORS_ORIGINS` | `http://localhost:8000,…` | Allowed CORS origins |

---

## Backend Integration

The backend connects to this service via `backend/app/services/ai_client.py`.

**Backend env variables to set:**

```env
AI_SERVICE_URL=http://localhost:8001
AI_TIMEOUT_SEC=30
```

The integration is **gracefully degrading**: if the AI service is down, the ECG upload still
succeeds and `prediction` / `confidence` will be `null` in the response. The backend will
update these fields when the AI service is restored.

---

## Module Structure

```
ai/
├── api/
│   ├── main.py          # FastAPI app + lifespan model loader
│   ├── routes.py        # POST /predict endpoint
│   └── schemas.py       # PredictionResponse, HealthResponse
├── model/
│   ├── loader.py        # Singleton model cache
│   ├── predict.py       # run_prediction() inference engine
│   ├── train.py         # MobileNetV2 training script
│   ├── labels.json      # class_id → label mapping
│   └── saved_models/
│       └── generate_stub.py   # Demo model generator
├── preprocessing/
│   ├── preprocess.py    # preprocess_ecg_image() — pure function
│   └── augment.py       # Keras augmentation pipeline (training only)
├── utils/
│   └── logger.py        # Structured logging utility
├── tests/
│   ├── test_preprocess.py
│   └── test_predict.py
├── dataset/             # Place training images here
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

---

## API Reference

### `POST /predict`

Classify an uploaded ECG image.

**Request:** `multipart/form-data` with field `file` (PNG / JPG / JPEG, max 10 MB)

**Response:**
```json
{
  "prediction": "Possible STEMI",
  "confidence": 0.94,
  "class_id": 1
}
```

**Error responses:**

| Status | Description |
|---|---|
| 400 | Invalid file type or corrupt image |
| 413 | File exceeds 10 MB limit |
| 503 | Model not yet loaded |
| 500 | Internal inference error |

### `GET /health`

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

## Design Constraints

This service intentionally does **not**:
- Access the database directly
- Implement authentication or authorisation
- Use WebSockets
- Send push notifications
- Duplicate backend functionality

All of the above remain the backend's responsibility.
