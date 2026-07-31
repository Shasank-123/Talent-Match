from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.models import User, JobDescription
from app.schemas.schemas import JobCreate, JobUpdate, JobOut, SuccessResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def createJob(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """POST /api/v1/jobs - Create a new job description."""
    job = JobDescription(
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
        required_skills=job_data.required_skills,
        preferred_skills=job_data.preferred_skills,
        experience_years=job_data.experience_years,
        location=job_data.location,
        user_id=current_user.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return SuccessResponse(status_message="Job created successfully", payload=JobOut.model_validate(job))


@router.get("", response_model=SuccessResponse)
def getJobs(
    skip: int = 0,
    limit: int = settings.DEFAULT_PAGE_SIZE,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/jobs - List all job descriptions."""
    query = db.query(JobDescription).filter(JobDescription.user_id == current_user.id)
    if search:
        query = query.filter(JobDescription.title.ilike(f"%{search}%"))
    total = query.count()
    jobList = query.offset(skip).limit(limit).all()
    return SuccessResponse(
        status_message="Jobs retrieved",
        payload={"jobList": [JobOut.model_validate(j) for j in jobList], "total": total}
    )


@router.get("/{jobId}", response_model=SuccessResponse)
def getJob(
    jobId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/jobs/{jobId} - Get job details."""
    job = db.query(JobDescription).filter(
        JobDescription.id == jobId, JobDescription.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "JOB_NOT_FOUND", "error_detail": "Job does not exist"}
        )
    return SuccessResponse(status_message="Job retrieved", payload=JobOut.model_validate(job))


@router.put("/{jobId}", response_model=SuccessResponse)
def updateJob(
    jobId: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """PUT /api/v1/jobs/{jobId} - Update a job description."""
    job = db.query(JobDescription).filter(
        JobDescription.id == jobId, JobDescription.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "JOB_NOT_FOUND", "error_detail": "Job does not exist"}
        )
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return SuccessResponse(status_message="Job updated successfully", payload=JobOut.model_validate(job))


@router.delete("/{jobId}", response_model=SuccessResponse)
def deleteJob(
    jobId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """DELETE /api/v1/jobs/{jobId} - Delete a job."""
    job = db.query(JobDescription).filter(
        JobDescription.id == jobId, JobDescription.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "JOB_NOT_FOUND", "error_detail": "Job does not exist"}
        )
    db.delete(job)
    db.commit()
    return SuccessResponse(status_message="Job deleted successfully", payload=None)
