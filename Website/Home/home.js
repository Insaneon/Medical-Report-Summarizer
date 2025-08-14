async function summarizeReport() {
    const reportText = document.getElementById('medicalReport').value.trim();
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    
    // Validation
    if (!reportText) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Please enter a medical report</div>';
        return;
    }
    
    // Show loading indicator
    loadingDiv.style.display = 'block';
    resultDiv.innerHTML = '';
    
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
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${data.error}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <strong>Network Error:</strong> Unable to process request. Please try again.
            </div>
        `;
    } finally {
        // Hide loading indicator
        loadingDiv.style.display = 'none';
    }
}

function displaySummary(summary) {
    const resultDiv = document.getElementById('result');
    
    let html = `
        <div class="summary-container">
            <h3>📋 Medical Report Summary</h3>
            
            ${summary.critical_flags.length > 0 ? `
                <div class="alert alert-danger">
                    <h5>🚨 Critical Flags</h5>
                    ${summary.critical_flags.map(flag => `<div>${flag}</div>`).join('')}
                </div>
            ` : ''}
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header">👤 Patient Information</div>
                        <div class="card-body">
                            ${summary.patient_info.name ? `<p><strong>Name:</strong> ${summary.patient_info.name}</p>` : ''}
                            ${summary.patient_info.age ? `<p><strong>Age:</strong> ${summary.patient_info.age}</p>` : ''}
                            ${summary.patient_info.gender ? `<p><strong>Gender:</strong> ${summary.patient_info.gender}</p>` : ''}
                            ${summary.patient_info.mrn ? `<p><strong>MRN:</strong> ${summary.patient_info.mrn}</p>` : ''}
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-header">📊 Vital Signs</div>
                        <div class="card-body">
                            ${Object.keys(summary.vital_signs).length > 0 ? 
                                Object.entries(summary.vital_signs).map(([key, value]) => 
                                    `<p><strong>${key}:</strong> ${value}</p>`
                                ).join('') : 
                                '<p>No vital signs recorded</p>'
                            }
                        </div>
                    </div>
                </div>
            </div>
            
            ${summary.chief_complaint ? `
                <div class="card mb-3">
                    <div class="card-header">💬 Chief Complaint</div>
                    <div class="card-body">
                        <p>${summary.chief_complaint}</p>
                    </div>
                </div>
            ` : ''}
            
            ${summary.diagnoses.length > 0 ? `
                <div class="card mb-3">
                    <div class="card-header">🩺 Diagnoses</div>
                    <div class="card-body">
                        <ol>
                            ${summary.diagnoses.map(diagnosis => `<li>${diagnosis}</li>`).join('')}
                        </ol>
                    </div>
                </div>
            ` : ''}
            
            ${summary.medications.length > 0 ? `
                <div class="card mb-3">
                    <div class="card-header">💊 Medications</div>
                    <div class="card-body">
                        <ul>
                            ${summary.medications.map(medication => `<li>${medication}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            ` : ''}
            
            ${summary.lab_results.length > 0 ? `
                <div class="card mb-3">
                    <div class="card-header">🧪 Laboratory Results</div>
                    <div class="card-body">
                        <ul>
                            ${summary.lab_results.map(result => `<li>${result}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            ` : ''}
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

// Add download functionality
function downloadSummary() {
    const summaryData = document.getElementById('result').innerText;
    const blob = new Blob([summaryData], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'medical_summary.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
