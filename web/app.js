async function summarizeReport() {
    const reportText = document.getElementById('medicalReport').value.trim();
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');
    
    // Validation
    if (!reportText) {
        showAlert('Please enter a medical report', 'warning');
        return;
    }
    
    // Show loading indicator
    loadingDiv.style.display = 'block';
    resultDiv.innerHTML = '';
    resultsSection.style.display = 'none';
    
    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                medical_report: reportText
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySummary(data.summary);
            resultsSection.style.display = 'block';
            // Smooth scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            showAlert(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Network Error: Unable to process request. Please try again.', 'error');
    } finally {
        // Hide loading indicator
        loadingDiv.style.display = 'none';
    }
}

function displaySummary(summary) {
    const resultDiv = document.getElementById('result');
    
    let html = `
        <!-- Critical Flags -->
        ${summary.critical_flags && summary.critical_flags.length > 0 ? `
            <div class="summary-card critical-flags">
                <div class="card-header">🚨 Critical Flags</div>
                <div class="card-body">
                    ${summary.critical_flags.map(flag => `<div class="flag-item">${flag}</div>`).join('')}
                </div>
            </div>
        ` : ''}
        
        <!-- Patient Information -->
        <div class="summary-row">
            <div class="summary-card">
                <div class="card-header">👤 Patient Information</div>
                <div class="card-body">
                    ${summary.patient_info.name ? `<p><strong>Name:</strong> ${summary.patient_info.name}</p>` : ''}
                    ${summary.patient_info.age ? `<p><strong>Age:</strong> ${summary.patient_info.age}</p>` : ''}
                    ${summary.patient_info.gender ? `<p><strong>Gender:</strong> ${summary.patient_info.gender}</p>` : ''}
                    ${summary.patient_info.mrn ? `<p><strong>MRN:</strong> ${summary.patient_info.mrn}</p>` : ''}
                    ${!summary.patient_info.name && !summary.patient_info.age ? '<p>No patient information available</p>' : ''}
                </div>
            </div>
            
            <div class="summary-card">
                <div class="card-header">📊 Vital Signs</div>
                <div class="card-body">
                    ${Object.keys(summary.vital_signs || {}).length > 0 ? 
                        Object.entries(summary.vital_signs).map(([key, value]) => 
                            `<p><strong>${key}:</strong> ${value}</p>`
                        ).join('') : 
                        '<p>No vital signs recorded</p>'
                    }
                </div>
            </div>
        </div>
        
        <!-- Chief Complaint -->
        ${summary.chief_complaint ? `
            <div class="summary-card">
                <div class="card-header">💬 Chief Complaint</div>
                <div class="card-body">
                    <p>${summary.chief_complaint}</p>
                </div>
            </div>
        ` : ''}
        
        <!-- Diagnoses -->
        ${summary.diagnoses && summary.diagnoses.length > 0 ? `
            <div class="summary-card">
                <div class="card-header">🩺 Diagnoses</div>
                <div class="card-body">
                    <ol>
                        ${summary.diagnoses.map(diagnosis => `<li>${diagnosis}</li>`).join('')}
                    </ol>
                </div>
            </div>
        ` : ''}
        
        <!-- Medications -->
        ${summary.medications && summary.medications.length > 0 ? `
            <div class="summary-card">
                <div class="card-header">💊 Medications</div>
                <div class="card-body">
                    <ul>
                        ${summary.medications.map(medication => `<li>${medication}</li>`).join('')}
                    </ul>
                </div>
            </div>
        ` : ''}
        
        <!-- Laboratory Results -->
        ${summary.lab_results && summary.lab_results.length > 0 ? `
            <div class="summary-card">
                <div class="card-header">🧪 Laboratory Results</div>
                <div class="card-body">
                    <ul>
                        ${summary.lab_results.map(result => `<li>${result}</li>`).join('')}
                    </ul>
                </div>
            </div>
        ` : ''}
    `;
    
    resultDiv.innerHTML = html;
}

function clearInput() {
    document.getElementById('medicalReport').value = '';
    document.getElementById('result').innerHTML = '';
    document.getElementById('results-section').style.display = 'none';
}

function newReport() {
    clearInput();
    // Scroll back to input section
    document.querySelector('.content').scrollIntoView({ behavior: 'smooth' });
}

function downloadSummary() {
    const summaryContent = document.getElementById('result').innerText;
    const blob = new Blob([summaryContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medical_summary_${new Date().toISOString().slice(0,10)}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    // Insert at the top of main content
    const main = document.querySelector('main');
    main.insertBefore(alertDiv, main.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Add sample medical report for testing
function loadSampleReport() {
    const sampleReport = `
Patient: John Smith
Age: 45
Gender: Male
MRN: MR123456

Chief Complaint: Chest pain and shortness of breath for 2 days

History of Present Illness: 
45-year-old male presents with acute onset chest pain and dyspnea. 
Pain is substernal, 7/10 severity, radiating to left arm.

Vital Signs:
BP: 150/95
HR: 110
Temp: 98.6
RR: 24
O2 Sat: 92%

Assessment and Plan:
1. Acute coronary syndrome - Rule out myocardial infarction
2. Hypertension - poorly controlled
3. Dyslipidemia

Medications:
1. Aspirin 81mg daily
2. Metoprolol 50mg twice daily
3. Atorvastatin 40mg daily
4. Lisinopril 10mg daily

Laboratory Results:
Hemoglobin: 12.5
WBC: 8.2
Glucose: 145
Creatinine: 1.2
    `;
    
    document.getElementById('medicalReport').value = sampleReport.trim();
}
