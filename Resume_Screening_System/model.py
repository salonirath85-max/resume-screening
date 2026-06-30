import re
from typing import Dict, List, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)
except Exception:
    pass

TECHNICAL_SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "html",
    "css",
    "javascript",
    "react",
    "angular",
    "node.js",
    "django",
    "flask",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "nlp",
    "data science",
    "power bi",
    "excel",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "linux",
    "rest api",
    "mongodb",
    "pandas",
    "numpy",
    "opencv",
    "scikit-learn",
    "communication",
    "leadership",
    "problem solving",
]


def normalize_text(text: str) -> str:
    """Clean and normalize raw text for NLP processing."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_text(text: str) -> List[str]:
    """Tokenize and remove stop words from text."""
    try:
        tokens = word_tokenize(normalize_text(text))
    except LookupError:
        tokens = normalize_text(text).split()

    stop_words = set(stopwords.words("english"))
    return [token for token in tokens if token not in stop_words and len(token) > 2]


def extract_skills(text: str) -> List[str]:
    """Return a list of known technical skills found in the text."""
    cleaned = normalize_text(text)
    found_skills = []
    for skill in TECHNICAL_SKILLS:
        if skill in cleaned:
            found_skills.append(skill)
    return found_skills


def compute_similarity(resume_text: str, job_description: str) -> float:
    """Compute a similarity score using TF-IDF and cosine similarity."""
    vectorizer = TfidfVectorizer(stop_words="english")
    documents = [resume_text, job_description]
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return float(similarity * 100)


def analyze_resume_against_job_description(resume_text: str, job_description: str) -> Dict[str, object]:
    """Analyze a resume against a job description and return structured results."""
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")
    if not job_description or not job_description.strip():
        raise ValueError("Job description is empty.")

    normalized_resume = normalize_text(resume_text)
    normalized_job = normalize_text(job_description)
    tokens_resume = tokenize_text(resume_text)
    tokens_job = tokenize_text(job_description)

    matched_skills = extract_skills(resume_text)
    missing_skills = [skill for skill in TECHNICAL_SKILLS if skill not in normalize_text(resume_text)]

    matching_keywords = sorted(set(tokens_resume).intersection(tokens_job))[:20]
    score = compute_similarity(resume_text, job_description)
    score = round(max(0.0, min(100.0, score)), 2)

    word_count = len(tokens_resume)
    completeness_score = min(100.0, round((word_count / 250) * 100, 2))

    suggestions = [
        "Add missing technical skills from the job description.",
        "Improve project descriptions with measurable results.",
        "Include certifications and training relevant to the role.",
        "Mention achievements with clear metrics.",
        "Improve formatting and structure for better readability.",
        "Add GitHub or LinkedIn profiles if available.",
    ]
    rating_label, rating_text = get_rating_label(score)

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matching_keywords": matching_keywords,
        "suggestions": suggestions,
        "word_count": word_count,
        "completeness_score": completeness_score,
        "extracted_text": resume_text,
        "rating_label": rating_label,
        "rating_text": rating_text,
    }


def get_rating_label(score: float) -> Tuple[str, str]:
    """Return a rating label and explanation based on the score."""
    if score >= 85:
        return "Excellent", "Excellent ⭐⭐⭐⭐⭐"
    if score >= 70:
        return "Good", "Good ⭐⭐⭐⭐"
    if score >= 50:
        return "Average", "Average ⭐⭐⭐"
    return "Needs Improvement", "Needs Improvement ⭐⭐"
