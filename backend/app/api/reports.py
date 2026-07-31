from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Report, Ranking, JobDescription, Resume
from app.schemas.schemas import ReportGenerateRequest, ReportOut, SuccessResponse
from app.services.report_service import generateReport, downloadReport

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def generateReportEndpoint(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """POST /api/v1/reports/generate - Generate a ranking report for a job."""
    job = db.query(JobDescription).filter(
        JobDescription.id == request.job_id,
        JobDescription.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "JOB_NOT_FOUND", "error_detail": "Job does not exist"}
        )

    rankings = db.query(Ranking).filter(Ranking.job_id == job.id).order_by(Ranking.rank_position).all()
    ranking_dicts = []
    for r in rankings:
        resume = db.query(Resume).filter(Resume.id == r.resume_id).first()
        ranking_dicts.append({
            "rank_position": r.rank_position,
            "candidate_name": resume.candidate_name if resume else "Unknown",
            "overall_score": r.overall_score,
            "similarity_score": r.similarity_score,
            "skill_match_score": r.skill_match_score,
            "matching_skills": r.matching_skills,
            "skill_gap": r.skill_gap,
            "explanation": r.explanation,
        })

    job_dict = {
        "id": job.id, "title": job.title, "company": job.company,
        "required_skills": job.required_skills
    }
    report_data = generateReport(job_dict, ranking_dicts)

    report = Report(
        job_id=job.id,
        report_type=request.report_type,
        report_data=report_data,
        created_by_id=current_user.id
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    file_path = downloadReport(report.id, report_data)
    report.file_path = file_path
    db.commit()

    return SuccessResponse(
        status_message="Report generated successfully",
        payload={"report_id": report.id, "job_title": job.title, "total_candidates": len(ranking_dicts)}
    )


@router.get("/download/{reportId}")
def downloadReportEndpoint(
    reportId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/reports/download/{reportId} - Download report as JSON file."""
    report = db.query(Report).filter(
        Report.id == reportId, Report.created_by_id == current_user.id
    ).first()
    if not report or not report.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "REPORT_NOT_FOUND", "error_detail": "Report file not found"}
        )
    return FileResponse(
        path=report.file_path,
        filename=f"report_{reportId}.json",
        media_type="application/json"
    )


@router.get("/{reportId}", response_model=SuccessResponse)
def getReport(
    reportId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/reports/{reportId} - Get report details."""
    report = db.query(Report).filter(
        Report.id == reportId, Report.created_by_id == current_user.id
    ).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "REPORT_NOT_FOUND", "error_detail": "Report does not exist"}
        )
    return SuccessResponse(status_message="Report retrieved", payload=report.report_data)
