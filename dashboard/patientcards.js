const patients = [
    {
        id: "PT-1024",
        name: "John Smith",
        age: 64,
        gender: "Male",
        heartRate: "115 bpm",
        bloodPressure: "150/95",
        spo2: "92%",
        priority: "Critical",
        ambulanceNum: "AMB-04",
        eta: "5 mins",
        ecgStatus: "Abnormal"
    },
    {
        id: "PT-2051",
        name: "Sarah Johnson",
        age: 42,
        gender: "Female",
        heartRate: "85 bpm",
        bloodPressure: "120/80",
        spo2: "98%",
        priority: "Medium",
        ambulanceNum: "AMB-12",
        eta: "15 mins",
        ecgStatus: "Normal"
    },
    {
        id: "PT-3092",
        name: "Robert Davis",
        age: 78,
        gender: "Male",
        heartRate: "58 bpm",
        bloodPressure: "110/70",
        spo2: "95%",
        priority: "High",
        ambulanceNum: "AMB-02",
        eta: "8 mins",
        ecgStatus: "Checking"
    },
    {
        id: "PT-4103",
        name: "Emily Wilson",
        age: 25,
        gender: "Female",
        heartRate: "72 bpm",
        bloodPressure: "115/75",
        spo2: "99%",
        priority: "Low",
        ambulanceNum: "AMB-08",
        eta: "20 mins",
        ecgStatus: "Normal"
    },
    {
        id: "PT-5120",
        name: "Michael Brown",
        age: 55,
        gender: "Male",
        heartRate: "130 bpm",
        bloodPressure: "160/100",
        spo2: "88%",
        priority: "Critical",
        ambulanceNum: "AMB-01",
        eta: "2 mins",
        ecgStatus: "Abnormal"
    },
    {
        id: "PT-6244",
        name: "Jessica Taylor",
        age: 38,
        gender: "Female",
        heartRate: "95 bpm",
        bloodPressure: "135/85",
        spo2: "96%",
        priority: "High",
        ambulanceNum: "AMB-07",
        eta: "10 mins",
        ecgStatus: "Normal"
    }
];

const patientGrid = document.getElementById('patientGrid');
const searchInput = document.getElementById('searchInput');
const priorityFilter = document.getElementById('priorityFilter');

function getPriorityClass(priority) {
    return priority.toLowerCase();
}

function getEcgStatusClass(status) {
    return `status-${status.toLowerCase()}`;
}

function renderCards(data) {
    patientGrid.innerHTML = '';
    
    if (data.length === 0) {
        patientGrid.innerHTML = '<p class="text-muted">No patients found.</p>';
        return;
    }

    data.forEach(patient => {
        const card = document.createElement('div');
        card.className = `patient-card priority-${getPriorityClass(patient.priority)}`;
        
        card.innerHTML = `
            <div class="card-header">
                <div class="patient-info">
                    <h2>${patient.name}</h2>
                    <span class="patient-id">${patient.id} | ${patient.age} y/o | ${patient.gender}</span>
                </div>
                <span class="badge ${getPriorityClass(patient.priority)}">${patient.priority}</span>
            </div>
            
            <div class="vitals">
                <div class="card-body">
                    <div class="data-item">
                        <span class="data-label">Heart Rate</span>
                        <span class="data-value">${patient.heartRate}</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">SpO₂</span>
                        <span class="data-value">${patient.spo2}</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Blood Pressure</span>
                        <span class="data-value">${patient.bloodPressure}</span>
                    </div>
                </div>
            </div>
            
            <div class="card-body">
                <div class="data-item">
                    <span class="data-label">Ambulance</span>
                    <span class="data-value">${patient.ambulanceNum}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">ETA</span>
                    <span class="data-value">${patient.eta}</span>
                </div>
            </div>
            
            <div class="card-footer">
                <div class="ecg-status">
                    <span class="status-dot ${getEcgStatusClass(patient.ecgStatus)}"></span>
                    <span>ECG: ${patient.ecgStatus}</span>
                </div>
                <button class="btn-view" onclick="alert('Viewing ECG for ${patient.name}')">View ECG</button>
            </div>
        `;
        
        patientGrid.appendChild(card);
    });
}

function filterPatients() {
    const searchTerm = searchInput.value.toLowerCase();
    const priorityTerm = priorityFilter.value;
    
    const filtered = patients.filter(patient => {
        const matchesSearch = patient.name.toLowerCase().includes(searchTerm) || 
                              patient.id.toLowerCase().includes(searchTerm);
        
        const matchesPriority = priorityTerm === 'All' || patient.priority === priorityTerm;
        
        return matchesSearch && matchesPriority;
    });
    
    renderCards(filtered);
}

// Event Listeners
searchInput.addEventListener('input', filterPatients);
priorityFilter.addEventListener('change', filterPatients);

// Initial Render
renderCards(patients);
