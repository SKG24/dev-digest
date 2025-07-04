# File: app/services/cache_service.py
import json
import time
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger("dev_digest.cache")

class InMemoryCache:
    """Simple in-memory cache for frequently accessed data"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry["expires_at"]:
                logger.debug(f"Cache hit for key: {key}")
                return entry["value"]
            else:
                # Expired, remove from cache
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value"""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
        logger.debug(f"Cache set for key: {key}, TTL: {ttl}")
    
    def delete(self, key: str) -> None:
        """Delete cached value"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self) -> None:
        """Clear all cached values"""
        self.cache.clear()
        logger.debug("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time >= entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "entries": len(self.cache),
            "memory_usage_bytes": sum(
                len(json.dumps(entry)) for entry in self.cache.values()
            )
        }

# Global cache instance
cache = InMemoryCache()