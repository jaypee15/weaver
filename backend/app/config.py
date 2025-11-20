from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API uses Session Mode (port 5432) - prepared statements enabled
    DATABASE_URL: str
    # Workers use Transaction Mode (port 6543) - high connection limit
    WORKER_DATABASE_URL: Optional[str] = None
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
    MAX_QUERIES_PER_DAY: int = 50  # Daily query limit per bot
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 3  # Reduced from 8 for faster retrieval
    LLM_TEMPERATURE: float = 0.2
    
    # Demo Bot Configuration
    DEMO_BOT_TENANT_ID: str = "00000000-0000-0000-0000-000000000000"
    DEMO_BOT_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def worker_db_url(self) -> str:
        """Get worker database URL, fallback to main DATABASE_URL if not set."""
        return self.WORKER_DATABASE_URL or self.DATABASE_URL


settings = Settings()

