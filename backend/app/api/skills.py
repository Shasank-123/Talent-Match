from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Resume, Ranking, JobDescription
from app.schemas.schemas import SkillExtractRequest, SuccessResponse
from app.services.ml_service import extractSkills, COMMON_SKILLS

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("", response_model=SuccessResponse)
def getSkills(current_user: User = Depends(get_current_user)):
    """GET /api/v1/skills - Get list of all known skills."""
    skillList = sorted(COMMON_SKILLS)
    return SuccessResponse(status_message="Skills retrieved", payload={"skillList": skillList})


@router.post("/extract", response_model=SuccessResponse)
def extractSkillsFromText(
    request: SkillExtractRequest,
    current_user: User = Depends(get_current_user)
):
    """POST /api/v1/skills/extract - Extract skills from free text."""
    skillList = extractSkills(request.text)
    return SuccessResponse(
        status_message="Skills extracted",
        payload={"skillList": skillList, "count": len(skillList)}
    )


@router.get("/missing/{candidateId}", response_model=SuccessResponse)
def getMissingSkills(
    candidateId: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/skills/missing/{candidateId} - Get skill gap for a candidate vs job."""
    resume = db.query(Resume).filter(Resume.id == candidateId, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "RESUME_NOT_FOUND", "error_detail": "Resume does not exist"}
        )
    ranking = db.query(Ranking).filter(
        Ranking.resume_id == candidateId, Ranking.job_id == job_id
    ).first()
    if ranking:
        skillGap = ranking.skill_gap or []
        matching = ranking.matching_skills or []
    else:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": "JOB_NOT_FOUND", "error_detail": "Job does not exist"}
            )
        resume_skills = [s.lower() for s in (resume.skills or [])]
        job_skills = [s.lower() for s in (job.required_skills or [])]
        matching = [s for s in job_skills if s in resume_skills]
        skillGap = [s for s in job_skills if s not in resume_skills]

    return SuccessResponse(
        status_message="Skill gap retrieved",
        payload={
            "candidate_id": candidateId,
            "job_id": job_id,
            "hasSkillGap": len(skillGap) > 0,
            "skillGap": skillGap,
            "matching_skills": matching,
        }
    )
