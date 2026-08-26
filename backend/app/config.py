from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./rakshak.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-secret"
    s3_bucket: str = "rakshak-evidence"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

