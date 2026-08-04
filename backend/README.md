# Smart Ambulance Suite - FastAPI Backend

Scalable, modular FastAPI backend foundation for the Smart Ambulance Suite hackathon project.

## Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── patient.py
│   │   ├── vitals.py
│   │   ├── ecg.py
│   │   ├── ambulance.py
│   │   └── hospital.py
│   ├── core/
│   │   └── config.py
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── services/
│   ├── websocket/
│   │   └── manager.py
│   ├── utils/
│   └── __init__.py
├── uploads/
├── tests/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup & Running Locally

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
   Activate the virtual environment:
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Linux/macOS: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   ```bash
   copy .env.example .env   # On Windows
   # or
   cp .env.example .env     # On Linux/macOS
   ```

5. **Start the development server:**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access Interactive API Documentation:**
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
   - Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## API Modules

- `/api/v1/patients` - Patient records and emergency triage
- `/api/v1/vitals` - Real-time patient vital metrics
- `/api/v1/ecg` - ECG signal telemetry and waveform upload
- `/api/v1/ambulances` - Ambulance tracking and dispatch status
- `/api/v1/hospitals` - Hospital ER availability and capacity
- `/ws/vitals` - Real-time WebSocket connection manager
