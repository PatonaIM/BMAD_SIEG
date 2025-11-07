"""In-memory cache for match explanations."""
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import structlog


class CachedExplanation:
    """Cached explanation with TTL."""

    def __init__(self, data: dict[str, Any], ttl_seconds: int):
        """
        Initialize cached explanation.
        
        Args:
            data: Explanation data to cache
            ttl_seconds: Time-to-live in seconds
        """
        self.data = data
        self.cached_at = datetime.utcnow()
        self.expires_at = self.cached_at + timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        """
        Check if cache entry has expired.
        
        Returns:
            True if expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at


class ExplanationCache:
    """
    In-memory cache for match explanations.
    
    Provides caching with TTL to reduce OpenAI API costs by reusing
    explanations that haven't changed. Cache entries are automatically
    invalidated when candidate profiles or job postings are updated.
    """

    def __init__(self):
        """Initialize explanation cache."""
        self._cache: dict[str, CachedExplanation] = {}
        self.logger = structlog.get_logger().bind(service="explanation_cache")

    async def get(self, cache_key: str) -> dict[str, Any] | None:
        """
        Retrieve cached explanation if exists and not expired.
        
        Args:
            cache_key: Cache key in format "explanation:{candidate_id}:{job_id}"
        
        Returns:
            Cached explanation dict or None if not found/expired
        """
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if not cached.is_expired():
                self.logger.info(
                    "cache_hit",
                    cache_key=cache_key,
                    age_seconds=(datetime.utcnow() - cached.cached_at).total_seconds()
                )
                return cached.data
            else:
                # Remove expired entry
                del self._cache[cache_key]
                self.logger.info(
                    "cache_entry_expired",
                    cache_key=cache_key
                )
        return None

    async def set(
        self,
        cache_key: str,
        data: dict[str, Any],
        ttl_seconds: int = 86400
    ) -> None:
        """
        Store explanation in cache with TTL.
        
        Args:
            cache_key: Cache key in format "explanation:{candidate_id}:{job_id}"
            data: Explanation data to cache
            ttl_seconds: Time-to-live in seconds (default: 24 hours)
        """
        self._cache[cache_key] = CachedExplanation(data, ttl_seconds)
        self.logger.info(
            "explanation_cached",
            cache_key=cache_key,
            ttl_seconds=ttl_seconds,
            expires_at=self._cache[cache_key].expires_at.isoformat()
        )

    async def invalidate(
        self,
        candidate_id: UUID | None = None,
        job_id: UUID | None = None
    ) -> int:
        """
        Invalidate cache entries for candidate or job.
        
        Use when candidate profile or job posting is updated to ensure
        fresh explanations are generated.
        
        Args:
            candidate_id: Invalidate all explanations for this candidate
            job_id: Invalidate all explanations involving this job
        
        Returns:
            Number of entries invalidated
        """
        keys_to_remove = []

        for key in self._cache.keys():
            # Cache key format: "explanation:{candidate_id}:{job_id}"
            if candidate_id and f":{candidate_id}:" in key or job_id and f":{job_id}" in key:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            self.logger.info(
                "cache_invalidated",
                count=len(keys_to_remove),
                candidate_id=str(candidate_id) if candidate_id else None,
                job_id=str(job_id) if job_id else None,
                keys=keys_to_remove
            )

        return len(keys_to_remove)

    def get_stats(self) -> dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dict with total_entries, expired_entries, active_entries
        """
        total = len(self._cache)
        expired = sum(1 for cached in self._cache.values() if cached.is_expired())
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired
        }
