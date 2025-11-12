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


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: str
    latency_ms: int


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


class BotConfigResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    config: dict
    created_at: datetime

