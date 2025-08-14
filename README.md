# Medical-Report-Summarizer
A web-based application that automatically processes and summarizes medical reports using advanced Natural Language Processing (NLP) techniques, Named Entity Recognition (NER), and transformer models.
<h3>Overview</h3>
This application extracts key medical information from unstructured medical reports and presents it in a structured, easy-to-read format. It leverages machine learning models to identify patient information, diagnoses, medications, vital signs, and critical flags from medical text.

✨ Features
Smart Medical Text Processing: Uses spaCy NER and transformer models for accurate information extraction

Comprehensive Data Extraction:

Patient demographics (name, age, gender, MRN)

Chief complaints and presenting problems

Primary and secondary diagnoses

Current medications with dosages

Vital signs and laboratory results

Critical flags and urgent findings

Web-based Interface: Clean, responsive UI for easy report input and result viewing

Real-time Processing: Instant summarization with loading indicators

• Export Functionality: Download summaries for record-keeping

Medical Validation: Built-in validation for medical entities and ICD-10 codes

🛠 Technology Stack
Backend
Python 3.7+

Flask - Web framework

spaCy - Named Entity Recognition and NLP

Transformers (Hugging Face) - BART model for text summarization

Flask-CORS - Cross-origin resource sharing

Frontend
HTML5 - Structure and markup

CSS3 - Modern responsive styling

JavaScript (ES6+) - Interactive functionality and API integration

Machine Learning Models
facebook/bart-large-cnn - Text summarization

en_core_web_sm - spaCy English language model

