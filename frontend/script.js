console.log("SCRIPT LOADED");
// --- Patient Registration Logic ---

const API_URL = "http://127.0.0.1:8000";

const patientForm = document.getElementById("patientForm");

if (patientForm) {

    const errorMessage = document.getElementById("errorMessage");
    const patientCard = document.querySelector(".registration-card");
    const saveBtn = document.getElementById("saveBtn");
    const nextBtn = document.getElementById("nextBtn");


    function validatePatientData() {

        const name =
            document.getElementById("patientName").value.trim();

        const age =
            document.getElementById("patientAge").value.trim();

        const gender =
            document.getElementById("patientGender").value;

        const symptoms =
            document.getElementById("symptoms").value.trim();


        errorMessage.style.display = "none";


        if (!name || !age || !gender || !symptoms) {

            showError(
                errorMessage,
                "Please fill in all required fields.",
                patientCard
            );

            return null;
        }


        const nameParts = name.split(" ");


        return {

            first_name: nameParts[0],

            last_name:
                nameParts.length > 1
                    ? nameParts.slice(1).join(" ")
                    : "Unknown",

            age: Number(age),

            gender: gender,

            triage_priority:
                "Level 2 (Urgent)",

            medical_notes:
                symptoms
        };
    }



    async function registerPatient(data) {

        try {

            const response = await fetch(
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


            if (!response.ok) {

                throw new Error(
                    "Patient creation failed"
                );

            }


            const result =
                await response.json();


            console.log(
                "Patient created:",
                result
            );


            localStorage.setItem(
                "patientId",
                result.patient_id
            );


            window.location.href =
                "ecg.html";


        }

        catch (error) {

            console.error(error);

            showError(
                errorMessage,
                "Backend connection failed.",
                patientCard
            );

            nextBtn.disabled = false;

            nextBtn.innerHTML =
                "Continue";

        }

    }



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



    patientForm.addEventListener(
        "submit",
        (e) => {

            e.preventDefault();


            const data =
                validatePatientData();


            if (data) {

                nextBtn.innerHTML =
                    "Registering...";

                nextBtn.disabled =
                    true;


                registerPatient(data);

            }

        }
    );

}

// --- ECG Image Capture Logic ---
// --- ECG Image Capture Logic ---

const ecgCard = document.querySelector(".ecg-card");

if (ecgCard) {

    const uploadInput =
        document.getElementById("uploadInput");

    const submitEcgBtn =
        document.getElementById("submitEcgBtn");

    const ecgErrorMessage =
        document.getElementById("ecgErrorMessage");
    const ecgPreviewContainer =
        document.getElementById("ecgPreviewContainer");

    const ecgPreviewImage =
        document.getElementById("ecgPreviewImage");


    // Show ECG preview after selecting image
    uploadInput.addEventListener("change", () => {

        const file = uploadInput.files[0];

        if (file) {

            const reader = new FileReader();

            reader.onload = function (e) {

                ecgPreviewImage.src = e.target.result;

                ecgPreviewContainer.style.display = "block";

            };

            reader.readAsDataURL(file);
        }

    });



    if (submitEcgBtn) {

        submitEcgBtn.addEventListener(
            "click",
            async () => {

                console.log("Submit ECG clicked");


                if (!uploadInput.files[0]) {

                    showError(
                        ecgErrorMessage,
                        "Please upload an ECG image.",
                        ecgCard
                    );

                    return;
                }



                const patientId =
                    localStorage.getItem("patientId");



                if (!patientId) {

                    showError(
                        ecgErrorMessage,
                        "Patient record not found.",
                        ecgCard
                    );

                    return;
                }



                const formData =
                    new FormData();


                formData.append(
                    "patient_id",
                    patientId
                );


                formData.append(
                    "file",
                    uploadInput.files[0]
                );



                submitEcgBtn.innerHTML =
                    "Analysing ECG...";


                submitEcgBtn.disabled = true;



                try {

                    const response =
                        await fetch(
                            "http://127.0.0.1:8000/ecg/",
                            {
                                method: "POST",
                                body: formData
                            }
                        );



                    const result =
                        await response.json();



                    console.log(
                        "ECG Result:",
                        result
                    );



                    localStorage.setItem(
                        "ecgResult",
                        JSON.stringify(result)
                    );



                    window.location.href =
                        "success.html";


                }


                catch (error) {

                    console.error(error);


                    showError(
                        ecgErrorMessage,
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