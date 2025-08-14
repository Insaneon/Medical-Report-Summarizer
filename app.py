from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import traceback
from models.summarizer import MedicalReportSummarizer

# Initialize the medical summarizer
summarizer = MedicalReportSummarizer()

app = Flask(__name__, static_folder='web', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/api/summarize', methods=['POST'])
def summarize_report():
    """API endpoint to process medical report and return summary"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'medical_report' not in data:
            return jsonify({
                'success': False,
                'error': 'No medical report provided'
            }), 400
        
        # Get the medical report text
        medical_text = data['medical_report'].strip()
        
        if not medical_text:
            return jsonify({
                'success': False,
                'error': 'Empty medical report'
            }), 400
        
        # Process the medical report
        summary = summarizer.summarize_report(medical_text)
        
        # Convert summary to JSON-serializable format
        result = {
            'patient_info': {
                'name': summary.patient_info.name,
                'age': summary.patient_info.age,
                'gender': summary.patient_info.gender,
                'mrn': summary.patient_info.mrn
            },
            'chief_complaint': summary.chief_complaint,
            'diagnoses': summary.diagnosis,
            'medications': summary.medications,
            'vital_signs': summary.vital_signs,
            'lab_results': summary.lab_results,
            'critical_flags': summary.critical_flags,
            'formatted_summary': summarizer.format_summary(summary)
        }
        
        return jsonify({
            'success': True,
            'summary': result
        })
    
    except Exception as e:
        # Log the full error for debugging
        print(f"Error processing request: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Processing error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Medical Report Summarizer API is running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
