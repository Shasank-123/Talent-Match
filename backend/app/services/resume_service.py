"""
Resume parsing service - extracts text and structured data from PDF, DOCX, and TXT files.
"""
import re
import os
from typing import Dict, List, Tuple
from app.core.config import settings


def cleanResumeText(text: str) -> str:
    """Clean and normalize resume text."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s@.\-,:()/]', ' ', text)
    return text.strip()


def _extract_text_from_pdf(file_path: str) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"


def _extract_text_from_docx(file_path: str) -> str:
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error reading DOCX: {e}"


def _extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading TXT: {e}"


def parseResume(file_path: str, file_type: str) -> Dict:
    """
    Parse resume file and extract raw text + structured data.
    Returns dict with: raw_text, candidate_name, candidate_email, experience_years, education
    """
    ext = file_type.lower()
    if ext == ".pdf":
        raw_text = _extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        raw_text = _extract_text_from_docx(file_path)
    else:
        raw_text = _extract_text_from_txt(file_path)

    cleaned_text = cleanResumeText(raw_text)

    # Extract structured fields
    candidate_email = _extract_email(cleaned_text)
    candidate_name = _extract_name(cleaned_text)
    experience_years = _extract_experience_years(cleaned_text)
    education = _extract_education(cleaned_text)

    return {
        "raw_text": cleaned_text[:settings.MAX_RESUME_LENGTH],
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "experience_years": experience_years,
        "education": education,
    }


def _extract_email(text: str) -> str:
    pattern = r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def _extract_name(text: str) -> str:
    """Simple heuristic: first line with 2 capitalized words."""
    lines = text.split('\n')
    for line in lines[:10]:
        line = line.strip()
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(w[0].isupper() for w in words if w.isalpha()):
                return line
    return "Unknown Candidate"


def _extract_experience_years(text: str) -> int:
    """Extract years of experience from resume text."""
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    # Count year ranges like "2020 - 2024"
    year_pattern = r'\b(20\d{2})\s*[-–]\s*(20\d{2}|present|current)\b'
    matches = re.findall(year_pattern, text, re.IGNORECASE)
    if matches:
        total_years = 0
        import datetime
        current_year = datetime.datetime.now().year
        for start, end in matches:
            end_year = current_year if end.lower() in ['present', 'current'] else int(end)
            total_years += max(0, end_year - int(start))
        return min(total_years, 30)

    return 0


def _extract_education(text: str) -> List[Dict]:
    """Extract education information."""
    education_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", "b.sc", "m.sc",
                          "mba", "bca", "mca", "diploma", "associate", "degree"]
    education = []
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in education_keywords):
            education.append({"degree": line.strip()[:200]})
    return education[:5]  # Max 5 education entries
