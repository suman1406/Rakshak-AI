from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "local"
    PROJECT_NAME: str = "Fasal Rakshak AI"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./rakshak.db"
    
    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Auth / JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production-12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day for dev
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    DEMO_GATE_PASSWORD: str = "rakshak2026"
    
    # Object Storage (S3 / R2 / B2)
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_BUCKET_NAME: str = "fasal-rakshak-evidence"
    S3_REGION: str = "auto"
    LOCAL_STORAGE_DIR: str = "./storage"
    
    # Pipeline thresholds
    MIN_USABLE_FRAMES_THRESHOLD: int = 5
    QUALITY_BLUR_THRESHOLD: float = 80.0
    
    # LLM
    LLM_API_BASE_URL: str | None = None
    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gemini-1.5-flash"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

settings = Settings()
