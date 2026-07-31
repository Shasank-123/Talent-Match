import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.models import User, Resume
from app.schemas.schemas import ResumeOut, SuccessResponse
from app.services.resume_service import parseResume
from app.services.ml_service import extractSkills

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def uploadResume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """POST /api/v1/resumes/upload - Upload a resume file (PDF, DOCX, TXT)."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "UNSUPPORTED_FILE_TYPE",
                "error_detail": f"Supported types: {settings.SUPPORTED_FILE_TYPES}"
            }
        )
    # Save file
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOADS_DIR, unique_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse resume
    parsed = parseResume(file_path, ext)
    skills = extractSkills(parsed.get("raw_text", ""))

    resume = Resume(
        candidate_name=parsed.get("candidate_name"),
        candidate_email=parsed.get("candidate_email"),
        file_name=file.filename,
        file_path=file_path,
        file_type=ext,
        raw_text=parsed.get("raw_text"),
        parsed_data=parsed,
        skills=skills,
        experience_years=parsed.get("experience_years", 0),
        education=parsed.get("education", []),
        is_parsed=True,
        user_id=current_user.id
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return SuccessResponse(
        status_message="Resume uploaded and parsed successfully",
        payload=ResumeOut.model_validate(resume)
    )


@router.get("", response_model=SuccessResponse)
def getResumes(
    skip: int = 0,
    limit: int = settings.DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/resumes - List all resumes for current user."""
    resumeList = db.query(Resume).filter(Resume.user_id == current_user.id).offset(skip).limit(limit).all()
    total = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    return SuccessResponse(
        status_message="Resumes retrieved",
        payload={"resumeList": [ResumeOut.model_validate(r) for r in resumeList], "total": total}
    )


@router.get("/{resumeId}", response_model=SuccessResponse)
def getResume(
    resumeId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/resumes/{resumeId} - Get resume details."""
    resume = db.query(Resume).filter(Resume.id == resumeId, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "RESUME_NOT_FOUND", "error_detail": "Resume does not exist"}
        )
    return SuccessResponse(status_message="Resume retrieved", payload=ResumeOut.model_validate(resume))


@router.delete("/{resumeId}", response_model=SuccessResponse)
def deleteResume(
    resumeId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """DELETE /api/v1/resumes/{resumeId} - Delete a resume."""
    resume = db.query(Resume).filter(Resume.id == resumeId, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "RESUME_NOT_FOUND", "error_detail": "Resume does not exist"}
        )
    if resume.file_path and os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    db.delete(resume)
    db.commit()
    return SuccessResponse(status_message="Resume deleted successfully", payload=None)
