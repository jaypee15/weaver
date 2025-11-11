from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.auth.oauth import get_current_user, User
from app.db.repositories import AnalyticsRepository

router = APIRouter()


@router.get("/tenants/{tenant_id}/analytics/queries")
async def get_query_analytics(
    tenant_id: UUID,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    analytics_repo = AnalyticsRepository()
    
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = datetime.now() - timedelta(days=30)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = datetime.now()
    
    data = await analytics_repo.get_query_stats(tenant_id, start, end)
    
    return data


@router.get("/tenants/{tenant_id}/analytics/top-queries")
async def get_top_queries(
    tenant_id: UUID,
    limit: int = 10,
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    analytics_repo = AnalyticsRepository()
    top_queries = await analytics_repo.get_top_queries(tenant_id, limit)
    
    return {"queries": top_queries}


@router.get("/tenants/{tenant_id}/analytics/unanswered")
async def get_unanswered_queries(
    tenant_id: UUID,
    limit: int = 20,
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    analytics_repo = AnalyticsRepository()
    unanswered = await analytics_repo.get_unanswered_queries(tenant_id, limit)
    
    return {"queries": unanswered}

