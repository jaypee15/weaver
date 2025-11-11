from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from fastapi.responses import StreamingResponse
from typing import Optional
from uuid import UUID

from app.api.v1.schemas import (
    QueryRequest,
    QueryResponse,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyListResponse,
    DocumentUploadResponse,
    DocumentListResponse,
    BotConfigResponse,
    SignupResponse,
    UserMeResponse,
)
from app.auth.api_key import verify_api_key
from app.auth.types import APIKeyData
from app.auth.oauth import get_current_user, verify_supabase_token, require_admin_or_owner, User
from app.services.query import QueryService
from app.services.ingestion import IngestionService
from app.db.repositories import (
    APIKeyRepository,
    DocumentRepository,
    BotRepository,
    TenantRepository,
    ProfileRepository,
)
from app.middleware.rate_limit import check_rate_limit
from app.api.v1 import analytics


router = APIRouter()
router.include_router(analytics.router, tags=["analytics"])


@router.post("/auth/complete-signup", response_model=SignupResponse)
async def complete_signup(auth_data: dict = Depends(verify_supabase_token)):
    """
    Complete signup after OAuth - creates tenant, user profile, and bot if first time
    Called by frontend after successful Supabase OAuth
    """
    profile_repo = ProfileRepository()
    tenant_repo = TenantRepository()
    
    user_id = auth_data["id"]
    email = auth_data["email"]
    
    # Check if user profile already exists
    existing_profile = await profile_repo.get_by_id(user_id)
    
    if existing_profile:
        # User already exists, return existing data
        return SignupResponse(
            tenant_id=existing_profile["tenant_id"],
            user_id=existing_profile["id"],
            email=existing_profile["email"],
            role=existing_profile["role"],
            is_new_user=False,
            message="Welcome back!"
        )
    
    # New user - create tenant, user profile, and bot
    # Extract tenant name from email (before @)
    tenant_name = email.split('@')[0].capitalize()
    
    # Create tenant (this will auto-create bot via trigger)
    tenant_id = await tenant_repo.create(name=f"{tenant_name}'s Workspace")
    
    # Create user profile in our database
    await profile_repo.create(
        user_id=user_id,
        tenant_id=tenant_id,
        email=email,
        role="owner"
    )
    
    return SignupResponse(
        tenant_id=tenant_id,
        user_id=user_id,
        email=email,
        role="owner",
        is_new_user=True,
        message="Account created successfully!"
    )


@router.get("/users/me", response_model=UserMeResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserMeResponse(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        role=user.role
    )


@router.post("/tenants/{tenant_id}/query", response_model=QueryResponse)
async def query_bot(
    tenant_id: UUID,
    request: QueryRequest,
    api_key_data: APIKeyData = Depends(verify_api_key),
):
    if api_key_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    await check_rate_limit(api_key_data)
    
    query_service = QueryService()
    result = await query_service.query(
        tenant_id=tenant_id,
        query=request.query,
        api_key_id=api_key_data.key_id,
    )
    
    return result


@router.get("/tenants/{tenant_id}/query/stream")
async def query_bot_stream(
    tenant_id: UUID,
    query: str,
    api_key_data: APIKeyData = Depends(verify_api_key),
):
    if api_key_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    await check_rate_limit(api_key_data)
    
    query_service = QueryService()
    stream = query_service.query_stream(
        tenant_id=tenant_id,
        query=query,
        api_key_id=api_key_data.key_id,
    )
    
    return StreamingResponse(stream, media_type="text/event-stream")


@router.post("/tenants/{tenant_id}/docs:upload", response_model=DocumentUploadResponse)
async def upload_document(
    tenant_id: UUID,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    ingestion_service = IngestionService()
    result = await ingestion_service.upload_document(
        tenant_id=tenant_id,
        file=file,
    )
    
    return result


@router.get("/tenants/{tenant_id}/docs", response_model=DocumentListResponse)
async def list_documents(
    tenant_id: UUID,
    user: User = Depends(get_current_user),
):
    """List all documents for a tenant"""
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    doc_repo = DocumentRepository()
    documents = await doc_repo.list_by_tenant(tenant_id)
    
    return {"documents": documents}


@router.get("/tenants/{tenant_id}/bot", response_model=BotConfigResponse)
async def get_bot_config(
    tenant_id: UUID,
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    bot_repo = BotRepository()
    bot = await bot_repo.get_by_tenant_id(tenant_id)
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return bot


@router.post("/tenants/{tenant_id}/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    tenant_id: UUID,
    request: APIKeyCreate,
    user: User = Depends(get_current_user),
):
    require_admin_or_owner(user, tenant_id)
    
    api_key_repo = APIKeyRepository()
    result = await api_key_repo.create_key(
        tenant_id=tenant_id,
        name=request.name,
        rate_limit_rpm=request.rate_limit_rpm,
    )
    
    return result


@router.get("/tenants/{tenant_id}/api-keys", response_model=APIKeyListResponse)
async def list_api_keys(
    tenant_id: UUID,
    user: User = Depends(get_current_user),
):
    require_admin_or_owner(user, tenant_id)
    
    api_key_repo = APIKeyRepository()
    keys = await api_key_repo.list_keys(tenant_id)
    
    return {"keys": keys}


@router.delete("/tenants/{tenant_id}/api-keys/{key_id}")
async def revoke_api_key(
    tenant_id: UUID,
    key_id: UUID,
    user: User = Depends(get_current_user),
):
    require_admin_or_owner(user, tenant_id)
    
    api_key_repo = APIKeyRepository()
    await api_key_repo.revoke_key(tenant_id, key_id)
    
    return {"status": "revoked"}

