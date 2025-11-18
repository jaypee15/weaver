from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SignupResponse(BaseModel):
    tenant_id: UUID
    user_id: UUID
    email: str
    role: str
    is_new_user: bool
    message: str


class UserMeResponse(BaseModel):
    user_id: UUID
    tenant_id: UUID
    email: str
    role: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)


class Source(BaseModel):
    doc_id: str
    page: Optional[int] = None
    confidence: float


class DailyUsage(BaseModel):
    current: int
    limit: int
    remaining: int
    redis_available: bool


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: str
    latency_ms: int
    daily_usage: Optional[DailyUsage] = None


class APIKeyCreate(BaseModel):
    name: Optional[str] = None
    rate_limit_rpm: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: UUID
    key: str
    name: Optional[str]
    created_at: datetime
    rate_limit_rpm: int


class APIKeyMetadata(BaseModel):
    id: UUID
    name: Optional[str]
    created_at: datetime
    last_used_at: Optional[datetime]
    revoked: bool
    rate_limit_rpm: int


class APIKeyListResponse(BaseModel):
    keys: List[APIKeyMetadata]


class DocumentUploadResponse(BaseModel):
    doc_id: UUID
    filename: str
    status: str
    upload_url: Optional[str] = None


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    size_bytes: int
    status: str
    error_message: Optional[str]
    created_at: str
    updated_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total: int
    limit: int
    offset: int
    status_filter: Optional[str] = None


class BotConfigResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    config: dict
    created_at: datetime


class BusinessInfoRequest(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10, max_length=1000)
    tone: str = Field(..., pattern="^(professional|friendly|technical|casual|formal)$")
    primary_goal: str = Field(..., min_length=5, max_length=500)
    special_instructions: Optional[str] = Field(None, max_length=500)


class GeneratedPromptResponse(BaseModel):
    system_prompt: str
    business_info: dict


class BotConfigUpdate(BaseModel):
    system_prompt: Optional[str] = Field(None, max_length=2000)
    business_info: Optional[dict] = None


class BotSettingsResponse(BaseModel):
    tenant_id: str
    name: str
    system_prompt: Optional[str] = None
    business_info: Optional[dict] = None
    using_default_prompt: bool
    created_at: str
    updated_at: str

