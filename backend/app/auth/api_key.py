import secrets
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, Header, Depends
from pydantic import BaseModel

from app.auth.utils import verify_key_hash
from app.auth.types import APIKeyData
from app.db.repositories import APIKeyRepository


async def verify_api_key(
    authorization: Optional[str] = Header(None),
) -> APIKeyData:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    if not api_key.startswith("wvr_"):
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    api_key_repo = APIKeyRepository()
    key_data = await api_key_repo.verify_key(api_key)
    
    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    
    await api_key_repo.update_last_used(key_data.key_id)
    
    return key_data

