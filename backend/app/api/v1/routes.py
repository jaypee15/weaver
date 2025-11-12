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
    BusinessInfoRequest,
    GeneratedPromptResponse,
    BotConfigUpdate,
    BotSettingsResponse,
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
from app.services.cache import cache_service
from app.services.rate_limit import daily_limit_service
from app.config import settings
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
    # Allow access to demo bot OR user's own tenant
    demo_bot_id = UUID(settings.DEMO_BOT_TENANT_ID) if settings.DEMO_BOT_ENABLED else None
    
    if tenant_id != api_key_data.tenant_id:
        # Check if querying demo bot
        if not (demo_bot_id and tenant_id == demo_bot_id):
            raise HTTPException(status_code=403, detail="Access denied. You can only query your own bot or the demo bot.")
    
    # Check rate limit (per minute)
    await check_rate_limit(api_key_data)
    
    # Check daily query limit - ALWAYS use user's tenant_id (not demo bot's)
    limit_info = await daily_limit_service.check_and_increment(api_key_data.tenant_id)
    
    query_service = QueryService()
    result = await query_service.query(
        tenant_id=tenant_id,  # Can be demo bot or user's own bot
        query=request.query,
        api_key_id=api_key_data.key_id,
    )
    
    # Add limit info to response
    result.daily_usage = limit_info
    
    return result


@router.get("/tenants/{tenant_id}/query/stream")
async def query_bot_stream(
    tenant_id: UUID,
    query: str,
    api_key_data: APIKeyData = Depends(verify_api_key),
):
    # Allow access to demo bot OR user's own tenant
    demo_bot_id = UUID(settings.DEMO_BOT_TENANT_ID) if settings.DEMO_BOT_ENABLED else None
    
    if tenant_id != api_key_data.tenant_id:
        # Check if querying demo bot
        if not (demo_bot_id and tenant_id == demo_bot_id):
            raise HTTPException(status_code=403, detail="Access denied. You can only query your own bot or the demo bot.")
    
    # Check rate limit (per minute)
    await check_rate_limit(api_key_data)
    
    # Check daily query limit - ALWAYS use user's tenant_id (not demo bot's)
    await daily_limit_service.check_and_increment(api_key_data.tenant_id)
    
    query_service = QueryService()
    stream = query_service.query_stream(
        tenant_id=tenant_id,  # Can be demo bot or user's own bot
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


@router.get("/cache/stats")
async def get_cache_stats(user: User = Depends(get_current_user)):
    """
    Get cache statistics (admin/monitoring endpoint)
    """
    stats = cache_service.get_stats()
    return stats


@router.get("/tenants/{tenant_id}/usage/daily")
async def get_daily_usage(
    tenant_id: UUID,
    user: User = Depends(get_current_user),
):
    """
    Get current daily query usage for a tenant
    """
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    usage = await daily_limit_service.get_current_usage(tenant_id)
    return usage


@router.post("/tenants/{tenant_id}/bot/generate-prompt", response_model=GeneratedPromptResponse)
async def generate_system_prompt(
    tenant_id: UUID,
    request: BusinessInfoRequest,
    user: User = Depends(get_current_user),
):
    """
    Generate optimal system prompt from business information using LLM
    """
    require_admin_or_owner(user, tenant_id)
    
    from app.services.prompt_generator import PromptGeneratorService
    
    generator = PromptGeneratorService()
    system_prompt = await generator.generate_from_business_info(
        business_name=request.business_name,
        industry=request.industry,
        description=request.description,
        tone=request.tone,
        primary_goal=request.primary_goal,
        special_instructions=request.special_instructions,
    )
    
    return GeneratedPromptResponse(
        system_prompt=system_prompt,
        business_info=request.dict(),
    )


@router.put("/tenants/{tenant_id}/bot", response_model=BotSettingsResponse)
async def update_bot_config(
    tenant_id: UUID,
    request: BotConfigUpdate,
    user: User = Depends(get_current_user),
):
    """
    Update bot configuration (system prompt, business info, etc.)
    """
    require_admin_or_owner(user, tenant_id)
    
    bot_repo = BotRepository()
    
    # Get existing bot
    bot = await bot_repo.get_by_tenant(tenant_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Update config_json
    current_config = bot.get("config", {})
    
    # Update system_prompt if provided
    if request.system_prompt is not None:
        if request.system_prompt.strip():
            current_config["system_prompt"] = request.system_prompt.strip()
        else:
            # Empty string = remove custom prompt, use default
            current_config.pop("system_prompt", None)
    
    # Update business_info if provided
    if request.business_info is not None:
        current_config["business_info"] = request.business_info
    
    # Update bot in database
    await bot_repo.update_config(tenant_id, current_config)
    
    # Return updated config
    updated_bot = await bot_repo.get_by_tenant(tenant_id)
    return BotSettingsResponse(
        tenant_id=str(tenant_id),
        name=updated_bot["name"],
        system_prompt=updated_bot["config"].get("system_prompt"),
        business_info=updated_bot["config"].get("business_info"),
        using_default_prompt=("system_prompt" not in updated_bot["config"]),
        created_at=updated_bot["created_at"].isoformat(),
        updated_at=updated_bot["updated_at"].isoformat(),
    )

