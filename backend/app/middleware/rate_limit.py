import time
from fastapi import HTTPException
import redis.asyncio as redis

from app.config import settings
from app.auth.types import APIKeyData

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def check_rate_limit(api_key_data: APIKeyData):
    key = f"rate_limit:{api_key_data.tenant_id}:{api_key_data.key_id}"
    window = 60
    limit = api_key_data.rate_limit_rpm
    
    current_time = int(time.time())
    window_start = current_time - window
    
    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zcard(key)
    pipe.zadd(key, {str(current_time): current_time})
    pipe.expire(key, window + 1)
    
    results = await pipe.execute()
    request_count = results[1]
    
    if request_count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} requests per minute.",
        )

