from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Resume, JobDescription, InterviewQuestion
from app.schemas.schemas import InterviewGenerateRequest, InterviewQuestionOut, SuccessResponse
from app.services.ml_service import generateInterviewQuestions

router = APIRouter(prefix="/interviews", tags=["Interview Questions"])


@router.post("/generate", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def generateInterviewQuestionsEndpoint(
    request: InterviewGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """POST /api/v1/interviews/generate - Generate interview questions for a candidate + job."""
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "RESUME_NOT_FOUND", "error_detail": "Resume does not exist"}
        )
    job = db.query(JobDescription).filter(
        JobDescription.id == request.job_id, JobDescription.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "JOB_NOT_FOUND", "error_detail": "Job does not exist"}
        )

    # Clear existing questions for this resume+job combo
    db.query(InterviewQuestion).filter(
        InterviewQuestion.resume_id == request.resume_id,
        InterviewQuestion.job_id == request.job_id
    ).delete()

    # Get skill gap from stored ranking if available
    from app.models.models import Ranking
    ranking = db.query(Ranking).filter(
        Ranking.resume_id == request.resume_id, Ranking.job_id == request.job_id
    ).first()
    skillGap = ranking.skill_gap if ranking else []
    resume_skills = resume.skills or []
    job_skills = job.required_skills or []

    questions_data = generateInterviewQuestions(resume_skills, job_skills, skillGap, job.title)

    interviewQuestionList = []
    for q in questions_data:
        iq = InterviewQuestion(
            resume_id=request.resume_id,
            job_id=request.job_id,
            question=q["question"],
            category=q["category"],
            difficulty=q["difficulty"]
        )
        db.add(iq)
        db.flush()
        interviewQuestionList.append({
            "id": iq.id,
            "question": iq.question,
            "category": iq.category,
            "difficulty": iq.difficulty,
        })

    db.commit()

    return SuccessResponse(
        status_message=f"{len(interviewQuestionList)} interview questions generated",
        payload={
            "hasInterviewQuestions": True,
            "resume_id": request.resume_id,
            "job_id": request.job_id,
            "candidate_name": resume.candidate_name,
            "job_title": job.title,
            "interviewQuestionList": interviewQuestionList
        }
    )


@router.get("/{candidateId}", response_model=SuccessResponse)
def getInterviewQuestions(
    candidateId: int,
    job_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """GET /api/v1/interviews/{candidateId} - Get interview questions for a candidate."""
    resume = db.query(Resume).filter(Resume.id == candidateId, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "RESUME_NOT_FOUND", "error_detail": "Resume does not exist"}
        )
    query = db.query(InterviewQuestion).filter(InterviewQuestion.resume_id == candidateId)
    if job_id:
        query = query.filter(InterviewQuestion.job_id == job_id)
    questions = query.all()
    return SuccessResponse(
        status_message="Interview questions retrieved",
        payload={
            "hasInterviewQuestions": len(questions) > 0,
            "candidate_name": resume.candidate_name,
            "interviewQuestionList": [
                {"id": q.id, "question": q.question, "category": q.category, "difficulty": q.difficulty}
                for q in questions
            ]
        }
    )
