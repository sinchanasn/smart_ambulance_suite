Smart Ambulance Suite — Demo Guide

1. Demo Objective

The purpose of the demonstration is to show how Smart Ambulance Suite connects an ambulance team with hospital staff during emergency patient transport.

The demonstration covers:

1. Ambulance staff login
2. Patient registration
3. Vital-sign entry
4. ECG upload
5. AI-assisted ECG analysis
6. Patient data transfer
7. Hospital staff login
8. Hospital patient dashboard
9. Patient and ECG review

---

2. System Preparation

Before starting the demonstration, make sure all required services are running.

Backend

cd backend
python -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

AI Service

cd ai
python -m uvicorn app:app --reload --port 8001

AI service:

http://127.0.0.1:8001

Frontend

From the project root:

python -m http.server 5500

Frontend:

http://127.0.0.1:5500

---

3. Start the Demonstration

Open:

http://127.0.0.1:5500/frontend/login.html

The login page provides two roles:

Ambulance Staff
Doctor / Hospital Staff

---

4. Ambulance Workflow

Step 1 — Ambulance Login

Select:

Ambulance Staff

Enter the configured demonstration credentials.

Username: ambulance
Password: ambulance123

Click:

Login

The ambulance workflow opens.

---

5. Register the Patient

Enter the patient's information.

Example demonstration data:

First Name: John
Last Name: Doe
Age: 54
Gender: Male
Symptoms: Chest pain and shortness of breath

Submit the patient information.

The patient record is sent to the backend.

---

6. Enter Vital Signs

Enter the patient's current vital signs.

Example:

Heart Rate: 102 bpm
Blood Pressure: 145/92 mmHg
SpO2: 94%
Temperature: 37.2 °C

Submit the vital information.

The data is associated with the patient record.

---

7. Upload ECG

Navigate to the ECG section.

Upload a sample ECG image.

The ECG is sent through the application for analysis.

The system sends the ECG to the AI service.

---

8. AI ECG Analysis

The AI service analyzes the ECG image.

The model produces:

Prediction
Confidence

Possible classifications include:

Normal
Possible STEMI
Needs Cardiologist Review

The result is returned to the application.

---

9. Patient Data Transfer

After the patient information, vitals, and ECG have been submitted, the backend stores the information.

The overall data flow is:

Ambulance
    |
    v
Patient Information
    |
    v
Vitals
    |
    v
ECG
    |
    v
AI Analysis
    |
    v
FastAPI Backend
    |
    v
Patient Record

This demonstrates how patient information can be made available to the receiving hospital before arrival.

---

10. Hospital Workflow

Open the login page again:

http://127.0.0.1:5500/frontend/login.html

Select:

Doctor / Hospital Staff

Enter the configured demonstration credentials:

Username: doctor
Password: doctor123

Click:

Login

The hospital dashboard opens.

---

11. Hospital Patient Dashboard

The hospital dashboard retrieves patient information from the backend.

The dashboard displays information such as:

- Patient name
- Patient ID
- Age
- Gender
- Emergency priority
- Medical notes

The hospital staff can search and filter patients.

---

12. Patient Priority

The dashboard provides priority information to help hospital staff identify patients requiring greater attention.

The system can represent priorities such as:

Critical
High
Medium
Low

The dashboard can filter patients according to their priority.

---

13. View Patient

Select:

View Patient

The hospital staff can access additional patient information.

This can include:

- Patient details
- Vital information
- ECG information
- AI ECG result
- Emergency priority

---

14. ECG Review

Open the patient's ECG viewer.

The hospital staff can review the ECG and the associated AI analysis.

The AI result should be treated as an assistive screening result and not as a final medical diagnosis.

---

15. Complete Demonstration Flow

The complete demonstration can be presented as:

                         LOGIN
                           |
              +------------+------------+
              |                         |
              v                         v
       AMBULANCE STAFF          HOSPITAL STAFF
              |                         |
              v                         v
       Patient Registration       Patient Dashboard
              |                         |
              v                         v
            Vitals                Patient Review
              |                         |
              v                         v
          ECG Upload                 ECG Viewer
              |
              v
        AI ECG Analysis
              |
              v
       FastAPI Backend
              |
              v
       Patient Information
              |
              +------------------------>
                         Hospital

---

16. Recommended Judge Presentation

The demonstration should focus on the problem and the complete workflow rather than individual technical files.

Step 1 — Explain the Problem

Explain that emergency departments may not have enough patient information before an ambulance arrives.

Step 2 — Show the Ambulance Side

Demonstrate:

Patient Registration
→ Vitals
→ ECG Upload
→ AI Analysis

Step 3 — Explain the AI

Show the ECG classification and confidence score.

Explain that the model is intended to assist with early screening and does not replace a medical professional.

Step 4 — Switch to Hospital Login

Log in as:

Doctor / Hospital Staff

Step 5 — Show the Patient

Demonstrate that the patient information collected by the ambulance is available on the hospital dashboard.

Step 6 — Show ECG and Priority

Open the patient and demonstrate:

Patient Information
→ Priority
→ ECG
→ AI Result

Step 7 — Conclude

Explain that the system provides a digital communication bridge between ambulance teams and hospitals, allowing the hospital to prepare before the patient's arrival.

---

17. Suggested 3-Minute Demo

If the presentation time is limited, use the following sequence:

0:00 – 0:30
Explain the problem and solution.

0:30 – 1:00
Ambulance login and patient registration.

1:00 – 1:30
Enter vitals and upload ECG.

1:30 – 2:00
Show AI ECG prediction.

2:00 – 2:30
Log in as hospital staff.

2:30 – 3:00
Show patient dashboard, priority and ECG result.

---

18. Demo Checklist

Before the presentation, verify:

- [ ] Backend is running
- [ ] AI service is running
- [ ] Frontend server is running
- [ ] Database is running
- [ ] Login page loads
- [ ] Ambulance role works
- [ ] Doctor role works
- [ ] Patient registration works
- [ ] Vitals submission works
- [ ] ECG upload works
- [ ] AI prediction works
- [ ] Patient appears in hospital dashboard
- [ ] Patient priority is displayed
- [ ] ECG viewer works
- [ ] No sensitive credentials are exposed
- [ ] Internet connection is stable if cloud services are being used

---

19. Backup Plan

For a hackathon demonstration, prepare a backup in case one of the services fails during the presentation.

Keep:

- A sample ECG image ready
- Sample patient information ready
- A previously created patient record if supported
- Screenshots of the AI prediction
- Screenshots of the hospital dashboard
- A copy of the presentation/demo flow

The primary demonstration should still use the live application whenever possible.

---

20. Medical Disclaimer

The AI ECG prediction is an assistive screening feature for the prototype.

It should not be considered a definitive medical diagnosis.

Final clinical decisions must be made by qualified healthcare professionals.