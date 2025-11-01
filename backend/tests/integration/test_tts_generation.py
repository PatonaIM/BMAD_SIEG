"""Integration tests for TTS (Text-to-Speech) generation."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.audio_cache_service import AudioCacheService
from app.services.speech_service import SpeechService


class TestTTSGeneration:
    """Test suite for TTS audio generation functionality."""

    @pytest.fixture
    def mock_audio_bytes(self):
        """Mock MP3 audio bytes."""
        return b"fake_mp3_audio_data_12345" * 100  # Simulate audio data

    @pytest.fixture
    def mock_tts_metadata(self):
        """Mock TTS generation metadata."""
        return {
            "file_size_bytes": 2500,
            "generation_time_ms": 1240,
            "character_count": 125,
            "model": "tts-1",
            "voice": "alloy",
            "speed": 0.95
        }

    @pytest.fixture
    def audio_cache(self):
        """Create audio cache service instance."""
        return AudioCacheService(ttl_seconds=3600)

    @pytest.fixture
    async def mock_speech_provider(self, mock_audio_bytes, mock_tts_metadata):
        """Mock speech provider that returns audio bytes and metadata."""
        provider = AsyncMock()
        provider.synthesize_speech = AsyncMock(
            return_value=(mock_audio_bytes, mock_tts_metadata)
        )
        return provider

    @pytest.fixture
    async def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    async def speech_service(
        self, mock_speech_provider, mock_db_session, audio_cache
    ):
        """Create SpeechService with mocked dependencies."""
        with patch("app.services.speech_service.InterviewRepository"), \
             patch("app.services.speech_service.InterviewMessageRepository"), \
             patch("app.services.speech_service.SpeechCostCalculator"):
            
            service = SpeechService(
                speech_provider=mock_speech_provider,
                db=mock_db_session,
                audio_cache=audio_cache
            )
            
            # Mock the cost update method
            service._update_interview_speech_cost = AsyncMock()
            
            return service

    async def test_generate_audio_success(
        self, speech_service, mock_audio_bytes, mock_tts_metadata
    ):
        """Test successful TTS audio generation."""
        text = "Tell me about your experience with React."
        interview_id = uuid4()
        voice = "alloy"
        speed = 0.95

        audio_bytes, metadata = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id,
            voice=voice,
            speed=speed
        )

        # Verify audio bytes returned
        assert audio_bytes == mock_audio_bytes
        assert len(audio_bytes) > 0

        # Verify metadata structure
        assert "provider" in metadata
        assert metadata["provider"] == "openai"
        assert metadata["voice"] == voice
        assert metadata["speed"] == speed
        assert metadata["character_count"] == len(text)
        assert "cached" in metadata
        assert metadata["cached"] is False  # First generation

        # Verify cost tracking was called
        assert speech_service._update_interview_speech_cost.called

    async def test_audio_caching_hit(
        self, speech_service, mock_audio_bytes, mock_tts_metadata
    ):
        """Test that second request for same audio hits cache."""
        text = "Can you explain closures in JavaScript?"
        interview_id = uuid4()

        # First generation (cache miss)
        audio1, metadata1 = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id
        )

        assert metadata1["cached"] is False
        assert audio1 == mock_audio_bytes

        # Second generation (should hit cache)
        audio2, metadata2 = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id
        )

        assert metadata2["cached"] is True
        assert audio2 == mock_audio_bytes
        
        # Cost should only be charged once
        assert speech_service._update_interview_speech_cost.call_count == 1

    async def test_cache_key_generation(self, audio_cache):
        """Test cache key generation is deterministic."""
        text = "Test question"
        voice = "alloy"
        speed = 0.95

        key1 = audio_cache.get_cache_key(text, voice, speed)
        key2 = audio_cache.get_cache_key(text, voice, speed)

        # Same inputs produce same key
        assert key1 == key2

        # Different inputs produce different keys
        key3 = audio_cache.get_cache_key(text, "nova", speed)
        assert key1 != key3

    async def test_cache_expiration(self, audio_cache, mock_audio_bytes):
        """Test that expired cache entries are not returned."""
        # Use very short TTL for testing
        cache = AudioCacheService(ttl_seconds=1)
        
        cache_key = cache.get_cache_key("test", "alloy", 1.0)
        metadata = {"test": "data"}
        
        # Cache the audio
        await cache.cache_audio(cache_key, mock_audio_bytes, metadata)
        
        # Should hit cache immediately
        cached = await cache.get_cached_audio(cache_key)
        assert cached is not None
        assert cached.audio_bytes == mock_audio_bytes
        
        # Wait for expiration
        import asyncio
        await asyncio.sleep(1.5)
        
        # Should miss cache after expiration
        cached_expired = await cache.get_cached_audio(cache_key)
        assert cached_expired is None

    async def test_cache_stats_tracking(self, audio_cache, mock_audio_bytes):
        """Test cache hit/miss statistics tracking."""
        metadata = {"test": "data"}
        
        # Initial stats
        stats = audio_cache.get_cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0.0
        
        # Cache miss
        await audio_cache.get_cached_audio("nonexistent_key")
        stats = audio_cache.get_cache_stats()
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.0
        
        # Cache a value
        cache_key = audio_cache.get_cache_key("test", "alloy", 1.0)
        await audio_cache.cache_audio(cache_key, mock_audio_bytes, metadata)
        
        # Cache hit
        await audio_cache.get_cached_audio(cache_key)
        stats = audio_cache.get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5  # 1 hit, 1 miss = 50%

    async def test_different_voices_not_cached_together(
        self, speech_service, mock_audio_bytes
    ):
        """Test that different voices generate separate cache entries."""
        text = "Test question"
        interview_id = uuid4()

        # Generate with 'alloy' voice
        audio1, meta1 = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id,
            voice="alloy"
        )

        # Generate with 'nova' voice
        audio2, meta2 = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id,
            voice="nova"
        )

        # Both should be cache misses (different cache keys)
        assert meta1["cached"] is False
        assert meta2["cached"] is False
        
        # Cost should be charged twice
        assert speech_service._update_interview_speech_cost.call_count == 2

    async def test_different_speeds_not_cached_together(
        self, speech_service, mock_audio_bytes
    ):
        """Test that different speeds generate separate cache entries."""
        text = "Test question"
        interview_id = uuid4()

        # Generate with speed 0.95
        audio1, meta1 = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id,
            speed=0.95
        )

        # Generate with speed 1.2
        audio2, meta2 = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id,
            speed=1.2
        )

        # Both should be cache misses
        assert meta1["cached"] is False
        assert meta2["cached"] is False
        
        # Cost should be charged twice
        assert speech_service._update_interview_speech_cost.call_count == 2

    @pytest.mark.parametrize("text", [
        "Tell me about your experience with React and how you handle state management.",
        "Can you explain the difference between SQL and NoSQL databases?",
        "Describe a challenging bug you encountered and how you resolved it.",
        "What is your approach to writing unit tests for a REST API?",
    ])
    async def test_sample_questions(self, speech_service, text):
        """Test TTS generation with realistic interview questions."""
        interview_id = uuid4()

        audio_bytes, metadata = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id
        )

        # Verify audio was generated
        assert audio_bytes is not None
        assert len(audio_bytes) > 0

        # Verify metadata
        assert metadata["character_count"] == len(text)
        assert metadata["voice"] == "alloy"
        assert metadata["speed"] == 0.95

    async def test_long_text_handling(self, speech_service):
        """Test handling of text near the 4096 character limit."""
        # Create text just under the limit
        text = "A" * 4090
        interview_id = uuid4()

        audio_bytes, metadata = await speech_service.generate_ai_speech(
            text=text,
            interview_id=interview_id
        )

        assert audio_bytes is not None
        assert metadata["character_count"] == 4090


class TestAudioCacheService:
    """Test suite for AudioCacheService functionality."""

    def test_cache_initialization(self):
        """Test cache service initialization."""
        cache = AudioCacheService(ttl_seconds=7200)
        
        assert cache._cache_ttl == 7200
        assert len(cache._cache) == 0
        assert cache._hits == 0
        assert cache._misses == 0

    async def test_cache_clear(self):
        """Test clearing all cache entries."""
        cache = AudioCacheService()
        
        # Add some entries
        await cache.cache_audio("key1", b"audio1", {"test": 1})
        await cache.cache_audio("key2", b"audio2", {"test": 2})
        
        assert len(cache._cache) == 2
        
        # Clear cache
        count = cache.clear_cache()
        
        assert count == 2
        assert len(cache._cache) == 0

    async def test_evict_expired_entries(self):
        """Test manual eviction of expired entries."""
        cache = AudioCacheService(ttl_seconds=1)
        
        # Add entries
        await cache.cache_audio("key1", b"audio1", {"test": 1})
        await cache.cache_audio("key2", b"audio2", {"test": 2})
        
        assert len(cache._cache) == 2
        
        # Wait for expiration
        import asyncio
        await asyncio.sleep(1.5)
        
        # Manually evict expired
        count = cache.evict_expired()
        
        assert count == 2
        assert len(cache._cache) == 0
