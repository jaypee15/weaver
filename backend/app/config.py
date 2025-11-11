from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    
    GOOGLE_API_KEY: str
    GCS_BUCKET_NAME: str
    GCS_ACCESS_KEY: str  # HMAC Access Key
    GCS_SECRET_KEY: str  # HMAC Secret
    
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    
    SENTRY_DSN: Optional[str] = None
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    RATE_LIMIT_RPM: int = 60
    MAX_FILE_SIZE_MB: int = 200
    MAX_TENANT_STORAGE_GB: int = 2
    
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP_PCT: int = 20
    TOP_K_RESULTS: int = 8
    LLM_TEMPERATURE: float = 0.2
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

