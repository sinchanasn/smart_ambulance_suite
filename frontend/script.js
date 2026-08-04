document.addEventListener("DOMContentLoaded", () => {
    // --- Shared functionality ---
    function showError(errorMessageEl, message, cardEl) {
        errorMessageEl.innerHTML = '<i class="fa-solid fa-circle-exclamation" style="margin-right: 5px;"></i>' + message;
        errorMessageEl.style.display = "block";
        
        // Add shake animation
        if (cardEl) {
            cardEl.style.animation = "shake 0.4s ease-in-out";
            
            // Remove animation after it completes to allow it to trigger again
            setTimeout(() => {
                cardEl.style.animation = "";
            }, 400);
        }
    }

    // --- Login Page Logic ---
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        const usernameInput = document.getElementById("username");
        const passwordInput = document.getElementById("password");
        const errorMessage = document.getElementById("errorMessage");
        const loginCard = document.querySelector(".login-card");

        loginForm.addEventListener("submit", (e) => {
            e.preventDefault(); // Prevent form submission
            
            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();
            
            // Reset error message
            errorMessage.style.display = "none";
            errorMessage.textContent = "";
            
            // Validation
            if (!username && !password) {
                showError(errorMessage, "Please enter both username/email and password.", loginCard);
                return;
            }
            
            if (!username) {
                showError(errorMessage, "Please enter your username or email.", loginCard);
                usernameInput.focus();
                return;
            }
            
            if (!password) {
                showError(errorMessage, "Please enter your password.", loginCard);
                passwordInput.focus();
                return;
            }
            
            // Add a small loading effect to the button
            const submitButton = loginForm.querySelector(".login-button");
            submitButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Logging in...';
            submitButton.disabled = true;
            
            setTimeout(() => {
                // Redirect to dashboard
                window.location.href = "dashboard.html";
            }, 800);
        });
    }

    // --- Sign Up Page Logic ---
    const signupForm = document.getElementById("signupForm");
    if (signupForm) {
        const fullnameInput = document.getElementById("fullname");
        const emailInput = document.getElementById("email");
        const phoneInput = document.getElementById("phone");
        const passwordInput = document.getElementById("password");
        const confirmPasswordInput = document.getElementById("confirmPassword");
        const errorMessage = document.getElementById("errorMessage");
        const signupCard = document.querySelector(".login-card");

        signupForm.addEventListener("submit", (e) => {
            e.preventDefault();
            
            const fullname = fullnameInput.value.trim();
            const email = emailInput.value.trim();
            const phone = phoneInput.value.trim();
            const password = passwordInput.value.trim();
            const confirmPassword = confirmPasswordInput.value.trim();
            
            errorMessage.style.display = "none";
            errorMessage.textContent = "";
            
            if (!fullname || !email || !phone || !password || !confirmPassword) {
                showError(errorMessage, "Please fill in all fields.", signupCard);
                return;
            }

            if (password !== confirmPassword) {
                showError(errorMessage, "Passwords do not match.", signupCard);
                confirmPasswordInput.focus();
                return;
            }
            
            const submitButton = signupForm.querySelector(".login-button");
            submitButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...';
            submitButton.disabled = true;
            
            setTimeout(() => {
                // Redirect to login after successful signup
                window.location.href = "login.html";
            }, 800);
        });
    }

    // --- Patient Registration Logic ---
    const patientForm = document.getElementById("patientForm");
    if (patientForm) {
        const errorMessage = document.getElementById("errorMessage");
        const patientCard = document.querySelector(".registration-card");
        
        const clearBtn = document.getElementById("clearBtn");
        const saveBtn = document.getElementById("saveBtn");
        
        clearBtn.addEventListener("click", () => {
            patientForm.reset();
            errorMessage.style.display = "none";
        });
        
        function validatePatientData() {
            const name = document.getElementById("patientName").value.trim();
            const age = document.getElementById("patientAge").value.trim();
            const gender = document.getElementById("patientGender").value;
            const phone = document.getElementById("patientPhone").value.trim();
            const emergency = document.getElementById("emergencyContact").value.trim();
            const heartRate = document.getElementById("heartRate").value.trim();
            const bp = document.getElementById("bloodPressure").value.trim();
            const spo2 = document.getElementById("oxygenSaturation").value.trim();
            const symptoms = document.getElementById("symptoms").value.trim();
            
            errorMessage.style.display = "none";
            
            if (!name || !age || !gender || !emergency || !heartRate || !bp || !spo2 || !symptoms) {
                showError(errorMessage, "Please fill in all required fields (*).", patientCard);
                return null;
            }
            
            const phoneRegex = /^\d{10}$/;
            if (phone && !phoneRegex.test(phone)) {
                showError(errorMessage, "Phone number must be exactly 10 digits.", patientCard);
                return null;
            }
            
            if (!phoneRegex.test(emergency)) {
                showError(errorMessage, "Emergency contact must be exactly 10 digits.", patientCard);
                return null;
            }
            
            // Collect all data
            const patientData = {
                name,
                age,
                gender,
                bloodGroup: document.getElementById("bloodGroup").value,
                phone,
                emergencyContact: emergency,
                height: document.getElementById("patientHeight").value.trim(),
                weight: document.getElementById("patientWeight").value.trim(),
                heartRate,
                bloodPressure: bp,
                oxygenSaturation: spo2,
                bodyTemperature: document.getElementById("bodyTemperature").value.trim(),
                allergies: document.getElementById("allergies").value.trim(),
                symptoms
            };
            
            return patientData;
        }
        
        saveBtn.addEventListener("click", () => {
            const data = validatePatientData();
            if (data) {
                localStorage.setItem("patientData", JSON.stringify(data));
                saveBtn.innerHTML = '<i class="fa-solid fa-check"></i> Saved';
                saveBtn.style.backgroundColor = "#c8e6c9";
                saveBtn.style.color = "#2e7d32";
                setTimeout(() => {
                    saveBtn.innerHTML = 'Save Patient Details';
                    saveBtn.style.backgroundColor = "";
                    saveBtn.style.color = "";
                }, 2000);
            }
        });
        
        patientForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const data = validatePatientData();
            if (data) {
                localStorage.setItem("patientData", JSON.stringify(data));
                const nextBtn = document.getElementById("nextBtn");
                nextBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
                nextBtn.disabled = true;
                
                setTimeout(() => {
                    window.location.href = "ecg.html";
                }, 800);
            }
        });
    }

    // --- ECG Image Capture Logic ---
    const ecgCard = document.querySelector(".ecg-card");
    if (ecgCard) {
        const cameraInput = document.getElementById("cameraInput");
        const uploadInput = document.getElementById("uploadInput");
        const ecgPreviewContainer = document.getElementById("ecgPreviewContainer");
        const ecgPreviewImage = document.getElementById("ecgPreviewImage");
        const ecgInitialActions = document.getElementById("ecgInitialActions");
        const ecgErrorMessage = document.getElementById("ecgErrorMessage");
        const ecgSuccessMessage = document.getElementById("ecgSuccessMessage");
        const submitEcgBtn = document.getElementById("submitEcgBtn");
        
        let currentImage = null;

        function handleImageSelection(event) {
            const file = event.target.files[0];
            ecgErrorMessage.style.display = "none";
            ecgSuccessMessage.style.display = "none";
            
            if (!file) return;

            // Validate file type
            const validTypes = ["image/jpeg", "image/png", "image/jpg"];
            if (!validTypes.includes(file.type)) {
                showError(ecgErrorMessage, "Please select a valid image format (.jpg, .jpeg, .png).", ecgCard);
                // Reset input so it can be re-selected if needed
                event.target.value = "";
                return;
            }

            // Display preview using FileReader
            const reader = new FileReader();
            reader.onload = (e) => {
                currentImage = e.target.result;
                ecgPreviewImage.src = currentImage;
                
                // Show preview area and hide initial buttons
                ecgInitialActions.style.display = "none";
                ecgPreviewContainer.style.display = "block";
            };
            
            reader.readAsDataURL(file);
        }

        // Attach listeners
        if (cameraInput) cameraInput.addEventListener("change", handleImageSelection);
        if (uploadInput) uploadInput.addEventListener("change", handleImageSelection);
        
        if (submitEcgBtn) {
            submitEcgBtn.addEventListener("click", () => {
                if (!currentImage) {
                    showError(ecgErrorMessage, "No image found. Please capture or upload an image.", ecgCard);
                    return;
                }
                
                // Save to localStorage
                localStorage.setItem("ecgImage", currentImage);
                
                // Show success feedback
                ecgSuccessMessage.textContent = "ECG image uploaded successfully. Ready for AI analysis.";
                ecgSuccessMessage.style.display = "block";
                ecgErrorMessage.style.display = "none";
                
                // Disable button and show spinner
                submitEcgBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
                submitEcgBtn.disabled = true;
                
                setTimeout(() => {
                    window.location.href = "success.html";
                }, 1500);
            });
        }
    }
});
