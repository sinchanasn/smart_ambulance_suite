"""
Pydantic schemas for the Smart Ambulance AI Service API.

These schemas define the request/response contracts for the AI prediction
endpoint.  They are intentionally kept separate from backend schemas to
maintain service independence.
"""

from typing import Optional

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """Response model returned by the ``POST /predict`` endpoint.

    The AI service analyses a camera photograph of a printed ECG report and
    returns a classification result with clinical context.

    Attributes:
        prediction:  Snake-case ECG classification label.
        confidence:  Model confidence score in the range [0.0, 1.0].
        message:     Human-readable clinical action message.
        class_id:    Integer class index (0 = normal, 1 = possible_stemi,
                     2 = needs_review).
        display:     Human-friendly display label (title-cased).
    """

    prediction: str = Field(
        ...,
        description="Snake-case ECG classification label",
        examples=["possible_stemi"],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Prediction confidence score between 0 and 1",
        examples=[0.91],
    )
    message: str = Field(
        ...,
        description="Clinical action message for the predicted class",
        examples=["Signs of possible ST-elevation myocardial infarction detected. Immediate cardiologist intervention required."],
    )
    class_id: int = Field(
        ...,
        ge=0,
        description="Integer class index corresponding to the prediction label",
        examples=[1],
    )
    display: Optional[str] = Field(
        default=None,
        description="Human-friendly display label (e.g. 'Possible STEMI')",
        examples=["Possible STEMI"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "prediction": "possible_stemi",
                "confidence": 0.91,
                "message": "Signs of possible ST-elevation myocardial infarction detected. Immediate cardiologist intervention required.",
                "class_id": 1,
                "display": "Possible STEMI",
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response for the AI microservice.

    Attributes:
        status:        Overall service status string.
        model_loaded:  Whether the Keras model is currently loaded in memory.
        version:       Service version string.
    """

    status: str = Field(default="healthy", description="Service health status")
    model_loaded: bool = Field(
        ..., description="Indicates whether the prediction model is loaded"
    )
    version: str = Field(default="1.0.0", description="AI service version")
