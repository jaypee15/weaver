from typing import Optional
from uuid import UUID
from fastapi import HTTPException, Header, Depends
from pydantic import BaseModel
from supabase import create_client, Client

from app.config import settings
from app.db.repositories import ProfileRepository


class User(BaseModel):
    id: UUID
    email: str
    tenant_id: UUID
    role: str


def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


async def verify_supabase_token(
    authorization: Optional[str] = Header(None),
) -> dict:
    """Verify Supabase JWT token without database lookup - for signup flow"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "id": UUID(user_response.user.id),
            "email": user_response.user.email
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> User:
    """Get current user with tenant mapping from our database"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user_response.user.id
        email = user_response.user.email
        
        # Look up user's tenant mapping in our application database
        profile_repo = ProfileRepository()
        app_user = await profile_repo.get_by_id(UUID(user_id))
        
        if not app_user:
            # User authenticated with Supabase but not set up in our app yet
            raise HTTPException(
                status_code=404, 
                detail="User not found in application. Please complete signup."
            )

        return User(
            id=UUID(user_id),
            email=email,
            tenant_id=app_user["tenant_id"],
            role=app_user["role"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def require_admin_or_owner(user: User, tenant_id: UUID) -> None:
    """
    Check if user has admin or owner role and belongs to the tenant.
    Raises HTTPException if not authorized.
    """
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    if user.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Admin or owner access required")

