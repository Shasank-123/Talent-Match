from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Resume, JobDescription, Ranking
from app.schemas.schemas import SuccessResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=SuccessResponse)
def getDashboardAnalytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/analytics/dashboard - Get dashboard summary metrics."""
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    total_jobs = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).count()
    active_jobs = db.query(JobDescription).filter(
        JobDescription.user_id == current_user.id, JobDescription.is_active == True
    ).count()

    # Get rankings for user's jobs
    user_job_ids = [j.id for j in db.query(JobDescription).filter(
        JobDescription.user_id == current_user.id
    ).all()]
    total_rankings = db.query(Ranking).filter(Ranking.job_id.in_(user_job_ids)).count() if user_job_ids else 0

    avg_score = 0.0
    if total_rankings > 0:
        rankings = db.query(Ranking).filter(Ranking.job_id.in_(user_job_ids)).all()
        avg_score = sum(r.overall_score for r in rankings) / len(rankings)

    return SuccessResponse(
        status_message="Dashboard analytics retrieved",
        payload={
            "isAnalysisReady": total_rankings > 0,
            "total_resumes": total_resumes,
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_rankings": total_rankings,
            "average_match_score": round(avg_score * 100, 1),
        }
    )


@router.get("/jobs", response_model=SuccessResponse)
def getJobsAnalytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/analytics/jobs - Get per-job analytics."""
    jobs = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).all()
    jobList = []
    for job in jobs:
        count = db.query(Ranking).filter(Ranking.job_id == job.id).count()
        top = db.query(Ranking).filter(Ranking.job_id == job.id).order_by(Ranking.rank_position).first()
        jobList.append({
            "job_id": job.id,
            "job_title": job.title,
            "candidate_count": count,
            "top_score": round((top.overall_score or 0) * 100, 1) if top else 0,
        })
    return SuccessResponse(status_message="Job analytics retrieved", payload={"jobList": jobList})


@router.get("/candidates", response_model=SuccessResponse)
def getCandidatesAnalytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/analytics/candidates - Get candidate analytics."""
    resumeList = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    candidateList = []
    for resume in resumeList:
        rankings = db.query(Ranking).filter(Ranking.resume_id == resume.id).all()
        best_score = max((r.overall_score for r in rankings), default=0)
        candidateList.append({
            "resume_id": resume.id,
            "candidate_name": resume.candidate_name,
            "skills_count": len(resume.skills or []),
            "experience_years": resume.experience_years,
            "best_match_score": round(best_score * 100, 1),
            "jobs_applied": len(rankings),
        })
    return SuccessResponse(status_message="Candidate analytics retrieved", payload={"candidateList": candidateList})
