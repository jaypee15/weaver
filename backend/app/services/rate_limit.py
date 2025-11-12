"""
Daily query limit tracking service
"""
import logging
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status

from app.services.cache import cache_service
from app.config import settings

logger = logging.getLogger(__name__)


class DailyLimitService:
    """Track and enforce daily query limits per tenant"""
    
    @staticmethod
    def _get_daily_key(tenant_id: UUID) -> str:
        """Generate Redis key for daily query count"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"daily_queries:{tenant_id}:{today}"
    
    @staticmethod
    async def check_and_increment(tenant_id: UUID) -> dict:
        """
        Check if tenant is within daily limit and increment counter.
        Returns dict with current count and limit info.
        Raises HTTPException if limit exceeded.
        """
        if not cache_service.is_available:
            # If Redis unavailable, allow queries (fail open)
            logger.warning("Redis unavailable, skipping daily limit check")
            return {
                "current": 0,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": settings.MAX_QUERIES_PER_DAY,
                "redis_available": False
            }
        
        key = DailyLimitService._get_daily_key(tenant_id)
        
        try:
            # Get current count
            current_count = cache_service._redis_client.get(key)
            current = int(current_count) if current_count else 0
            
            # Check if limit exceeded
            if current >= settings.MAX_QUERIES_PER_DAY:
                logger.warning(f"Daily limit exceeded for tenant {tenant_id}: {current}/{settings.MAX_QUERIES_PER_DAY}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Daily query limit exceeded",
                        "current": current,
                        "limit": settings.MAX_QUERIES_PER_DAY,
                        "message": f"You have reached your daily limit of {settings.MAX_QUERIES_PER_DAY} queries. Limit resets at midnight UTC."
                    }
                )
            
            # Increment counter
            new_count = cache_service._redis_client.incr(key)
            
            # Set expiry to end of day (if this is the first increment)
            if new_count == 1:
                # Calculate seconds until midnight UTC
                now = datetime.now(timezone.utc)
                tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow = tomorrow.replace(day=tomorrow.day + 1)
                seconds_until_midnight = int((tomorrow - now).total_seconds())
                cache_service._redis_client.expire(key, seconds_until_midnight)
            
            remaining = settings.MAX_QUERIES_PER_DAY - new_count
            
            logger.info(f"Query count for tenant {tenant_id}: {new_count}/{settings.MAX_QUERIES_PER_DAY} (remaining: {remaining})")
            
            return {
                "current": new_count,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": max(0, remaining),
                "redis_available": True
            }
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log error but allow query (fail open)
            logger.error(f"Error checking daily limit for tenant {tenant_id}: {e}")
            return {
                "current": 0,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": settings.MAX_QUERIES_PER_DAY,
                "redis_available": False,
                "error": str(e)
            }
    
    @staticmethod
    async def get_current_usage(tenant_id: UUID) -> dict:
        """Get current daily usage without incrementing"""
        if not cache_service.is_available:
            return {
                "current": 0,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": settings.MAX_QUERIES_PER_DAY,
                "redis_available": False
            }
        
        key = DailyLimitService._get_daily_key(tenant_id)
        
        try:
            current_count = cache_service._redis_client.get(key)
            current = int(current_count) if current_count else 0
            remaining = max(0, settings.MAX_QUERIES_PER_DAY - current)
            
            return {
                "current": current,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": remaining,
                "redis_available": True
            }
        except Exception as e:
            logger.error(f"Error getting daily usage for tenant {tenant_id}: {e}")
            return {
                "current": 0,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": settings.MAX_QUERIES_PER_DAY,
                "redis_available": False,
                "error": str(e)
            }


# Singleton instance
daily_limit_service = DailyLimitService()

