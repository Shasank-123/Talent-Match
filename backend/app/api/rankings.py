from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Resume, JobDescription, Ranking
from app.schemas.schemas import RankingRunRequest, RankingOut, SuccessResponse
from app.services import ml_service

router = APIRouter(prefix="/rankings", tags=["Rankings"])


@router.post("/analyze", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def analyzeRankings(
    request: RankingRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    POST /api/v1/rankings/analyze - Run ML ranking analysis for a job.
    Changed from /rankings/run → /rankings/analyze
    """
    job = db.query(JobDescription).filter(
        JobDescription.id == request.job_id,
        JobDescription.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "JOB_NOT_FOUND", "error_detail": "Job does not exist"}
        )

    # Get resumes
    resume_query = db.query(Resume).filter(Resume.user_id == current_user.id)
    if request.resume_ids:
        resume_query = resume_query.filter(Resume.id.in_(request.resume_ids))
    resumeList = resume_query.all()

    if not resumeList:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "NO_RESUMES", "error_detail": "No resumes found to rank"}
        )

    # Delete existing rankings for this job
    db.query(Ranking).filter(Ranking.job_id == job.id).delete()

    job_text = f"{job.title} {job.description} {' '.join(job.required_skills or [])}"
    job_skills = job.required_skills or []
    required_years = job.experience_years or 0

    candidates_data = []
    for resume in resumeList:
        resume_text = resume.raw_text or ""
        resume_skills = resume.skills or []

        # Compute scores
        similarityScore = ml_service.calculateSimilarity(resume_text, job_text)
        skill_match_score, matching_skills, skillGap = ml_service.calculateSkillMatchScore(
            resume_skills, job_skills
        )
        experience_score = ml_service.calculateExperienceScore(
            resume.experience_years or 0, required_years
        )
        overallScore = ml_service.calculateOverallScore(
            similarityScore, skill_match_score, experience_score
        )
        explanation = ml_service.generateExplanation(
            resume.candidate_name or "Candidate",
            job.title,
            overallScore,
            matching_skills,
            skillGap,
            resume.experience_years or 0
        )
        candidates_data.append({
            "resume_id": resume.id,
            "candidate_name": resume.candidate_name,
            "overall_score": overallScore,
            "similarity_score": similarityScore,
            "skill_match_score": skill_match_score,
            "experience_score": experience_score,
            "skill_gap": skillGap,
            "matching_skills": matching_skills,
            "explanation": explanation,
        })

    # Rank candidates
    rankingList = ml_service.rankCandidates(candidates_data)

    # Save rankings to DB
    saved_rankings = []
    for item in rankingList:
        ranking = Ranking(
            job_id=job.id,
            resume_id=item["resume_id"],
            overall_score=item["overall_score"],
            similarity_score=item["similarity_score"],
            skill_match_score=item["skill_match_score"],
            experience_score=item["experience_score"],
            rank_position=item["rank_position"],
            skill_gap=item["skill_gap"],
            matching_skills=item["matching_skills"],
            explanation=item["explanation"]
        )
        db.add(ranking)
        db.flush()
        saved_rankings.append({**item, "id": ranking.id, "job_id": job.id})

    db.commit()

    return SuccessResponse(
        status_message=f"Ranking analysis completed. {len(saved_rankings)} candidates ranked.",
        payload={
            "job_id": job.id,
            "job_title": job.title,
            "total_candidates": len(saved_rankings),
            "rankingList": saved_rankings
        }
    )


@router.get("/history", response_model=SuccessResponse)
@router.get("/history/all", response_model=SuccessResponse)
def getRankingHistory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/rankings/history - Get ranking history."""
    jobs = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).all()
    rankingHistory = []
    for job in jobs:
        count = db.query(Ranking).filter(Ranking.job_id == job.id).count()
        if count > 0:
            rankingHistory.append({"job_id": job.id, "job_title": job.title, "candidate_count": count})
    return SuccessResponse(status_message="Ranking history retrieved", payload={"rankingHistory": rankingHistory})


@router.get("/{jobId}", response_model=SuccessResponse)
def getRankings(
    jobId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/rankings/{jobId} - Get all rankings for a job."""
    job = db.query(JobDescription).filter(
        JobDescription.id == jobId, JobDescription.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "JOB_NOT_FOUND", "error_detail": "Job does not exist"}
        )
    rankings = db.query(Ranking).filter(Ranking.job_id == jobId).order_by(Ranking.rank_position).all()
    result = []
    for r in rankings:
        resume = db.query(Resume).filter(Resume.id == r.resume_id).first()
        result.append({
            "id": r.id,
            "job_id": r.job_id,
            "resume_id": r.resume_id,
            "overall_score": r.overall_score,
            "similarity_score": r.similarity_score,
            "skill_match_score": r.skill_match_score,
            "experience_score": r.experience_score,
            "rank_position": r.rank_position,
            "skill_gap": r.skill_gap,
            "matching_skills": r.matching_skills,
            "explanation": r.explanation,
            "candidate_name": resume.candidate_name if resume else None,
            "created_at": r.created_at,
        })
    return SuccessResponse(status_message="Rankings retrieved", payload={"rankingList": result, "job_title": job.title})


@router.get("/{jobId}/{candidateId}", response_model=SuccessResponse)
def getCandidateRanking(
    jobId: int,
    candidateId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/rankings/{jobId}/{candidateId} - Get specific candidate ranking."""
    ranking = db.query(Ranking).filter(
        Ranking.job_id == jobId, Ranking.resume_id == candidateId
    ).first()
    if not ranking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "RANKING_NOT_FOUND", "error_detail": "No ranking found for this candidate and job"}
        )
    resume = db.query(Resume).filter(Resume.id == candidateId).first()
    return SuccessResponse(
        status_message="Candidate ranking retrieved",
        payload={
            "id": ranking.id,
            "job_id": ranking.job_id,
            "resume_id": ranking.resume_id,
            "overall_score": ranking.overall_score,
            "rank_position": ranking.rank_position,
            "skill_gap": ranking.skill_gap,
            "matching_skills": ranking.matching_skills,
            "explanation": ranking.explanation,
            "candidate_name": resume.candidate_name if resume else None,
        }
    )
