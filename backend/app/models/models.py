from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="recruiter")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    resumes = relationship("Resume", back_populates="uploaded_by")
    jobs = relationship("JobDescription", back_populates="created_by")


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    experience_years = Column(Integer, default=0)
    location = Column(String(255))
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by = relationship("User", back_populates="jobs")
    rankings = relationship("Ranking", back_populates="job")
    required_skills_list = relationship("JobSkill", back_populates="job")


class JobSkill(Base):
    __tablename__ = "job_skills"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    skill_name = Column(String(255))
    is_required = Column(Boolean, default=True)

    job = relationship("JobDescription", back_populates="required_skills_list")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(255))
    candidate_email = Column(String(255))
    file_name = Column(String(500))
    file_path = Column(String(500))
    file_type = Column(String(50))
    raw_text = Column(Text)
    parsed_data = Column(JSON, default=dict)
    skills = Column(JSON, default=list)
    experience_years = Column(Integer, default=0)
    education = Column(JSON, default=list)
    is_parsed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    uploaded_by = relationship("User", back_populates="resumes")
    rankings = relationship("Ranking", back_populates="resume")
    interview_questions = relationship("InterviewQuestion", back_populates="resume")


class Ranking(Base):
    __tablename__ = "rankings"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    overall_score = Column(Float, default=0.0)
    similarity_score = Column(Float, default=0.0)
    skill_match_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    rank_position = Column(Integer, default=0)
    skill_gap = Column(JSON, default=list)
    matching_skills = Column(JSON, default=list)
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("JobDescription", back_populates="rankings")
    resume = relationship("Resume", back_populates="rankings")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    question = Column(Text)
    category = Column(String(100))
    difficulty = Column(String(50), default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="interview_questions")


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    report_type = Column(String(100), default="ranking")
    file_path = Column(String(500))
    report_data = Column(JSON, default=dict)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255))
    resource_type = Column(String(100))
    resource_id = Column(Integer)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
