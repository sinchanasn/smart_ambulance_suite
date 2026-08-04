from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Patient(Base):
    """Patient ORM Model representing emergency care subjects."""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    triage_priority = Column(String(50), default="Level 2 (Urgent)")
    medical_notes = Column(Text, nullable=True)
    ambulance_id = Column(String(50), nullable=True)
    hospital = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vitals = relationship("Vitals", back_populates="patient", cascade="all, delete-orphan")
    ecg_records = relationship("ECG", back_populates="patient", cascade="all, delete-orphan")


class Vitals(Base):
    """Vitals ORM Model representing patient telemetry data."""
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    heart_rate = Column(Integer, nullable=True)         # BPM
    blood_pressure = Column(String(20), nullable=True)  # mmHg (e.g. "120/80")
    spo2 = Column(Float, nullable=True)                 # Oxygen saturation %
    temperature = Column(Float, nullable=True)          # Celsius
    respiratory_rate = Column(Integer, nullable=True)   # breaths/min, optional
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="vitals")


class ECG(Base):
    """ECG ORM Model representing uploaded cardiac ECG scans and AI review data."""
    __tablename__ = "ecg_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(255), nullable=True)       # Path to uploaded ECG image scan
    prediction = Column(String(100), nullable=True)       # AI-inferred rhythm/condition label
    confidence = Column(Float, nullable=True)             # AI prediction confidence score
    doctor_review = Column(Text, nullable=True)            # Clinician's review/annotation
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="ecg_records")