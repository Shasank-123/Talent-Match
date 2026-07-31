from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime


# ─────────────────────────────────────────────
# Standard Response Envelope
# ─────────────────────────────────────────────
class SuccessResponse(BaseModel):
    success: bool = True
    status_message: str = "Operation completed successfully"
    payload: Any = None


class ErrorDetail(BaseModel):
    error_code: str
    error_detail: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


# ─────────────────────────────────────────────
# Auth Schemas
# ─────────────────────────────────────────────
class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    role: Optional[str] = "recruiter"


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─────────────────────────────────────────────
# Job Schemas
# ─────────────────────────────────────────────
class JobCreate(BaseModel):
    title: str
    company: Optional[str] = None
    description: str
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    experience_years: Optional[int] = 0
    location: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class JobOut(BaseModel):
    id: int
    title: str
    company: Optional[str]
    description: str
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    experience_years: Optional[int] = 0
    location: Optional[str]
    is_active: bool
    user_id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Resume Schemas
# ─────────────────────────────────────────────
class ResumeOut(BaseModel):
    id: int
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    file_name: str
    file_type: str
    skills: Optional[List[str]] = []
    experience_years: Optional[int] = 0
    is_parsed: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Ranking Schemas
# ─────────────────────────────────────────────
class RankingRunRequest(BaseModel):
    job_id: int
    resume_ids: Optional[List[int]] = None  # None = rank all resumes


class RankingOut(BaseModel):
    id: int
    job_id: int
    resume_id: int
    overall_score: float
    similarity_score: float
    skill_match_score: float
    experience_score: float
    rank_position: int
    skill_gap: Optional[List[str]] = []
    matching_skills: Optional[List[str]] = []
    explanation: Optional[str]
    candidate_name: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Skills Schemas
# ─────────────────────────────────────────────
class SkillExtractRequest(BaseModel):
    text: str


class SkillGapRequest(BaseModel):
    candidate_id: int
    job_id: int


# ─────────────────────────────────────────────
# Interview Schemas
# ─────────────────────────────────────────────
class InterviewGenerateRequest(BaseModel):
    resume_id: int
    job_id: int


class InterviewQuestionOut(BaseModel):
    id: int
    question: str
    category: str
    difficulty: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Report Schemas
# ─────────────────────────────────────────────
class ReportGenerateRequest(BaseModel):
    job_id: int
    report_type: Optional[str] = "ranking"


class ReportOut(BaseModel):
    id: int
    job_id: int
    report_type: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
