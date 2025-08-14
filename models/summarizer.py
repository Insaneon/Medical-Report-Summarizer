import re
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import spacy
from transformers import pipeline

@dataclass
class PatientInfo:
    name: str = ""
    age: str = ""
    gender: str = ""
    mrn: str = ""
    dob: str = ""

@dataclass
class MedicalSummary:
    patient_info: PatientInfo
    chief_complaint: str
    diagnosis: List[str]
    medications: List[str]
    vital_signs: Dict[str, str]
    procedures: List[str]
    allergies: List[str]
    lab_results: List[str]
    recommendations: List[str]
    critical_flags: List[str]

class MedicalReportSummarizer:
    def __init__(self):
        # Initialize NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize summarization pipeline
        try:
            self.summarizer = pipeline("summarization", 
                                     model="facebook/bart-large-cnn", 
                                     max_length=150, 
                                     min_length=50)
        except:
            print("Warning: Summarization model not available")
            self.summarizer = None
    
    def validate_medical_entity(self, text: str) -> bool:
        """Validate if text represents a medical condition"""
        
        # ICD-10 pattern matching
        if re.match(r'^[A-Z]\d{2}', text):  # ICD-10 codes start with letter+digits
            return True
        
        # Common medical suffixes
        medical_suffixes = ['-emia', '-itis', '-osis', '-pathy', '-syndrome', '-disease']
        if any(text.lower().endswith(suffix) for suffix in medical_suffixes):
            return True
        
        # Common medical conditions
        medical_conditions = [
            'diabetes', 'hypertension', 'pneumonia', 'coronary', 'acute',
            'chronic', 'syndrome', 'failure', 'disease', 'disorder'
        ]
        if any(condition in text.lower() for condition in medical_conditions):
            return True
            
        return False


    def extract_patient_info(self, text: str) -> PatientInfo:
        """Extract basic patient information"""
        patient = PatientInfo()
        
        # Extract name (usually after "Patient:" or "Name:")
        name_patterns = [
            r"Patient[:\s]+([A-Za-z\s,]+?)(?:\n|Age|DOB|MRN)",
            r"Name[:\s]+([A-Za-z\s,]+?)(?:\n|Age|DOB|MRN)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                patient.name = match.group(1).strip()
                break
        
        # Extract age
        age_match = re.search(r"Age[:\s]+(\d+)", text, re.IGNORECASE)
        if age_match:
            patient.age = age_match.group(1)
        
        # Extract gender
        gender_match = re.search(r"(?:Gender|Sex)[:\s]+(Male|Female|M|F)", text, re.IGNORECASE)
        if gender_match:
            patient.gender = gender_match.group(1)
        
        # Extract MRN
        mrn_match = re.search(r"MRN[:\s]+([A-Z0-9]+)", text, re.IGNORECASE)
        if mrn_match:
            patient.mrn = mrn_match.group(1)
        
        return patient
    
    def extract_chief_complaint(self, text: str) -> str:
        """Extract chief complaint or presenting problem"""
        patterns = [
            r"Chief Complaint[:\s]+(.*?)(?:\n\n|History of Present)",
            r"Presenting Problem[:\s]+(.*?)(?:\n\n|History)",
            r"CC[:\s]+(.*?)(?:\n\n|HPI)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""
    
    def extract_diagnoses(self, text: str) -> List[str]:
        """Extract diagnoses with improved accuracy"""
        diagnoses = []
        
        # Multiple pattern approaches
        patterns = [
            r"(?:Primary\s+)?Diagnosis[es]*[:\s]+(.*?)(?:\n\n|Plan|Medications|Treatment)",
            r"(?:Final\s+)?Impression[:\s]+(.*?)(?:\n\n|Plan|Recommendations)",  
            r"Assessment[:\s]+(.*?)(?:\n\n|Plan|Treatment)",
            r"ICD[:\s]*(?:10|9)[:\s]+(.*?)(?:\n\n|Plan)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                diag_text = match.group(1).strip()
                
                # Clean and filter diagnoses
                cleaned_diagnoses = self.clean_diagnosis_text(diag_text)
                diagnoses.extend(cleaned_diagnoses)
                break
        
        return diagnoses[:10]  # Limit to top 10

    def clean_diagnosis_text(self, text: str) -> List[str]:
        """Clean and filter diagnosis text to remove non-diagnoses"""
        
        # Split by common delimiters
        items = re.split(r'\n\s*\d+\.|\n\s*[-•]|\n(?=\d+\.)', text)
        
        diagnoses = []
        
        # Words to exclude (not actual diagnoses)
        exclude_words = [
            'adjustment', 'management', 'follow-up', 'monitoring', 'continued',
            'stable', 'controlled', 'improved', 'resolved', 'plan', 'care',
            'treatment', 'therapy', 'medication', 'drug', 'well-controlled'
        ]
        
        # Medical condition indicators (actual diagnoses)
        medical_indicators = [
            'syndrome', 'disease', 'disorder', 'condition', 'emia', 'itis', 
            'osis', 'pathy', 'cancer', 'tumor', 'failure', 'infarction',
            'pneumonia', 'diabetes', 'hypertension', 'coronary', 'acute'
        ]
        
        for item in items:
            item = item.strip()
            if not item or len(item) < 5:
                continue
                
            # Remove numbering and bullets
            item = re.sub(r'^\d+\.\s*', '', item)
            item = re.sub(r'^[-•]\s*', '', item)
            
            # Skip if it's just an action/management phrase
            item_lower = item.lower()
            if any(exclude in item_lower for exclude in exclude_words):
                # Check if it also contains medical terms
                if not any(med in item_lower for med in medical_indicators):
                    continue
            
            # Extract the actual diagnosis part (before any management notes)
            diagnosis_part = re.split(r'[-–]\s*(?:stable|controlled|improved|management|adjustment)', item)[0]
            diagnosis_part = diagnosis_part.strip()
            
            if diagnosis_part and len(diagnosis_part) > 3:
                diagnoses.append(diagnosis_part)
        
        return diagnoses

    
    def extract_medications(self, text: str) -> List[str]:
        """Extract current medications"""
        medications = []
        
        patterns = [
            r"Medications?[:\s]+(.*?)(?:\n\n|Allergies|Procedures)",
            r"Current Medications[:\s]+(.*?)(?:\n\n|Allergies|Procedures)",
            r"Rx[:\s]+(.*?)(?:\n\n|Allergies|Procedures)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                med_text = match.group(1)
                # Extract medication names (common patterns)
                med_items = re.findall(r'([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+\d+(?:mg|mcg|g)', med_text)
                medications.extend(med_items)
                
                # Also split by lines for simple lists
                lines = med_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not re.match(r'^\d+\.', line):
                        medications.append(line)
                break
        
        return medications[:15]  # Limit to top 15
    
    def extract_vital_signs(self, text: str) -> Dict[str, str]:
        """Extract vital signs"""
        vitals = {}
        
        # Blood pressure
        bp_match = re.search(r"BP[:\s]+(\d+/\d+)", text, re.IGNORECASE)
        if bp_match:
            vitals["Blood Pressure"] = bp_match.group(1)
        
        # Heart rate
        hr_match = re.search(r"HR[:\s]+(\d+)", text, re.IGNORECASE)
        if hr_match:
            vitals["Heart Rate"] = hr_match.group(1) + " bpm"
        
        # Temperature
        temp_match = re.search(r"Temp[:\s]+(\d+\.?\d*)", text, re.IGNORECASE)
        if temp_match:
            vitals["Temperature"] = temp_match.group(1) + "°F"
        
        # Respiratory rate
        rr_match = re.search(r"RR[:\s]+(\d+)", text, re.IGNORECASE)
        if rr_match:
            vitals["Respiratory Rate"] = rr_match.group(1) + " /min"
        
        # Oxygen saturation
        o2_match = re.search(r"O2 Sat[:\s]+(\d+%)", text, re.IGNORECASE)
        if o2_match:
            vitals["Oxygen Saturation"] = o2_match.group(1)
        
        return vitals
    
    def extract_lab_results(self, text: str) -> List[str]:
        """Extract key laboratory results"""
        labs = []
        
        # Common lab patterns
        lab_patterns = [
            r"(Hemoglobin|Hgb)[:\s]+(\d+\.?\d*)",
            r"(WBC|White Blood Cell)[:\s]+(\d+\.?\d*)",
            r"(Glucose)[:\s]+(\d+)",
            r"(Creatinine)[:\s]+(\d+\.?\d*)",
            r"(BUN)[:\s]+(\d+)",
            r"(Cholesterol)[:\s]+(\d+)"
        ]
        
        for pattern in lab_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                labs.append(f"{match.group(1)}: {match.group(2)}")
        
        return labs
    
    def identify_critical_flags(self, text: str, summary: MedicalSummary) -> List[str]:
        """Identify critical conditions or urgent findings"""
        flags = []
        
        critical_terms = [
            "critical", "urgent", "emergency", "acute", "severe",
            "chest pain", "shortness of breath", "stroke", "heart attack",
            "allergic reaction", "sepsis", "pneumonia"
        ]
        
        text_lower = text.lower()
        for term in critical_terms:
            if term in text_lower:
                flags.append(f"⚠️ {term.title()} mentioned")
        
        # Check vital signs for abnormal values
        if "Blood Pressure" in summary.vital_signs:
            bp = summary.vital_signs["Blood Pressure"]
            if "/" in bp:
                systolic = int(bp.split("/")[0])
                if systolic > 140 or systolic < 90:
                    flags.append("⚠️ Abnormal Blood Pressure")
        
        return flags
    
    def generate_summary_text(self, text: str) -> str:
        """Generate AI-powered summary of the full report"""
        if not self.summarizer:
            return "Summary generation not available"
        
        try:
            # Clean and truncate text for summarizer
            clean_text = re.sub(r'\n+', ' ', text)
            clean_text = clean_text[:1024]  # Limit input length
            
            summary = self.summarizer(clean_text, max_length=100, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            return f"Summary generation error: {str(e)}"
    
    def summarize_report(self, medical_report: str) -> MedicalSummary:
        """Main function to summarize medical report"""
        
        # Extract all components
        patient_info = self.extract_patient_info(medical_report)
        chief_complaint = self.extract_chief_complaint(medical_report)
        diagnoses = self.extract_diagnoses(medical_report)
        medications = self.extract_medications(medical_report)
        vital_signs = self.extract_vital_signs(medical_report)
        lab_results = self.extract_lab_results(medical_report)
        
        # Create summary object
        summary = MedicalSummary(
            patient_info=patient_info,
            chief_complaint=chief_complaint,
            diagnosis=diagnoses,
            medications=medications,
            vital_signs=vital_signs,
            procedures=[],  # Can be extended
            allergies=[],   # Can be extended
            lab_results=lab_results,
            recommendations=[],  # Can be extended
            critical_flags=[]
        )
        
        # Identify critical flags
        summary.critical_flags = self.identify_critical_flags(medical_report, summary)
        
        return summary
    
    def format_summary(self, summary: MedicalSummary) -> str:
        """Format summary for display"""
        
        output = []
        output.append("=" * 60)
        output.append("📋 MEDICAL REPORT SUMMARY")
        output.append("=" * 60)
        
        # Patient Information
        output.append("\n👤 PATIENT INFORMATION")
        output.append("-" * 30)
        if summary.patient_info.name:
            output.append(f"Name: {summary.patient_info.name}")
        if summary.patient_info.age:
            output.append(f"Age: {summary.patient_info.age}")
        if summary.patient_info.gender:
            output.append(f"Gender: {summary.patient_info.gender}")
        if summary.patient_info.mrn:
            output.append(f"MRN: {summary.patient_info.mrn}")
        
        # Critical Flags
        if summary.critical_flags:
            output.append("\n🚨 CRITICAL FLAGS")
            output.append("-" * 30)
            for flag in summary.critical_flags:
                output.append(flag)
        
        # Chief Complaint
        if summary.chief_complaint:
            output.append("\n💬 CHIEF COMPLAINT")
            output.append("-" * 30)
            output.append(summary.chief_complaint)
        
        # Diagnoses
        if summary.diagnosis:
            output.append("\n🩺 DIAGNOSES")
            output.append("-" * 30)
            for i, diag in enumerate(summary.diagnosis, 1):
                output.append(f"{i}. {diag}")
        
        # Vital Signs
        if summary.vital_signs:
            output.append("\n📊 VITAL SIGNS")
            output.append("-" * 30)
            for vital, value in summary.vital_signs.items():
                output.append(f"{vital}: {value}")
        
        # Medications
        if summary.medications:
            output.append("\n💊 MEDICATIONS")
            output.append("-" * 30)
            for i, med in enumerate(summary.medications[:10], 1):
                output.append(f"{i}. {med}")
        
        # Lab Results
        if summary.lab_results:
            output.append("\n🧪 LABORATORY RESULTS")
            output.append("-" * 30)
            for lab in summary.lab_results:
                output.append(f"• {lab}")
        
        output.append("\n" + "=" * 60)
        output.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)

# Usage Example and Testing
def main():
    pass
if __name__ == "__main__":
    main()
