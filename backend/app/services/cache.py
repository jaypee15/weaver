"""
Centralized Redis cache service with connection pooling
"""
import hashlib
import json
import logging
from typing import Optional, Any
from redis import Redis
from redis.exceptions import RedisError

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Singleton Redis cache service"""
    
    _instance = None
    _redis_client: Optional[Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Redis connection pool"""
        try:
            # Create a single connection pool shared across all cache operations
            self._redis_client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # Handle encoding/decoding manually for flexibility
                max_connections=50,  # Connection pool size
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self._redis_client.ping()
            logger.info("Redis cache service initialized successfully")
        except RedisError as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache will be disabled.")
            self._redis_client = None
        except Exception as e:
            logger.error(f"Unexpected error initializing Redis: {e}. Cache will be disabled.")
            self._redis_client = None
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self._redis_client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_available:
            return None
        
        try:
            value = self._redis_client.get(key)
            if value:
                # Decode bytes to string and parse JSON
                return json.loads(value.decode('utf-8'))
            return None
        except RedisError as e:
            logger.warning(f"Cache GET error for key '{key}': {e}")
            return None
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Cache value decode error for key '{key}': {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL in seconds"""
        if not self.is_available:
            return False
        
        try:
            # Encode value as JSON bytes
            encoded_value = json.dumps(value).encode('utf-8')
            self._redis_client.setex(key, ttl, encoded_value)
            return True
        except RedisError as e:
            logger.warning(f"Cache SET error for key '{key}': {e}")
            return False
        except (TypeError, ValueError) as e:
            logger.warning(f"Cache value encode error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.is_available:
            return False
        
        try:
            self._redis_client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Cache DELETE error for key '{key}': {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern. Returns number of keys deleted."""
        if not self.is_available:
            return 0
        
        try:
            keys = self._redis_client.keys(pattern)
            if keys:
                return self._redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"Cache CLEAR error for pattern '{pattern}': {e}")
            return 0
    
    @staticmethod
    def generate_key(prefix: str, *args) -> str:
        """Generate a consistent cache key from prefix and arguments"""
        # Concatenate all args and create hash
        key_parts = [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get_stats(self) -> dict:
        """Get Redis cache statistics"""
        if not self.is_available:
            return {"available": False}
        
        try:
            info = self._redis_client.info("stats")
            return {
                "available": True,
                "total_connections": info.get("total_connections_received", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
            }
        except RedisError as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {"available": False, "error": str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Singleton instance
cache_service = CacheService()

