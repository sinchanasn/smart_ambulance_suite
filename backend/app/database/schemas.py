from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# -------------------------
# Patient Schemas
# -------------------------

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    triage_priority: Optional[str] = "Level 2 (Urgent)"
    medical_notes: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class PatientCreateResponse(BaseModel):
    message: str
    patient_id: int


# -------------------------
# Vitals Schemas
# -------------------------

class VitalsBase(BaseModel):
    patient_id: int
    heart_rate: Optional[int] = None
    blood_pressure: Optional[str] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None


class VitalsCreate(VitalsBase):
    pass

class VitalsUpdate(BaseModel):
    heart_rate: Optional[int] = None
    blood_pressure: Optional[str] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None


class VitalsResponse(VitalsBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# ECG Schemas
# -------------------------

class ECGBase(BaseModel):
    patient_id: int
    rhythm_status: Optional[str] = "Normal Sinus Rhythm"
    qrs_duration: Optional[float] = None
    lead_data: Optional[str] = None


class ECGCreate(ECGBase):
    pass


class ECGResponse(ECGBase):
    id: int
    image_path: Optional[str] = None
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    uploaded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ECGUploadResponse(BaseModel):
    message: str
    patient_id: int
    ecg_id: int
    image_path: Optional[str] = None
    # AI prediction fields — populated if the AI service was reachable.
    # None if the AI service was unavailable at upload time.
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    status: Optional[str] = None


# -------------------------
# Ambulance Location
# -------------------------

class AmbulanceLocation(BaseModel):
    ambulance_id: str
    latitude: float
    longitude: float
    speed_kmh: Optional[float] = 0.0
    status: str = "EN_ROUTE"
    eta_minutes: Optional[int] = 10


class HospitalInfo(BaseModel):
    hospital_id: str
    name: str
    available_beds: int
    er_status: str = "OPEN"
    trauma_center_level: int = 1