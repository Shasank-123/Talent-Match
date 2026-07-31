from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "TalentMatch AI"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # JWT
    SECRET_KEY: str = "talentmatch-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite:///./talentmatch.db"

    # File storage
    UPLOADS_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    MAX_FILE_SIZE_MB: int = 10

    # ML
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD: float = 0.3
    DEFAULT_PAGE_SIZE: int = 20
    MAX_RESUME_LENGTH: int = 5000
    SUPPORTED_FILE_TYPES: list = [".pdf", ".docx", ".doc", ".txt"]

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
