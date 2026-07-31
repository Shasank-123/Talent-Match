from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import create_tables
from app.api import auth, resumes, jobs, rankings, skills, analytics, reports, interviews

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Resume Matching & Candidate Ranking Platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception Handler ──────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "error_code": "INTERNAL_SERVER_ERROR",
                "error_detail": str(exc)
            }
        }
    )

# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    create_tables()
    print(f"[OK] {settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"[DOCS] API Docs: http://localhost:8000/api/docs")

# ── Routes ─────────────────────────────────────────────────────────────────────
prefix = settings.API_V1_PREFIX
app.include_router(auth.router, prefix=prefix)
app.include_router(resumes.router, prefix=prefix)
app.include_router(jobs.router, prefix=prefix)
app.include_router(rankings.router, prefix=prefix)
app.include_router(skills.router, prefix=prefix)
app.include_router(analytics.router, prefix=prefix)
app.include_router(reports.router, prefix=prefix)
app.include_router(interviews.router, prefix=prefix)


@app.get("/")
def root():
    return {
        "success": True,
        "status_message": f"{settings.APP_NAME} API is running",
        "payload": {"version": settings.APP_VERSION, "docs": "/api/docs"}
    }
