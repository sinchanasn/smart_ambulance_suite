Smart Ambulance Suite — API Documentation

1. Overview

The Smart Ambulance Suite backend provides REST APIs for communication between the ambulance frontend, AI service, database, and hospital dashboard.

The backend is built using FastAPI.

Backend Base URL

For local development:

http://127.0.0.1:8000

---

2. Patient API

Create Patient

Creates a new patient record.

Request

POST /patient

Purpose

Used by the ambulance application to submit patient information to the backend.

Example Request

{
    "first_name": "John",
    "last_name": "Doe",
    "age": 54,
    "gender": "Male",
    "medical_notes": "Chest pain and shortness of breath"
}

Example Response

{
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "age": 54,
    "gender": "Male",
    "medical_notes": "Chest pain and shortness of breath"
}

The returned patient ID can be used to associate additional information such as vitals and ECG records with the patient.

---

3. Get Patients

Retrieves patient records for the hospital dashboard.

Request

GET /patient/

Purpose

Used by the hospital dashboard to retrieve patients submitted by the ambulance application.

Example Response

[
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "age": 54,
        "gender": "Male",
        "medical_notes": "Chest pain and shortness of breath",
        "triage_priority": "High"
    }
]

The hospital dashboard uses this information to populate the patient cards and priority filters.

---

4. Vitals API

Submit Patient Vitals

Records vital signs associated with a patient.

Request

POST /vitals

Purpose

Used by the ambulance application to submit the patient's recorded vital signs.

Typical Data

The submitted information may include:

- Patient ID
- Heart rate
- Blood pressure
- Oxygen saturation
- Temperature
- Other recorded vital signs

Example Request

{
    "patient_id": 1,
    "heart_rate": 102,
    "blood_pressure": "145/92",
    "spo2": 94,
    "temperature": 37.2
}

Example Response

{
    "message": "Vitals recorded successfully"
}

---

5. ECG API

Submit ECG

Stores an ECG record associated with a patient.

Request

POST /ecg

Purpose

Used by the ambulance workflow to submit ECG information to the backend.

The ECG workflow can include:

1. ECG file selection or capture
2. Upload to backend
3. AI analysis
4. Prediction and confidence
5. Storage of the ECG record

ECG Processing Flow

ECG Image
    |
    v
Ambulance Frontend
    |
    v
Backend
    |
    v
AI Service
    |
    v
Prediction
    |
    v
Backend
    |
    v
Patient ECG Record

---

6. AI ECG Prediction API

The AI service runs separately from the main backend.

AI Base URL

For local development:

http://127.0.0.1:8001

Predict ECG Classification

Request

POST /predict

Request Type

The endpoint accepts an ECG image as a file upload.

Example Request

POST /predict
Content-Type: multipart/form-data

The uploaded file is provided as the ECG image.

Example Response

{
    "prediction": "possible_stemi",
    "confidence": 0.91
}

Possible Predictions

normal
possible_stemi
needs_review

The exact response structure may depend on the current AI service implementation.

---

7. Ambulance API

Get Ambulance Information

Retrieves ambulance-related information.

Request

GET /ambulance

Purpose

Provides ambulance information that can be used by the application or hospital-side services.

---

8. Hospital API

Get Hospital Information

Retrieves hospital-related information.

Request

GET /hospital

Purpose

Provides hospital information that can be used by the application for hospital coordination.

---

9. API Communication Flow

The overall communication architecture is:

AMBULANCE FRONTEND
        |
        | POST /patient
        | POST /vitals
        | POST /ecg
        |
        v
FASTAPI BACKEND
        |
        +----------------------+
        |                      |
        v                      v
    DATABASE              AI SERVICE
                               |
                               | POST /predict
                               |
                               v
                          ECG Prediction
                               |
                               v
                         FASTAPI BACKEND
                               |
                               v
                    HOSPITAL DASHBOARD
                               |
                               | GET /patient/
                               v
                         Patient Records

---

10. HTTP Status Codes

The API follows standard HTTP status codes.

Status Code| Meaning
200| Request successful
201| Resource created successfully
400| Invalid request
404| Resource not found
422| Validation error
500| Internal server error

---

11. API Validation

The backend uses Pydantic schemas to validate incoming API data.

Validation helps ensure that:

- Required fields are provided
- Data types are correct
- Invalid requests are rejected
- Database records receive structured data

FastAPI automatically provides validation responses when request data does not match the defined schema.

---

12. API Documentation Interface

FastAPI automatically provides interactive API documentation.

When the backend is running locally, the Swagger UI can be accessed at:

http://127.0.0.1:8000/docs

The OpenAPI schema can be accessed at:

http://127.0.0.1:8000/openapi.json

Swagger UI can be used to test available API endpoints during development.

---

13. Frontend-to-Backend Communication

The ambulance frontend communicates with the backend using HTTP requests.

The hospital dashboard also communicates with the backend to retrieve patient information.

Example:

const response = await fetch(
    "http://127.0.0.1:8000/patient/"
);

const patients = await response.json();

The deployed version will replace the local backend URL with the public backend URL.

---

14. Backend-to-AI Communication

The backend communicates with the AI service when an ECG requires analysis.

The architecture separates the AI service from the main backend:

Backend
   |
   | HTTP POST /predict
   v
AI Service
   |
   v
ECG Model
   |
   v
Prediction + Confidence
   |
   v
Backend

This separation allows the AI model to be updated independently from the main application.

---

15. Error Handling

The frontend and backend handle API failures so that users can receive feedback when a service is unavailable.

For example, the hospital dashboard displays an error message when it cannot connect to the backend.

Unable to connect to ambulance backend.

Backend errors are logged during development to assist with debugging.

---

16. Production API Considerations

Before production deployment, the API should include:

- HTTPS
- Authentication
- Authorization
- Secure API credentials
- Input validation
- File type validation
- File size limits
- Rate limiting
- CORS configuration
- Database security
- Error logging
- Audit logging

Patient information should only be accessible to authorized users.

---

17. Current Prototype Scope

The current API implementation is intended for a hackathon prototype.

The primary goal is to demonstrate the complete emergency data flow:

Patient Registration
        ↓
Vitals
        ↓
ECG
        ↓
AI Analysis
        ↓
Backend Storage
        ↓
Hospital Dashboard

Production deployment would require additional authentication, authorization, security, monitoring, and healthcare data compliance measures.