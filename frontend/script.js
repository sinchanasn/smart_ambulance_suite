console.log("SCRIPT LOADED");

// ============================================================
// ROLE-BASED LOGIN / SESSION
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
        console.error("Invalid login data.");
        return null;
    }
}


// ============================================================
// CURRENT PAGE
// ============================================================

const currentPage =
    window.location.pathname.toLowerCase();


// ============================================================
// PROTECT AMBULANCE PAGES
// ============================================================

const ambulancePages = [
    "patient.html",
    "vitalsinput.html",
    "ecg.html",
    "gps.html"
];


const isAmbulancePage =
    ambulancePages.some(page =>
        currentPage.endsWith(page)
    );


if (isAmbulancePage) {

    const user = getLoggedInUser();

    if (!user || user.role !== "ambulance") {

        alert(
            "Access denied. Please login as Ambulance Staff."
        );

        window.location.href = "login.html";
    }
}


// ============================================================
// LOGOUT FUNCTION
// ============================================================

function logoutUser() {

    sessionStorage.removeItem(
        "smartAmbulanceUser"
    );

    localStorage.removeItem(
        "smartAmbulanceUser"
    );

    window.location.href = "login.html";
}


// ============================================================
// BACKEND API
// ============================================================

const API_URL = "https://smart-ambulance-suite-backend.onrender.com";

// ============================================================
// GLOBAL ECG FILE
// ============================================================

// Both cameraInput and uploadInput can provide the ECG.
// We keep whichever file the user selected here.
let selectedEcgFile = null;


// ============================================================
// COMMON ERROR HELPER
// ============================================================

function showError(element, message, card = null) {
    if (!element) {
        console.error(message);
        return;
    }

    element.textContent = message;
    element.style.display = "block";

    if (card) {
        card.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }
}


// ============================================================
// PATIENT REGISTRATION
// ============================================================

const patientForm = document.getElementById("patientForm");

if (patientForm) {

    const errorMessage =
        document.getElementById("errorMessage");

    const patientCard =
        document.querySelector(".registration-card");

    const saveBtn =
        document.getElementById("saveBtn");

    const nextBtn =
        document.getElementById("nextBtn");


    // --------------------------------------------------------
    // VALIDATE PATIENT DATA
    // --------------------------------------------------------

    function validatePatientData() {

        const nameElement =
            document.getElementById("patientName");

        const ageElement =
            document.getElementById("patientAge");

        const genderElement =
            document.getElementById("patientGender");

        const symptomsElement =
            document.getElementById("symptoms");


        const name =
            nameElement
                ? nameElement.value.trim()
                : "";

        const age =
            ageElement
                ? ageElement.value.trim()
                : "";

        const gender =
            genderElement
                ? genderElement.value
                : "";

        const symptoms =
            symptomsElement
                ? symptomsElement.value.trim()
                : "";


        if (errorMessage) {
            errorMessage.style.display = "none";
        }


        if (!name || !age || !gender || !symptoms) {

            showError(
                errorMessage,
                "Please fill in all required fields.",
                patientCard
            );

            return null;
        }


        const nameParts =
            name.split(/\s+/);


        return {

            first_name:
                nameParts[0],

            last_name:
                nameParts.length > 1
                    ? nameParts.slice(1).join(" ")
                    : "Unknown",

            age:
                Number(age),

            gender:
                gender,

            triage_priority:
                "Level 2 (Urgent)",

            medical_notes:
                symptoms
        };
    }


    // --------------------------------------------------------
    // REGISTER PATIENT + SAVE VITALS
    // --------------------------------------------------------

    async function registerPatient(data) {

        try {

            // =================================================
            // STEP 1: CREATE PATIENT
            // =================================================

            console.log("Creating patient...");


            const patientResponse =
                await fetch(
                    `${API_URL}/patient/`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(data)
                    }
                );


            if (!patientResponse.ok) {

                const errorText =
                    await patientResponse.text();

                console.error(
                    "Patient creation failed:",
                    errorText
                );

                throw new Error(
                    `Patient creation failed: ${patientResponse.status}`
                );
            }


            const patientResult =
                await patientResponse.json();


            console.log(
                "Patient created:",
                patientResult
            );


            // =================================================
            // STEP 2: GET PATIENT ID
            // =================================================

            const patientId =
                patientResult.id ??
                patientResult.patient_id;


            if (!patientId) {

                console.error(
                    "No patient ID received:",
                    patientResult
                );

                throw new Error(
                    "Patient ID was not returned by backend"
                );
            }


            console.log(
                "Patient ID:",
                patientId
            );


            localStorage.setItem(
                "patientId",
                String(patientId)
            );


            // =================================================
            // STEP 3: COLLECT VITALS
            // =================================================

            const heartRateElement =
                document.getElementById("heartRate");

            const bloodPressureElement =
                document.getElementById("bloodPressure");

            const spo2Element =
                document.getElementById("oxygenSaturation");

            const temperatureElement =
                document.getElementById("bodyTemperature");

            const respiratoryRateElement =
                document.getElementById("respiratoryRate");


            const heartRate =
                heartRateElement
                    ? heartRateElement.value.trim()
                    : "";

            const bloodPressure =
                bloodPressureElement
                    ? bloodPressureElement.value.trim()
                    : "";

            const spo2 =
                spo2Element
                    ? spo2Element.value.trim()
                    : "";

            const temperature =
                temperatureElement
                    ? temperatureElement.value.trim()
                    : "";

            const respiratoryRate =
                respiratoryRateElement
                    ? respiratoryRateElement.value.trim()
                    : "";


            const vitalsData = {

                patient_id:
                    Number(patientId),

                heart_rate:
                    heartRate
                        ? Number(heartRate)
                        : null,

                blood_pressure:
                    bloodPressure || null,

                spo2:
                    spo2
                        ? Number(spo2)
                        : null,

                temperature:
                    temperature
                        ? Number(temperature)
                        : null,

                respiratory_rate:
                    respiratoryRate
                        ? Number(respiratoryRate)
                        : null
            };


            console.log(
                "Vitals to be saved:",
                vitalsData
            );


            // =================================================
            // STEP 4: SAVE VITALS
            // =================================================

            const vitalsResponse =
                await fetch(
                    `${API_URL}/vitals/`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(vitalsData)
                    }
                );


            if (!vitalsResponse.ok) {

                const errorText =
                    await vitalsResponse.text();

                console.error(
                    "Vitals save failed:",
                    errorText
                );

                throw new Error(
                    `Vitals could not be saved: ${vitalsResponse.status}`
                );
            }


            const vitalsResult =
                await vitalsResponse.json();


            console.log(
                "Vitals saved:",
                vitalsResult
            );


            // =================================================
            // STEP 5: SAVE LOCALLY
            // =================================================

            localStorage.setItem(
                "patientData",
                JSON.stringify(data)
            );


            localStorage.setItem(
                "vitalsData",
                JSON.stringify(vitalsData)
            );


            // =================================================
            // STEP 6: GO TO ECG PAGE
            // =================================================

            console.log(
                "Patient and vitals saved successfully."
            );


            window.location.href =
                "ecg.html";

        }


        catch (error) {

            console.error(
                "Registration error:",
                error
            );


            showError(
                errorMessage,
                error.message ||
                "Backend connection failed.",
                patientCard
            );


            if (nextBtn) {

                nextBtn.disabled =
                    false;

                nextBtn.innerHTML =
                    "Continue";
            }
        }
    }


    // --------------------------------------------------------
    // SAVE BUTTON
    // --------------------------------------------------------

    if (saveBtn) {

        saveBtn.addEventListener(
            "click",
            () => {

                const data =
                    validatePatientData();


                if (data) {

                    localStorage.setItem(
                        "patientData",
                        JSON.stringify(data)
                    );


                    saveBtn.innerHTML =
                        "✓ Saved";
                }
            }
        );
    }


    // --------------------------------------------------------
    // FORM SUBMIT
    // --------------------------------------------------------

    patientForm.addEventListener(
        "submit",
        (e) => {

            e.preventDefault();


            const data =
                validatePatientData();


            if (data) {

                if (nextBtn) {

                    nextBtn.innerHTML =
                        "Registering...";

                    nextBtn.disabled =
                        true;
                }


                registerPatient(data);
            }
        }
    );
}


// ============================================================
// ECG IMAGE CAPTURE + AI ANALYSIS
// ============================================================

const ecgCard =
    document.querySelector(".ecg-card");

if (ecgCard) {

    const cameraInput =
        document.getElementById("cameraInput");

    const uploadInput =
        document.getElementById("uploadInput");

    const submitEcgBtn =
        document.getElementById("submitEcgBtn");

    const retakeBtn =
        document.getElementById("retakeBtn");

    const uploadAnotherBtn =
        document.getElementById("uploadAnotherBtn");

    const ecgErrorMessage =
        document.getElementById("ecgErrorMessage");

    const ecgSuccessMessage =
        document.getElementById("ecgSuccessMessage");

    const ecgPreviewContainer =
        document.getElementById("ecgPreviewContainer");

    const ecgPreviewImage =
        document.getElementById("ecgPreviewImage");


    // --------------------------------------------------------
    // HANDLE SELECTED ECG FILE
    // --------------------------------------------------------

    function handleEcgFile(file) {

        if (!file) {
            return;
        }

        console.log(
            "ECG file selected:",
            file.name,
            file.type,
            file.size
        );


        // --------------------------------------------
        // VALIDATE FILE TYPE
        // --------------------------------------------

        const allowedTypes = [
            "image/jpeg",
            "image/jpg",
            "image/png"
        ];

        const allowedExtensions = [
            ".jpg",
            ".jpeg",
            ".png"
        ];

        const filename =
            file.name.toLowerCase();

        const validType =
            allowedTypes.includes(file.type);

        const validExtension =
            allowedExtensions.some(
                ext => filename.endsWith(ext)
            );


        if (!validType && !validExtension) {

            selectedEcgFile = null;

            showError(
                ecgErrorMessage,
                "Invalid file. Please select a PNG, JPG, or JPEG ECG image.",
                ecgCard
            );

            return;
        }


        // --------------------------------------------
        // SAVE SELECTED ECG FILE
        // --------------------------------------------

        selectedEcgFile = file;


        // --------------------------------------------
        // CLEAR OLD ERROR
        // --------------------------------------------

        if (ecgErrorMessage) {

            ecgErrorMessage.textContent = "";

            ecgErrorMessage.style.display = "none";
        }


        // --------------------------------------------
        // READ + SAVE ECG IMAGE
        // --------------------------------------------

        const reader = new FileReader();


        reader.onload = function (e) {

            // Save image so ecg-result.html
            // can display it later
            localStorage.setItem(
                "ecgImagePreview",
                e.target.result
            );


            // Show preview on ECG page
            if (ecgPreviewImage) {

                ecgPreviewImage.src =
                    e.target.result;
            }


            if (ecgPreviewContainer) {

                ecgPreviewContainer.style.display =
                    "block";
            }
        };


        reader.onerror = function () {

            showError(
                ecgErrorMessage,
                "Could not preview the ECG image.",
                ecgCard
            );
        };


        reader.readAsDataURL(file);
    }


    // --------------------------------------------------------
    // CAMERA INPUT
    // --------------------------------------------------------

    if (cameraInput) {

        cameraInput.addEventListener(
            "change",
            () => {

                const file =
                    cameraInput.files &&
                    cameraInput.files[0];


                handleEcgFile(file);
            }
        );
    }


    // --------------------------------------------------------
    // UPLOAD INPUT
    // --------------------------------------------------------

    if (uploadInput) {

        uploadInput.addEventListener(
            "change",
            () => {

                const file =
                    uploadInput.files &&
                    uploadInput.files[0];


                handleEcgFile(file);
            }
        );
    }


    // --------------------------------------------------------
    // RETAKE IMAGE
    // --------------------------------------------------------

    if (retakeBtn) {

        retakeBtn.addEventListener(
            "click",
            () => {

                if (cameraInput) {

                    cameraInput.value =
                        "";

                    cameraInput.click();
                }
            }
        );
    }


    // --------------------------------------------------------
    // UPLOAD ANOTHER IMAGE
    // --------------------------------------------------------

    if (uploadAnotherBtn) {

        uploadAnotherBtn.addEventListener(
            "click",
            () => {

                if (uploadInput) {

                    uploadInput.value =
                        "";

                    uploadInput.click();
                }
            }
        );
    }


    // --------------------------------------------------------
    // SUBMIT ECG
    // --------------------------------------------------------

    if (submitEcgBtn) {

        submitEcgBtn.addEventListener(
            "click",
            async () => {

                console.log(
                    "Submit ECG clicked"
                );


                // --------------------------------------------
                // CHECK IMAGE
                // --------------------------------------------

                if (!selectedEcgFile) {

                    showError(
                        ecgErrorMessage,
                        "Please capture or upload an ECG image first.",
                        ecgCard
                    );

                    return;
                }


                // --------------------------------------------
                // GET PATIENT ID
                // --------------------------------------------

                const patientId =
                    localStorage.getItem(
                        "patientId"
                    );


                if (!patientId) {

                    showError(
                        ecgErrorMessage,
                        "Patient record not found. Please register the patient again.",
                        ecgCard
                    );

                    return;
                }


                console.log(
                    "Uploading ECG for patient:",
                    patientId
                );


                // --------------------------------------------
                // CREATE FORM DATA
                // --------------------------------------------

                const formData =
                    new FormData();


                formData.append(
                    "patient_id",
                    patientId
                );


                formData.append(
                    "file",
                    selectedEcgFile,
                    selectedEcgFile.name
                );


                // --------------------------------------------
                // BUTTON STATE
                // --------------------------------------------

                submitEcgBtn.innerHTML =
                    "Analysing ECG...";

                submitEcgBtn.disabled =
                    true;


                if (ecgErrorMessage) {

                    ecgErrorMessage.style.display =
                        "none";
                }


                try {

                    // ========================================
                    // SEND ECG TO BACKEND
                    // ========================================

                    console.log(
                        "Sending ECG to:",
                        `${API_URL}/ecg/`
                    );


                    const response =
                        await fetch(
                            `${API_URL}/ecg/`,
                            {
                                method: "POST",

                                body:
                                    formData
                            }
                        );


                    // ========================================
                    // READ RESPONSE SAFELY
                    // ========================================

                    const responseText =
                        await response.text();


                    let result;


                    try {

                        result =
                            JSON.parse(responseText);

                    }
                    catch {

                        console.error(
                            "Backend returned non-JSON response:",
                            responseText
                        );

                        throw new Error(
                            `Backend returned an invalid response (${response.status})`
                        );
                    }


                    console.log(
                        "ECG Result:",
                        result
                    );


                    // ========================================
                    // HANDLE BACKEND ERROR
                    // ========================================

                    if (!response.ok) {

                        throw new Error(
                            result.detail ||
                            result.message ||
                            `ECG upload failed (${response.status})`
                        );
                    }


                    // ========================================
                    // SAVE COMPLETE ECG RESULT
                    // ========================================

                    localStorage.setItem(
                        "ecgResult",
                        JSON.stringify(result)
                    );


                    console.log(
                        "ECG saved successfully."
                    );


                    console.log(
                        "ECG ID:",
                        result.ecg_id
                    );


                    console.log(
                        "AI prediction:",
                        result.prediction
                    );


                    console.log(
                        "AI confidence:",
                        result.confidence
                    );


                    console.log(
                        "ECG status:",
                        result.status
                    );


                    // ========================================
                    // SUCCESS MESSAGE
                    // ========================================

                    if (ecgSuccessMessage) {

                        ecgSuccessMessage.textContent =
                            result.prediction
                                ? "ECG analysed successfully."
                                : "ECG uploaded successfully. AI result pending.";

                        ecgSuccessMessage.style.display =
                            "block";
                    }


                    // ========================================
                    // GO TO SUCCESS PAGE
                    // ========================================

                    window.location.href =
                        "ecg-result.html";

                }


                catch (error) {

                    console.error(
                        "ECG upload error:",
                        error
                    );


                    showError(
                        ecgErrorMessage,
                        error.message ||
                        "ECG upload failed.",
                        ecgCard
                    );


                    submitEcgBtn.disabled =
                        false;


                    submitEcgBtn.innerHTML =
                        "Submit ECG";
                }
            }
        );
    }
}


// ============================================================
// SUCCESS PAGE
// ============================================================

const successPage =
    document.getElementById("ecgSuccessMessage");

if (successPage) {

    const storedResult =
        localStorage.getItem(
            "ecgResult"
        );


    if (storedResult) {

        try {

            const result =
                JSON.parse(
                    storedResult
                );


            console.log(
                "Stored ECG result:",
                result
            );

        }
        catch (error) {

            console.error(
                "Could not read stored ECG result:",
                error
            );
        }
    }
}


// ============================================================
// UTILITY: FORMAT AI PREDICTION
// ============================================================

function formatPrediction(value) {

    if (!value) {
        return "Not available";
    }


    return String(value)
        .replaceAll("_", " ")
        .replace(/\b\w/g, char =>
            char.toUpperCase()
        );
}


// ============================================================
// UTILITY: FORMAT CONFIDENCE
// ============================================================
//
// Your AI may return:
//     0.94  -> 94%
//     94    -> 94%
//     0.87  -> 87%
//
// This keeps the frontend compatible with both.
// ============================================================

function formatConfidence(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "N/A";
    }


    const numericValue =
        Number(value);


    if (Number.isNaN(numericValue)) {

        return "N/A";
    }


    let percentage;


    if (numericValue <= 1) {

        percentage =
            numericValue * 100;

    } else {

        percentage =
            numericValue;
    }


    percentage =
        Math.max(
            0,
            Math.min(
                100,
                percentage
            )
        );


    return `${percentage.toFixed(2)}%`;
}