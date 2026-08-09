Smart Ambulance Suite — Setup Guide

1. Prerequisites

Before running the project, install the following:

- Git
- Python 3.10 or compatible Python version
- PostgreSQL
- A modern web browser
- An IDE or code editor

The project uses separate services for the frontend, backend, and AI system.

---

2. Clone the Repository

Clone the project from GitHub:

git clone <YOUR_GITHUB_REPOSITORY_URL>

Move into the project directory:

cd smart_ambulance_suite

The project should contain:

smart_ambulance_suite/
├── frontend/
├── backend/
├── ai/
├── dashboard/
└── docs/

---

3. Backend Setup

Open a terminal in the project directory.

Move into the backend:

cd backend

Create a Python virtual environment:

python -m venv venv

Activate the virtual environment on Windows:

venv\Scripts\activate

Install the backend dependencies:

pip install -r requirements.txt

---

4. Database Setup

The backend uses PostgreSQL for persistent data storage.

Create a PostgreSQL database for the project.

Example database name:

smart_ambulance_db

Configure the database connection using the backend configuration.

Example:

postgresql://postgres:postgres@localhost:5432/smart_ambulance_db

For deployment, database credentials should be stored using environment variables rather than hard-coded in source code.

---

5. Start the Backend

From the "backend" directory:

python -m uvicorn app.main:app --reload

The backend should start at:

http://127.0.0.1:8000

Verify that the API is running by opening:

http://127.0.0.1:8000/docs

This opens the FastAPI Swagger UI.

---

6. AI Service Setup

Open a new terminal.

Move into the AI directory:

cd ai

Create a virtual environment if required:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

Install the AI dependencies:

pip install -r requirements.txt

The AI service requires the trained ECG classification model.

The model should be available in the model directory according to the project's AI configuration.

---

7. Start the AI Service

From the "ai" directory:

python -m uvicorn app:app --reload --port 8001

The AI service should be available at:

http://127.0.0.1:8001

The ECG prediction endpoint is:

POST /predict

---

8. Frontend Setup

The frontend consists of static HTML, CSS, and JavaScript files.

A local web server should be used instead of opening the HTML files directly using "file://".

Open a new terminal.

From the project root:

cd smart_ambulance_suite

Start the Python HTTP server:

python -m http.server 5500

The project will be available at:

http://127.0.0.1:5500

---

9. Open the Application

Open the login page:

http://127.0.0.1:5500/frontend/login.html

The application provides two demonstration roles.

---

10. Ambulance Login

Select:

Ambulance Staff

Use the configured demonstration credentials:

Username: ambulance
Password: ambulance123

The ambulance workflow provides access to:

- Patient registration
- Vital signs
- ECG upload
- ECG analysis
- GPS/location features

---

11. Hospital Login

Select:

Doctor / Hospital Staff

Use the configured demonstration credentials:

Username: doctor
Password: doctor123

The hospital workflow provides access to:

- Patient dashboard
- Patient information
- Priority information
- ECG information
- Patient review

---

12. Running All Services

For the complete application, three services need to run simultaneously.

Terminal 1 — Backend

cd backend
python -m uvicorn app.main:app --reload

Runs on:

http://127.0.0.1:8000

Terminal 2 — AI Service

cd ai
python -m uvicorn app:app --reload --port 8001

Runs on:

http://127.0.0.1:8001

Terminal 3 — Frontend

python -m http.server 5500

Runs on:

http://127.0.0.1:5500

---

13. Complete Application Flow

Once all services are running:

                    Login
                      |
          +-----------+-----------+
          |                       |
          v                       v
   Ambulance Staff       Doctor / Hospital Staff
          |                       |
          v                       v
    Patient Entry          Hospital Dashboard
          |
          v
       Vitals
          |
          v
      ECG Upload
          |
          v
      AI Service
          |
          v
    ECG Prediction
          |
          v
    FastAPI Backend
          |
          v
   Hospital Dashboard

---

14. Troubleshooting

Backend does not start

Check that:

- Python is installed
- The virtual environment is activated
- Backend dependencies are installed
- PostgreSQL is running
- The database configuration is correct

Try:

python -m uvicorn app.main:app --reload

---

AI service does not start

Check that:

- The AI virtual environment is activated
- AI dependencies are installed
- The trained model exists
- Port "8001" is available

Try:

python -m uvicorn app:app --reload --port 8001

---

Frontend shows 404 errors

Make sure the HTTP server is running from:

smart_ambulance_suite/

not from inside the "frontend" directory.

Start it with:

python -m http.server 5500

Then open:

http://127.0.0.1:5500/frontend/login.html

---

Frontend cannot connect to backend

Make sure the backend is running on:

http://127.0.0.1:8000

Check the browser developer console for network or CORS errors.

The frontend API URLs should point to the running backend.

---

ECG AI analysis does not work

Check that:

1. The backend is running.
2. The AI service is running.
3. The AI service is listening on port "8001".
4. The trained model is available.
5. The ECG file is a supported image format.
6. The backend AI client is configured to use the correct AI service URL.

---

15. Important Configuration

Do not commit sensitive information to GitHub.

Sensitive values such as:

- Database passwords
- API keys
- Authentication secrets
- Cloud credentials
- Production URLs containing credentials

should be stored using environment variables.

Example:

DATABASE_URL=<database-url>
AI_SERVICE_URL=<ai-service-url>
SECRET_KEY=<secret-key>

---

16. Production Deployment

The local development URLs:

http://127.0.0.1:5500
http://127.0.0.1:8000
http://127.0.0.1:8001

are only for local development.

During deployment, they must be replaced with the public URLs of the deployed services.

Example architecture:

Public Frontend
       |
       v
Public Backend API
       |
       +-------> PostgreSQL
       |
       +-------> Public AI Service

All production communication should use HTTPS.

---

17. Recommended Startup Order

For local development:

1. Start PostgreSQL
2. Start AI service
3. Start FastAPI backend
4. Start frontend server
5. Open frontend/login.html

This ensures that the backend and AI services are available when the frontend starts sending requests.

---

18. Development Notes

The project is currently configured as a hackathon prototype.

Some components use local URLs and demonstration credentials.

Before production deployment, the following should be implemented:

- Production authentication
- Secure password storage
- Server-side role authorization
- HTTPS
- Environment variables
- Production database
- CORS configuration
- Secure file uploads
- Monitoring and logging
- Healthcare data security and compliance

---

19. Quick Start

For experienced developers, the minimum startup sequence is:

Backend

cd backend
python -m uvicorn app.main:app --reload

AI

cd ai
python -m uvicorn app:app --reload --port 8001

Frontend

python -m http.server 5500

Then open:

http://127.0.0.1:5500/frontend/login.html