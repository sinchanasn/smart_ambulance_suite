// ============================================================
// BACKEND URL
// ============================================================

const BACKEND_URL = "https://smart-ambulance-suite-backend.onrender.com";


// ============================================================
// DOM ELEMENTS
// ============================================================

const patientGrid =
    document.getElementById("patientGrid");

const searchInput =
    document.getElementById("searchInput");

const priorityFilter =
    document.getElementById("priorityFilter");

let patients = [];


// ============================================================
// LOGIN / ROLE CHECK
// ============================================================

function getLoggedInUser() {

    const sessionUser =
        sessionStorage.getItem("smartAmbulanceUser");

    const localUser =
        localStorage.getItem("smartAmbulanceUser");

    const userData =
        sessionUser || localUser;


    if (!userData) {
        return null;
    }


    try {

        return JSON.parse(userData);

    } catch (error) {

        console.error(
            "Invalid login data:",
            error
        );

        return null;
    }
}


// ============================================================
// CHECK DOCTOR ROLE
// ============================================================

const loggedInUser =
    getLoggedInUser();


if (
    !loggedInUser ||
    loggedInUser.role !== "doctor"
) {

    alert(
        "Access denied. Doctor / Hospital Staff login required."
    );

    // Clear the invalid session
    sessionStorage.removeItem(
        "smartAmbulanceUser"
    );

    localStorage.removeItem(
        "smartAmbulanceUser"
    );

    // Send back to login
    window.location.replace(
        "../frontend/login.html"
    );

} else {

    // ========================================================
    // FETCH PATIENTS FROM BACKEND
    // ========================================================

    async function loadPatients() {

        try {

            console.log(
                "Fetching patients from backend..."
            );


            const response =
                await fetch(
                    `${BACKEND_URL}/patient/`
                );


            if (!response.ok) {

                throw new Error(
                    `Backend returned ${response.status}`
                );

            }


            patients =
                await response.json();


            console.log(
                "Patients received:",
                patients
            );


            renderPatients();


        } catch (error) {

            console.error(
                "Failed to load patients:",
                error
            );


            if (patientGrid) {

                patientGrid.innerHTML = `
                    <div class="error-message">
                        Unable to connect to ambulance backend.
                    </div>
                `;

            }

        }

    }


    // ========================================================
    // RENDER PATIENT CARDS
    // ========================================================

    function renderPatients() {

        const searchText =
            searchInput.value
                .trim()
                .toLowerCase();


        const selectedPriority =
            priorityFilter.value;


        const filteredPatients =
            patients.filter(patient => {

                const fullName =
                    `${patient.first_name} ${patient.last_name}`
                        .toLowerCase();


                const matchesSearch =
                    fullName.includes(searchText) ||
                    String(patient.id)
                        .includes(searchText);


                const matchesPriority =
                    selectedPriority === "All" ||
                    getPriority(
                        patient.triage_priority
                    )
                        .toLowerCase() ===
                    selectedPriority.toLowerCase();


                return (
                    matchesSearch &&
                    matchesPriority
                );

            });


        patientGrid.innerHTML = "";


        if (filteredPatients.length === 0) {

            patientGrid.innerHTML = `
                <div class="empty-message">
                    No patients found.
                </div>
            `;

            return;
        }


        filteredPatients.forEach(patient => {

            const priority =
                getPriority(
                    patient.triage_priority
                );


            const card =
                document.createElement("div");


            card.className =
                `patient-card priority-${priority.toLowerCase()}`;


            card.innerHTML = `

                <div class="patient-card-header">

                    <div>

                        <h3>
                            ${patient.first_name}
                            ${patient.last_name}
                        </h3>

                        <span>
                            Patient ID: ${patient.id}
                        </span>

                    </div>


                    <span class="priority-badge">
                        ${priority}
                    </span>

                </div>


                <div class="patient-info">

                    <p>
                        <strong>Age:</strong>
                        ${patient.age ?? "N/A"}
                    </p>

                    <p>
                        <strong>Gender:</strong>
                        ${patient.gender ?? "N/A"}
                    </p>

                    <p>
                        <strong>Priority:</strong>
                        ${patient.triage_priority ?? "N/A"}
                    </p>

                    <p>
                        <strong>Medical Notes:</strong>
                        ${patient.medical_notes ?? "None"}
                    </p>

                </div>


                <button
                    class="view-patient-btn"
                    onclick="viewPatient(${patient.id})">

                    View Patient

                </button>

            `;


            patientGrid.appendChild(card);

        });

    }


    // ========================================================
    // PRIORITY CONVERSION
    // ========================================================

    function getPriority(priority) {

        if (!priority) {
            return "Medium";
        }


        const value =
            priority.toLowerCase();


        if (
            value.includes("critical") ||
            value.includes("level 1")
        ) {

            return "Critical";

        }


        if (
            value.includes("high") ||
            value.includes("level 2")
        ) {

            return "High";

        }


        if (
            value.includes("medium") ||
            value.includes("level 3")
        ) {

            return "Medium";

        }


        return "Low";
    }


    // ========================================================
    // VIEW PATIENT
    // ========================================================

    function viewPatient(patientId) {

        localStorage.setItem(
            "selectedPatientId",
            patientId
        );


        window.location.href =
            `ecgviewer.html?patient_id=${patientId}`;

    }


    // ========================================================
    // SEARCH + FILTER
    // ========================================================

    searchInput.addEventListener(
        "input",
        renderPatients
    );


    priorityFilter.addEventListener(
        "change",
        renderPatients
    );


    // ========================================================
    // INITIAL LOAD
    // ========================================================

    loadPatients();

}