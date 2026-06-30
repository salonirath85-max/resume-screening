import os
import re
from pathlib import Path

import streamlit as st

from model import analyze_resume_against_job_description, get_rating_label
from utils import create_analysis_pdf, extract_text_from_file

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESUME_DIR = BASE_DIR / "resumes"
JOB_DESCRIPTION_PATH = BASE_DIR / "sample_data" / "job_description.txt"


def sanitize_filename(name: str) -> str:
    """Create a safe filename for uploaded resumes."""
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return sanitized or "uploaded_resume"


def load_default_job_description() -> str:
    """Load the sample job description from the local data file."""
    try:
        with JOB_DESCRIPTION_PATH.open("r", encoding="utf-8") as handle:
            return handle.read().strip()
    except FileNotFoundError:
        return """We are looking for a data-focused professional with experience in Python, SQL, machine learning, and communication."""


st.set_page_config(page_title="Resume Screening System", page_icon="📄", layout="wide")

st.title("Resume Screening System")
st.caption("Upload a resume and compare it with a job description using NLP and similarity scoring.")

with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        1. Upload a resume in PDF, DOCX, or TXT format.
        2. Paste or edit the job description.
        3. Click Analyze Resume.
        4. Review the match score, skills, suggestions, and report.
        """
    )
    st.markdown("---")
    st.info("Supported file formats: PDF, DOCX, TXT")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESUME_DIR.mkdir(parents=True, exist_ok=True)

resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
job_description = st.text_area(
    "Job Description",
    value=load_default_job_description(),
    height=220,
    help="Edit the job description to match the role you are screening for.",
)

if resume_file is not None:
    st.success(f"Uploaded: {resume_file.name}")

if st.button("Analyze Resume", type="primary"):
    if resume_file is None:
        st.error("Please upload a resume before analyzing.")
    elif not job_description.strip():
        st.error("Please provide a job description before analyzing.")
    else:
        try:
            progress_bar = st.progress(0)
            progress_bar.progress(0.2)

            upload_name = sanitize_filename(resume_file.name)
            save_path = UPLOAD_DIR / upload_name
            with save_path.open("wb") as handle:
                handle.write(resume_file.getbuffer())

            progress_bar.progress(0.4)
            resume_text = extract_text_from_file(str(save_path))
            if not resume_text.strip():
                st.error("The uploaded resume appears to be empty.")
                st.stop()

            progress_bar.progress(0.7)
            analysis = analyze_resume_against_job_description(resume_text, job_description)
            progress_bar.progress(1.0)

            score = analysis["score"]
            rating_label, rating_text = get_rating_label(score)

            st.subheader("Analysis Results")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Match Score", f"{score:.1f}%")
            col2.metric("Resume Rating", rating_label)
            col3.metric("Word Count", analysis["word_count"])
            col4.metric("Completeness", f"{analysis['completeness_score']:.1f}%")

            st.progress(score / 100)
            st.caption(rating_text)

            st.markdown("---")
            st.subheader("Skills Found")
            if analysis["matched_skills"]:
                for skill in analysis["matched_skills"]:
                    st.write(f"✔ {skill}")
            else:
                st.info("No matching skills were detected from the resume.")

            st.markdown("---")
            st.subheader("Missing Skills")
            if analysis["missing_skills"]:
                for skill in analysis["missing_skills"]:
                    st.write(f"✘ {skill}")
            else:
                st.success("The resume appears to cover most of the expected skills.")

            st.markdown("---")
            st.subheader("Matching Keywords")
            keywords = analysis["matching_keywords"]
            if keywords:
                st.write(", ".join(keywords))
            else:
                st.info("No strong keyword matches were found.")

            st.markdown("---")
            st.subheader("Suggestions")
            for suggestion in analysis["suggestions"]:
                st.write(f"• {suggestion}")

            st.markdown("---")
            with st.expander("View Extracted Resume Text"):
                st.text_area("Extracted Text", analysis["extracted_text"], height=250)

            pdf_bytes = create_analysis_pdf(analysis)
            st.download_button(
                "Download analysis report as PDF",
                data=pdf_bytes,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
            )

        except (ValueError, RuntimeError, OSError) as exc:
            st.error(f"Analysis failed: {exc}")
        except Exception as exc:  # pragma: no cover - defensive fallback
            st.error(f"Unexpected error: {exc}")
