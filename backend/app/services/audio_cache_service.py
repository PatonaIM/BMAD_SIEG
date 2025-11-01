"""Audio caching service for TTS generated audio."""

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta

import structlog

logger = structlog.get_logger().bind(service="audio_cache_service")


@dataclass
class CachedAudio:
    """Container for cached audio data with expiration."""

    audio_bytes: bytes
    created_at: datetime
    metadata: dict
    cache_key: str

    def is_expired(self, ttl_seconds: int = 86400) -> bool:
        """
        Check if cached audio has expired.
        
        Args:
            ttl_seconds: Time-to-live in seconds (default: 24 hours)
        
        Returns:
            True if expired, False otherwise
        """
        expiry_time = self.created_at + timedelta(seconds=ttl_seconds)
        return datetime.utcnow() > expiry_time

    def age_seconds(self) -> int:
        """Calculate age of cached audio in seconds."""
        return int((datetime.utcnow() - self.created_at).total_seconds())


class AudioCacheService:
    """
    In-memory cache service for TTS-generated audio files.
    
    Caches audio based on text content, voice, and speed parameters to reduce
    OpenAI API calls and improve response times. Uses SHA-256 hashing for
    cache keys and implements TTL-based expiration.
    
    Cache Strategy:
    ==============
    - Cache Key: SHA-256 hash of (text + voice + speed)
    - TTL: 24 hours (configurable)
    - Storage: In-memory Python dict (MVP)
    - Eviction: Lazy deletion on access (check expiry)
    - Future: Redis/Memcached for distributed caching
    
    Performance Benefits:
    ====================
    - Reduces OpenAI API costs (cache hit = $0 cost)
    - Improves response time (cache hit: ~5ms vs API: ~1500ms)
    - Reduces API rate limit pressure
    - Target cache hit rate: 40%+ for common questions
    
    Cost Optimization:
    =================
    - Average question: 150 chars @ $0.015/1K = $0.00225
    - 40% cache hit rate saves: $0.0009 per question
    - 100 interviews/day * 10 questions * 40% = $3.60/day savings
    
    Usage Examples:
    ==============
    Initialize service:
        >>> cache = AudioCacheService(ttl_seconds=86400)
        
    Check cache before generation:
        >>> cache_key = cache.get_cache_key(text, voice, speed)
        >>> cached = await cache.get_cached_audio(cache_key)
        >>> if cached:
        ...     return cached.audio_bytes
        
    Store generated audio:
        >>> await cache.cache_audio(cache_key, audio_bytes, metadata)
        
    Get cache statistics:
        >>> stats = cache.get_cache_stats()
        >>> print(f"Hit rate: {stats['hit_rate']:.1%}")
        >>> print(f"Cached items: {stats['cached_items']}")
    
    Thread Safety:
    =============
    Note: This in-memory implementation is NOT thread-safe for multi-worker
    deployments. Each worker maintains its own cache. For production, migrate
    to Redis for shared cache across workers.
    
    Redis Migration Path:
    ====================
    1. Install: pip install redis
    2. Replace _cache dict with Redis client
    3. Use Redis SETEX for TTL-based expiration
    4. Use Redis GET/SET for cache operations
    5. Monitor with Redis INFO command
    
    Example Redis Implementation:
        >>> import redis.asyncio as redis
        >>> client = redis.from_url("redis://localhost:6379")
        >>> await client.setex(f"tts:{cache_key}", 86400, audio_bytes)
        >>> cached = await client.get(f"tts:{cache_key}")
    """

    def __init__(self, ttl_seconds: int = 86400):
        """
        Initialize audio cache service.
        
        Args:
            ttl_seconds: Time-to-live for cached audio in seconds (default: 24 hours)
        """
        self._cache: dict[str, CachedAudio] = {}
        self._cache_ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

        logger.info(
            "audio_cache_service_initialized",
            ttl_seconds=ttl_seconds,
            ttl_hours=ttl_seconds / 3600
        )

    def get_cache_key(self, text: str, voice: str, speed: float) -> str:
        """
        Generate deterministic cache key from TTS parameters.
        
        Uses SHA-256 to create a unique, fixed-length key that represents
        the combination of text, voice, and speed. Same inputs always
        produce the same key.
        
        Args:
            text: Text to be synthesized
            voice: Voice identifier (e.g., "alloy")
            speed: Speech speed (e.g., 0.95)
        
        Returns:
            SHA-256 hash string (64 hex characters)
        
        Example:
            >>> cache.get_cache_key("Hello world", "alloy", 1.0)
            "7f8b9c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b"
        """
        # Normalize text (strip whitespace, lowercase for consistency)
        normalized_text = text.strip().lower()
        
        # Create composite string with separators
        content = f"{normalized_text}|{voice}|{speed:.2f}"
        
        # Generate SHA-256 hash
        cache_key = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        return cache_key

    async def get_cached_audio(self, cache_key: str) -> CachedAudio | None:
        """
        Retrieve cached audio if exists and not expired.
        
        Checks cache for audio matching the key. If found and not expired,
        increments hit counter and returns audio. If expired or not found,
        removes expired entry and increments miss counter.
        
        Args:
            cache_key: SHA-256 hash from get_cache_key()
        
        Returns:
            CachedAudio object if found and valid, None otherwise
        
        Side Effects:
            - Increments _hits or _misses counter
            - Removes expired entries from cache (lazy eviction)
            - Logs cache hit/miss events
        """
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            
            # Check if expired
            if cached.is_expired(self._cache_ttl):
                # Remove expired entry
                del self._cache[cache_key]
                self._misses += 1
                
                logger.info(
                    "cache_miss_expired",
                    cache_key=cache_key,
                    age_seconds=cached.age_seconds(),
                    ttl_seconds=self._cache_ttl
                )
                return None
            
            # Cache hit!
            self._hits += 1
            
            logger.info(
                "cache_hit",
                cache_key=cache_key,
                audio_size_bytes=len(cached.audio_bytes),
                age_seconds=cached.age_seconds(),
                hit_rate=self.get_hit_rate()
            )
            
            return cached
        
        # Cache miss
        self._misses += 1
        
        logger.info(
            "cache_miss",
            cache_key=cache_key,
            hit_rate=self.get_hit_rate()
        )
        
        return None

    async def cache_audio(
        self,
        cache_key: str,
        audio_bytes: bytes,
        metadata: dict
    ) -> None:
        """
        Store generated audio in cache with metadata.
        
        Saves audio bytes and metadata in cache with current timestamp.
        Replaces existing entry if key already exists.
        
        Args:
            cache_key: SHA-256 hash from get_cache_key()
            audio_bytes: Generated MP3 audio bytes
            metadata: TTS generation metadata (provider, model, voice, etc.)
        
        Side Effects:
            - Adds/updates cache entry
            - Logs cache storage event
        """
        cached_audio = CachedAudio(
            audio_bytes=audio_bytes,
            created_at=datetime.utcnow(),
            metadata=metadata,
            cache_key=cache_key
        )
        
        self._cache[cache_key] = cached_audio
        
        logger.info(
            "audio_cached",
            cache_key=cache_key,
            audio_size_bytes=len(audio_bytes),
            metadata_keys=list(metadata.keys()),
            total_cached_items=len(self._cache)
        )

    def get_hit_rate(self) -> float:
        """
        Calculate cache hit rate as percentage.
        
        Returns:
            Hit rate from 0.0 to 1.0 (0% to 100%)
            Returns 0.0 if no cache accesses yet
        """
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def get_cache_stats(self) -> dict:
        """
        Get detailed cache statistics for monitoring.
        
        Returns:
            Dictionary with cache performance metrics:
            - cached_items: Number of items in cache
            - hits: Total cache hits
            - misses: Total cache misses
            - hit_rate: Hit rate percentage (0.0-1.0)
            - total_size_bytes: Total size of cached audio
            - avg_item_size_bytes: Average item size
        """
        total_size = sum(len(cached.audio_bytes) for cached in self._cache.values())
        avg_size = total_size / len(self._cache) if self._cache else 0
        
        return {
            "cached_items": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.get_hit_rate(),
            "total_size_bytes": total_size,
            "avg_item_size_bytes": int(avg_size),
            "ttl_seconds": self._cache_ttl
        }

    def clear_cache(self) -> int:
        """
        Clear all cached audio entries.
        
        Useful for testing or manual cache invalidation.
        
        Returns:
            Number of items removed from cache
        """
        count = len(self._cache)
        self._cache.clear()
        
        logger.info(
            "cache_cleared",
            items_removed=count
        )
        
        return count

    def evict_expired(self) -> int:
        """
        Manually evict all expired cache entries.
        
        Iterates through cache and removes expired items. Normally this
        happens lazily on access, but this method allows proactive cleanup.
        
        Returns:
            Number of expired items removed
        """
        expired_keys = [
            key for key, cached in self._cache.items()
            if cached.is_expired(self._cache_ttl)
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(
                "expired_items_evicted",
                count=len(expired_keys),
                remaining_items=len(self._cache)
            )
        
        return len(expired_keys)
