"""
ML Service - Handles semantic similarity, skill extraction, and candidate ranking.
Uses sentence-transformers for local embeddings (no external API needed).
"""
import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity

# Lazy-load the model to speed up startup
_model = None

COMMON_SKILLS = [
    "python", "javascript", "java", "c++", "c#", "typescript", "go", "rust", "ruby", "php",
    "react", "vue", "angular", "next.js", "node.js", "express", "django", "fastapi", "flask",
    "spring", "laravel", "rails", "asp.net",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "sqlite",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "machine learning", "deep learning", "nlp", "computer vision", "data science",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "spark",
    "git", "ci/cd", "jenkins", "github actions", "agile", "scrum", "jira",
    "html", "css", "rest api", "graphql", "microservices", "system design",
    "linux", "bash", "powershell", "data structures", "algorithms",
    "excel", "power bi", "tableau", "looker", "airflow", "kafka",
    "communication", "leadership", "teamwork", "problem solving", "critical thinking",
    "project management", "time management", "collaboration",
]


def _get_model():
    """Lazy-load sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model = None
    return _model


def generateEmbedding(text: str) -> Optional[np.ndarray]:
    """Generate semantic embedding for text."""
    model = _get_model()
    if model is None:
        return None
    try:
        embedding = model.encode([text[:5000]])[0]
        return embedding
    except Exception:
        return None


def calculateSimilarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity between two texts."""
    emb1 = generateEmbedding(text1)
    emb2 = generateEmbedding(text2)
    if emb1 is None or emb2 is None:
        return _fallback_similarity(text1, text2)
    similarity = cosine_similarity([emb1], [emb2])[0][0]
    return float(np.clip(similarity, 0.0, 1.0))


def _fallback_similarity(text1: str, text2: str) -> float:
    """Keyword-overlap based fallback similarity."""
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


def extractSkills(text: str) -> List[str]:
    """Extract skills from text by matching against known skill list."""
    text_lower = text.lower()
    found_skills = []
    for skill in COMMON_SKILLS:
        # Match whole word/phrase
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return list(set(found_skills))


def calculateSkillMatchScore(resume_skills: List[str], job_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Calculate skill match score.
    Returns: (score, matching_skills, skill_gap)
    """
    if not job_skills:
        return 1.0, resume_skills, []

    resume_skills_lower = [s.lower() for s in resume_skills]
    job_skills_lower = [s.lower() for s in job_skills]

    matching = [s for s in job_skills_lower if s in resume_skills_lower]
    gap = [s for s in job_skills_lower if s not in resume_skills_lower]

    score = len(matching) / len(job_skills_lower) if job_skills_lower else 1.0
    return float(score), matching, gap


def calculateExperienceScore(candidate_years: int, required_years: int) -> float:
    """Score candidate experience vs required."""
    if required_years == 0:
        return 1.0
    ratio = candidate_years / required_years
    if ratio >= 1.0:
        return 1.0
    elif ratio >= 0.7:
        return 0.75
    elif ratio >= 0.5:
        return 0.5
    else:
        return ratio * 0.5


def calculateOverallScore(
    similarity_score: float,
    skill_match_score: float,
    experience_score: float,
    weights: Dict[str, float] = None
) -> float:
    """Calculate weighted overall score."""
    if weights is None:
        weights = {"similarity": 0.40, "skill_match": 0.45, "experience": 0.15}
    overall = (
        similarity_score * weights["similarity"] +
        skill_match_score * weights["skill_match"] +
        experience_score * weights["experience"]
    )
    return float(np.clip(overall, 0.0, 1.0))


def generateExplanation(
    candidate_name: str,
    job_title: str,
    overall_score: float,
    matching_skills: List[str],
    skill_gap: List[str],
    experience_years: int
) -> str:
    """Generate a human-readable explanation for the ranking."""
    score_pct = int(overall_score * 100)
    level = "Strong" if score_pct >= 75 else "Moderate" if score_pct >= 50 else "Weak"
    match_str = ", ".join(matching_skills[:5]) if matching_skills else "none detected"
    gap_str = ", ".join(skill_gap[:5]) if skill_gap else "none"
    return (
        f"{level} match ({score_pct}%) for {job_title}. "
        f"Candidate has {experience_years} year(s) of experience. "
        f"Matching skills: {match_str}. "
        f"Missing skills: {gap_str}."
    )


def rankCandidates(candidates_data: List[Dict]) -> List[Dict]:
    """Sort candidates by overall_score descending and assign rank positions."""
    ranked = sorted(candidates_data, key=lambda x: x["overall_score"], reverse=True)
    for i, candidate in enumerate(ranked):
        candidate["rank_position"] = i + 1
    return ranked


def generateInterviewQuestions(
    resume_skills: List[str],
    job_skills: List[str],
    skill_gap: List[str],
    job_title: str
) -> List[Dict]:
    """Generate targeted interview questions based on job and candidate profile."""
    questions = []

    # Behavioral questions
    questions.append({
        "question": f"Tell me about a challenging project you worked on as a {job_title}. How did you handle it?",
        "category": "behavioral",
        "difficulty": "medium"
    })
    questions.append({
        "question": "Describe a time you had to learn a new technology under tight deadlines. What was your approach?",
        "category": "behavioral",
        "difficulty": "medium"
    })
    questions.append({
        "question": "How do you prioritize tasks when managing multiple projects simultaneously?",
        "category": "behavioral",
        "difficulty": "easy"
    })

    # Technical questions on matched skills
    for skill in matching_skills_q(resume_skills, job_skills)[:3]:
        questions.append({
            "question": f"Can you explain your experience with {skill}? Give a concrete example of how you used it.",
            "category": "technical",
            "difficulty": "medium"
        })

    # Gap-filling questions
    for skill in skill_gap[:2]:
        questions.append({
            "question": f"This role requires experience with {skill}. What is your familiarity with it and how quickly could you get up to speed?",
            "category": "skill_gap",
            "difficulty": "hard"
        })

    # Role-specific
    questions.append({
        "question": f"Where do you see the {job_title} role evolving in the next 2–3 years, and how do you plan to stay current?",
        "category": "strategic",
        "difficulty": "hard"
    })

    return questions


def matching_skills_q(resume_skills: List[str], job_skills: List[str]) -> List[str]:
    """Helper to find common skills for question generation."""
    r = [s.lower() for s in resume_skills]
    j = [s.lower() for s in job_skills]
    return [s for s in j if s in r]
