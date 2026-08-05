"""
Smart Ambulance AI Service — FastAPI application entry point.

Start the service:
    uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

Environment variables:
    AI_SERVICE_HOST   Bind host (default: ``0.0.0.0``).
    AI_SERVICE_PORT   Bind port (default: ``8001``).
    MODEL_PATH        Path to the saved Keras model file.
    AI_LOG_LEVEL      Logging verbosity (default: ``INFO``).
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as prediction_router
from api.schemas import HealthResponse
from model.loader import is_model_loaded, load_model
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan: load model once at startup, clean up on shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Loads the ECG model on startup.  If the model file is missing the service
    still starts but returns ``503`` for prediction requests until the model
    is available (allows independent deployment without a trained model).
    """
    logger.info("Smart Ambulance AI Service starting up …")
    try:
        load_model()
        logger.info("Model loaded successfully — service is ready.")
    except FileNotFoundError as exc:
        logger.warning(
            "Model file not found: %s  "
            "Predictions will return 503 until the model is available.  "
            "Run 'python model/saved_models/generate_stub.py' to create a demo model.",
            exc,
        )
    except RuntimeError as exc:
        logger.error("Model load failed: %s", exc)

    yield  # Application runs here

    logger.info("Smart Ambulance AI Service shutting down.")


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Smart Ambulance AI Service",
    description=(
        "Microservice providing ECG image classification via a MobileNetV2 "
        "transfer learning model.  Consumed by the Smart Ambulance backend.\n\n"
        "**Endpoint summary:**\n"
        "- `POST /predict` — Upload an ECG image and receive an AI classification.\n"
        "- `GET  /health`  — Service health and model status.\n"
        "- `GET  /`        — Root status check."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — restrict to known origins in production via the env var
# ---------------------------------------------------------------------------
_cors_origins: list[str] = os.getenv(
    "AI_CORS_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(prediction_router)


# ---------------------------------------------------------------------------
# Health and root endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/",
    summary="Root status",
    include_in_schema=False,
)
async def root() -> dict[str, str]:
    """Return a simple alive message."""
    return {"message": "Smart Ambulance AI Service is running", "version": "1.0.0"}


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["health"],
)
async def health() -> HealthResponse:
    """Return the service health status including model load state."""
    model_loaded = is_model_loaded()
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        version="1.0.0",
    )


# ---------------------------------------------------------------------------
# Dev runner (python api/main.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn  # noqa: PLC0415

    host: str = os.getenv("AI_SERVICE_HOST", "0.0.0.0")
    port: int = int(os.getenv("AI_SERVICE_PORT", "8001"))

    logger.info("Starting AI service on %s:%d", host, port)
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
