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
    DEMO_GATE_PASSWORD: str | None = None
    BOOTSTRAP_DEMO_ACCOUNTS: bool = False
    
    # Object Storage (S3 / R2 / B2)
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_BUCKET_NAME: str = "fasal-rakshak-evidence"
    S3_REGION: str = "auto"
    LOCAL_STORAGE_DIR: str = "./storage"
    MAX_UPLOAD_BYTES: int = 100 * 1024 * 1024
    ALLOWED_VIDEO_EXTENSIONS: str = ".mp4,.mov,.m4v,.avi"
    MIN_VIDEO_DURATION_SECONDS: float = 10.0
    MAX_VIDEO_DURATION_SECONDS: float = 30.0
    MAX_VIDEO_WIDTH: int = 1920
    MAX_VIDEO_HEIGHT: int = 1080
    CELERY_CPU_QUEUE: str = "cpu_processing"
    CELERY_GPU_QUEUE: str = "gpu_inference"
    
    # Pipeline thresholds
    MIN_USABLE_FRAMES_THRESHOLD: int = 5
    QUALITY_BLUR_THRESHOLD: float = 80.0
    
    # LLM
    LLM_API_BASE_URL: str | None = None
    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gemini-1.5-flash"
    
    # Groq (for LLM advisor)
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

settings = Settings()
