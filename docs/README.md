# Smart Ambulance Suite

## AI-Powered Emergency Patient Monitoring and Hospital Coordination

## Problem Statement

## Our Solution

## User Roles

### Ambulance Staff

### Doctor / Hospital Staff

## AI ECG Analysis

## System Architecture

## Technology Stack

## Project Structure

## Main API Endpoints

## Emergency Data Flow

## Running the Project Locally

## Demo Workflow

## Demo Login

## Key Features

## Future Improvements

## Medical Disclaimer

## Project

               # Smart Ambulance Suite — System Architecture

## 1. Overview

Smart Ambulance Suite consists of three major application layers:

1. Ambulance Frontend
2. Backend API
3. AI ECG Analysis Service
4. Hospital Dashboard

The system is designed to allow patient information collected during ambulance transport to be transferred to the hospital for early preparation and review.

---

## 2. High-Level Architecture

```text
                         SMART AMBULANCE SUITE

       +-----------------------+       +------------------------+
       |                       |       |                        |
       |   Ambulance Frontend  |       |  Hospital Dashboard    |
       |                       |       |                        |
       |  Patient Registration |       |  Patient Queue         |
       |  Vitals               |       |  Patient Information    |
       |  ECG Upload           |       |  Priority               |
       |  GPS                  |       |  ECG Review             |
       |                       |       |                        |
       +-----------+-----------+       +------------+-----------+
                   |                                |
                   |                                |
                   +---------------+----------------+
                                   |
                                   v
                         +-------------------+
                         |                   |
                         |   FastAPI Backend |
                         |                   |
                         +---------+---------+
                                   |
                     +-------------+-------------+
                     |                           |
                     v                           v
             +---------------+           +----------------+
             |               |           |                |
             |   Database    |           |   AI Service   |
             |               |           |                |
             | Patient Data  |           | ECG Analysis   |
             | Vitals        |           | Prediction     |
             | ECG Records   |           | Confidence     |
             |               |           |                |
             +---------------+           +----------------+
```

---

# 3. Application Components

## 3.1 Ambulance Frontend

The ambulance frontend is responsible for collecting information from ambulance personnel during patient transport.

### Main responsibilities

* Patient registration
* Patient demographic information
* Vital-sign entry
* ECG upload
* ECG viewing
* AI analysis result display
* GPS/location information
* Submission of patient data to the backend

### Technologies

* HTML
* CSS
* JavaScript

### Main frontend files

```text
frontend/
├── login.html
├── patient.html
├── Ecg viewer.html
├── ecg-result.html
├── gps.html
├── vitalsinput.html
├── success.html
├── script.js
└── style.css
```

---

# 4. Hospital Dashboard

The hospital dashboard provides hospital staff with information about patients being transported by ambulance.

### Main responsibilities

* Display incoming patients
* Display patient information
* Search patients
* Filter patients by priority
* Display emergency priority
* View patient details
* Access ECG information
* Review ECG analysis

### Technologies

* HTML
* CSS
* JavaScript

### Main dashboard files

```text
dashboard/
├── Patientcards.html
├── patientcards.js
├── patientcards.css
├── ecgviewer.html
└── Priorityqueue.html
```

---

# 5. Backend

The backend acts as the central communication layer between the ambulance application, database, AI service, and hospital dashboard.

### Technology

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL

### Responsibilities

* Receive patient information
* Store patient records
* Receive vital signs
* Store ECG records
* Communicate with the AI service
* Return patient information to the hospital dashboard
* Provide REST APIs for frontend applications

---

# 6. Database

The database stores information required by the ambulance and hospital applications.

### Main types of data

#### Patient Data

Includes information such as:

* Patient ID
* First name
* Last name
* Age
* Gender
* Medical notes
* Emergency priority

#### Vital Data

Includes information such as:

* Heart rate
* Blood pressure
* Oxygen saturation
* Temperature
* Other recorded vital signs

#### ECG Data

Includes information such as:

* ECG file or reference
* Patient association
* AI prediction
* Prediction confidence
* Analysis status

---

# 7. AI Service

The AI service is implemented as a separate Python service.

Its purpose is to analyze uploaded ECG images and provide an AI-assisted classification.

### ECG classifications

```text
Normal
Possible STEMI
Needs Cardiologist Review
```

The service receives an ECG image and returns a prediction with a confidence value.

### AI service endpoint

```text
POST /predict
```

### Technologies

* Python
* FastAPI
* TensorFlow
* Keras
* OpenCV
* Pillow
* Scikit-learn

---

# 8. AI Communication Flow

The ECG analysis process follows this flow:

```text
Ambulance User
      |
      v
ECG Upload
      |
      v
Frontend
      |
      v
FastAPI Backend
      |
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
      |
      v
Frontend / Hospital Dashboard
```

The backend communicates with the AI service rather than requiring the frontend to directly communicate with the AI model.

This keeps the AI component separated from the user interface.

---

# 9. Patient Data Flow

The overall patient workflow is:

```text
1. Ambulance Staff Login
             |
             v
2. Register Patient
             |
             v
3. Record Vitals
             |
             v
4. Upload ECG
             |
             v
5. AI ECG Analysis
             |
             v
6. Store Patient Information
             |
             v
7. Hospital Dashboard
             |
             v
8. Doctor Reviews Patient
```

---

# 10. Role-Based Application Flow

The application provides different interfaces based on the selected role.

```text
                         LOGIN
                           |
                +----------+----------+
                |                     |
                v                     v
        Ambulance Staff       Doctor / Hospital Staff
                |                     |
                v                     v
       Ambulance Frontend       Hospital Dashboard
                |                     |
                v                     v
        Patient / Vitals /      Patient Queue /
        ECG / GPS               ECG / Priority
```

The current prototype implements role-based navigation at the frontend level.

For production deployment, this can be extended using server-side authentication and authorization.

---

# 11. Communication Between Services

The system communicates through HTTP-based APIs.

```text
Ambulance Frontend
        |
        | HTTP Requests
        v
FastAPI Backend
        |
        | Database Operations
        v
PostgreSQL

FastAPI Backend
        |
        | HTTP Request
        v
AI Service
        |
        | Prediction
        v
FastAPI Backend

Hospital Dashboard
        |
        | HTTP Requests
        v
FastAPI Backend
```

---

# 12. Local Development Ports

During local development, the services use separate ports.

| Service    | Port |
| ---------- | ---: |
| Frontend   | 5500 |
| Backend    | 8000 |
| AI Service | 8001 |

### Frontend

```text
http://127.0.0.1:5500
```

### Backend

```text
http://127.0.0.1:8000
```

### AI Service

```text
http://127.0.0.1:8001
```

---

# 13. Project Directory Structure

```text
smart_ambulance_suite/
│
├── frontend/
│   ├── login.html
│   ├── patient.html
│   ├── Ecg viewer.html
│   ├── ecg-result.html
│   ├── gps.html
│   ├── vitalsinput.html
│   ├── success.html
│   ├── script.js
│   └── style.css
│
├── dashboard/
│   ├── Patientcards.html
│   ├── patientcards.js
│   ├── patientcards.css
│   ├── ecgviewer.html
│   └── Priorityqueue.html
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── core/
│       ├── models/
│       ├── schemas/
│       └── services/
│
├── ai/
│   ├── api/
│   ├── dataset/
│   ├── model/
│   ├── preprocessing/
│   ├── tests/
│   └── app.py
│
└── docs/
    ├── README.md
    └── ARCHITECTURE.md
```

---

# 14. Deployment Architecture

For deployment, the local services can be hosted separately.

```text
                     INTERNET
                         |
              +----------+----------+
              |                     |
              v                     v
        Frontend Host          Hospital Dashboard
              |                     |
              +----------+----------+
                         |
                         v
                  Backend Server
                         |
              +----------+----------+
              |                     |
              v                     v
          PostgreSQL           AI Service
```

The frontend and hospital dashboard communicate with the deployed backend using its public HTTPS URL.

The backend communicates with the deployed AI service through its service URL.

---

# 15. Security Considerations

The current project is a hackathon prototype.

Before production deployment, the following should be implemented:

* Secure user authentication
* JWT or session-based authentication
* Server-side role authorization
* HTTPS
* Password hashing
* Secure environment variables
* Database access controls
* API authentication
* File-upload validation
* Rate limiting
* Audit logging
* Patient-data encryption
* Appropriate healthcare data privacy controls

The current frontend role selection is intended primarily for demonstrating separate ambulance and hospital workflows.

---

# 16. Design Goal

The architecture is designed around one central objective:

> Provide hospitals with relevant patient information before the patient arrives, enabling earlier preparation and faster emergency response.

The separation of the ambulance application, backend, AI service, and hospital dashboard allows each component to be developed and scaled independently.
