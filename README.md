# Medical-Report-Summarizer
A web-based application that automatically processes and summarizes medical reports using advanced Natural Language Processing (NLP) techniques, Named Entity Recognition (NER), and transformer models.
<h3>Overview</h3>
This application extracts key medical information from unstructured medical reports and presents it in a structured, easy-to-read format. It leverages machine learning models to identify patient information, diagnoses, medications, vital signs, and critical flags from medical text.
<h3>Features</h3>

• Smart Medical Text Processing: Uses spaCy NER and transformer models for accurate information extraction.

• Comprehensive Data Extraction.

• Web-based Interface: Clean, responsive UI for easy report input and result viewing

• Real-time Processing: Instant summarization with loading indicators

• Export Functionality: Download summaries for record-keeping



<h3>Quick Setup</h3>

Prerequisites: Python 3.7 or higher, pip package manager

Clone the repo
---------------

```
git clone https://github.com/Insaneon01/Medical-Report-Summarizer.git
cd Medical-Report-Summarizer
```

Install Python Dependencies
----------------------------

```
pip install flask flask-cors transformers torch spacy dataclasses-json
```

Download spaCy Language Model
------------------------------

```
python -m spacy download en_core_web_sm
```

Resources for better execution time(optional)
----------------------------------------------

```
# For GPU support (optional)
pip install torch torchvision torchaudio

# For better performance
pip install accelerate
```

Run the application
--------------------

```
python app.py
```


<h3>Keep Going 👍</h3>