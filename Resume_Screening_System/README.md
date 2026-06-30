# Resume Screening System

A full-stack-style Python application for screening resumes against a job description using NLP, TF-IDF, and cosine similarity.

## Features

- Upload PDF, DOCX, or TXT resumes
- Extract readable text from uploaded resumes
- Preprocess text with NLP techniques
- Compute a match score between 0 and 100
- Identify matching and missing skills
- Provide suggestions for resume improvement
- Show extracted text, word count, and completeness score
- Download an analysis report as a PDF

## Installation

```bash
pip install -r requirements.txt
```

## How to run

```bash
streamlit run app.py
```

## Project Structure

- `app.py` – Streamlit user interface
- `model.py` – NLP preprocessing, similarity scoring, and skill analysis
- `utils.py` – text extraction and PDF report generation
- `sample_data/job_description.txt` – sample job description
- `uploads/` – uploaded resume files
- `resumes/` – local storage for processed resumes

## Screenshots

Placeholder: add screenshots of the Streamlit UI here.

## Future Improvements

- Add a database for storing screening results
- Support job-role-specific skill dictionaries
- Add resume ranking and batch screening
- Improve PDF parsing for complex layouts
