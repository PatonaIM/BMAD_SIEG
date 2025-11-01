"""Integration tests for audio processing pipeline."""

import asyncio
import io
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import UploadFile
from httpx import AsyncClient

from app.schemas.speech import TranscriptionResult


class TestAudioProcessingIntegration:
    """Integration tests for complete audio processing pipeline."""

    @pytest.fixture
    def mock_audio_file(self):
        """Create a mock audio file for testing."""
        # Create mock audio content (small MP3-like header)
        audio_content = b'\x00\x00\x00\x20ftypM4A \x00\x00\x00\x00M4A mp42isom\x00\x00\x00'
        
        # Create mock UploadFile
        file_obj = io.BytesIO(audio_content)
        return UploadFile(
            filename="test_audio.mp3",
            file=file_obj,
            size=len(audio_content),
            headers={"content-type": "audio/mp3"}
        )

    @pytest.fixture
    def mock_transcription_result(self):
        """Create a mock transcription result."""
        return TranscriptionResult(
            text="Tell me about your React experience and how you handle state management",
            confidence=0.95,
            duration_seconds=5.2,
            language="en",
            processing_time_ms=1200,
            segments=[
                {
                    "text": "Tell me about your React experience",
                    "start": 0.0,
                    "end": 3.0,
                    "confidence": 0.94
                },
                {
                    "text": "and how you handle state management",
                    "start": 3.0,
                    "end": 5.2,
                    "confidence": 0.96
                }
            ]
        )

    @pytest.fixture
    def mock_interview_response(self):
        """Create a mock interview engine response."""
        return {
            "message_id": str(uuid4()),
            "ai_response": "Can you walk me through a specific example of how you've used Redux?",
            "question_number": 3,
            "total_questions": 15,
            "session_state": {
                "current_difficulty": "standard",
                "skill_boundaries": {"react": "intermediate"}
            },
            "tokens_used": 245
        }

    @pytest.mark.asyncio
    async def test_complete_audio_processing_pipeline(
        self,
        async_client: AsyncClient,
        mock_audio_file,
        mock_transcription_result,
        mock_interview_response,
        mock_candidate,
        mock_interview,
        mock_interview_session
    ):
        """Test complete audio processing pipeline end-to-end."""
        
        # Mock all external dependencies
        with patch("app.services.speech_service.SpeechService.transcribe_candidate_audio") as mock_transcribe, \
             patch("app.services.interview_engine.InterviewEngine.process_candidate_response") as mock_engine, \
             patch("app.repositories.interview.InterviewRepository.get_by_id") as mock_get_interview, \
             patch("app.repositories.interview_session.InterviewSessionRepository.get_by_interview_id") as mock_get_session, \
             patch("app.repositories.interview_message.InterviewMessageRepository.create_message") as mock_create_message, \
             patch("app.repositories.interview_message.InterviewMessageRepository.get_message_count_for_session") as mock_count:
            
            # Setup mocks
            mock_transcribe.return_value = mock_transcription_result
            mock_engine.return_value = mock_interview_response
            mock_get_interview.return_value = mock_interview
            mock_get_session.return_value = mock_interview_session
            mock_count.return_value = 5
            
            # Mock created message
            mock_message = MagicMock()
            mock_message.id = uuid4()
            mock_create_message.return_value = mock_message
            
            # Prepare request
            files = {"audio_file": ("test.mp3", mock_audio_file.file, "audio/mp3")}
            data = {"message_sequence": 6}
            
            # Make request
            response = await async_client.post(
                f"/api/v1/interviews/{mock_interview.id}/audio",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {mock_candidate.auth_token}"}
            )
            
            # Verify response
            assert response.status_code == 200
            response_data = response.json()
            
            assert response_data["transcription"] == mock_transcription_result.text
            assert response_data["confidence"] == mock_transcription_result.confidence
            assert response_data["next_question_ready"] is True
            assert response_data["message_id"] == str(mock_message.id)
            
            # Verify audio metadata
            metadata = response_data["audio_metadata"]
            assert metadata["provider"] == "openai"
            assert metadata["model"] == "whisper-1"
            assert metadata["confidence"] == mock_transcription_result.confidence
            assert metadata["language"] == "en"
            
            # Verify service calls
            mock_transcribe.assert_called_once()
            mock_engine.assert_called_once_with(
                interview_id=mock_interview.id,
                session_id=mock_interview_session.id,
                response_text=mock_transcription_result.text,
                role_type=mock_interview.role_type
            )
            mock_create_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_audio_validation_failure_large_file(
        self,
        async_client: AsyncClient,
        mock_candidate,
        mock_interview
    ):
        """Test audio validation failure for oversized files."""
        
        # Create oversized audio file (>25MB)
        large_content = b"x" * (26 * 1024 * 1024)  # 26MB
        large_file = io.BytesIO(large_content)
        
        files = {"audio_file": ("large.mp3", large_file, "audio/mp3")}
        
        response = await async_client.post(
            f"/api/v1/interviews/{mock_interview.id}/audio",
            files=files,
            headers={"Authorization": f"Bearer {mock_candidate.auth_token}"}
        )
        
        assert response.status_code == 413
        error_data = response.json()["detail"]
        assert error_data["error"] == "AUDIO_FILE_TOO_LARGE"

    @pytest.mark.asyncio
    async def test_audio_validation_failure_invalid_format(
        self,
        async_client: AsyncClient,
        mock_candidate,
        mock_interview
    ):
        """Test audio validation failure for invalid file format."""
        
        # Create text file instead of audio
        text_content = b"This is not an audio file"
        text_file = io.BytesIO(text_content)
        
        files = {"audio_file": ("test.txt", text_file, "text/plain")}
        
        response = await async_client.post(
            f"/api/v1/interviews/{mock_interview.id}/audio",
            files=files,
            headers={"Authorization": f"Bearer {mock_candidate.auth_token}"}
        )
        
        assert response.status_code == 400
        error_data = response.json()["detail"]
        assert error_data["error"] == "INVALID_AUDIO_FORMAT"

    @pytest.mark.asyncio
    async def test_transcription_failure_handling(
        self,
        async_client: AsyncClient,
        mock_audio_file,
        mock_candidate,
        mock_interview,
        mock_interview_session
    ):
        """Test handling of transcription service failures."""
        
        with patch("app.services.speech_service.SpeechService.transcribe_candidate_audio") as mock_transcribe, \
             patch("app.repositories.interview.InterviewRepository.get_by_id") as mock_get_interview, \
             patch("app.repositories.interview_session.InterviewSessionRepository.get_by_interview_id") as mock_get_session:
            
            # Setup mocks
            from app.core.exceptions import TranscriptionFailedError
            mock_transcribe.side_effect = TranscriptionFailedError("OpenAI API unavailable")
            mock_get_interview.return_value = mock_interview
            mock_get_session.return_value = mock_interview_session
            
            files = {"audio_file": ("test.mp3", mock_audio_file.file, "audio/mp3")}
            
            response = await async_client.post(
                f"/api/v1/interviews/{mock_interview.id}/audio",
                files=files,
                headers={"Authorization": f"Bearer {mock_candidate.auth_token}"}
            )
            
            assert response.status_code == 500
            error_data = response.json()["detail"]
            assert error_data["error"] == "TRANSCRIPTION_FAILED"

    @pytest.mark.asyncio
    async def test_low_confidence_transcription(
        self,
        async_client: AsyncClient,
        mock_audio_file,
        mock_candidate,
        mock_interview,
        mock_interview_session
    ):
        """Test handling of low confidence transcriptions."""
        
        # Create low confidence transcription result
        low_confidence_result = TranscriptionResult(
            text="mumble unclear speech",
            confidence=0.3,  # Below threshold
            duration_seconds=2.1,
            language="en",
            processing_time_ms=800,
            segments=[]
        )
        
        with patch("app.services.speech_service.SpeechService.transcribe_candidate_audio") as mock_transcribe, \
             patch("app.repositories.interview.InterviewRepository.get_by_id") as mock_get_interview, \
             patch("app.repositories.interview_session.InterviewSessionRepository.get_by_interview_id") as mock_get_session:
            
            from app.core.exceptions import AudioValidationError
            mock_transcribe.side_effect = AudioValidationError(
                "Transcription confidence 0.30 below minimum 0.60",
                field="confidence"
            )
            mock_get_interview.return_value = mock_interview
            mock_get_session.return_value = mock_interview_session
            
            files = {"audio_file": ("test.mp3", mock_audio_file.file, "audio/mp3")}
            
            response = await async_client.post(
                f"/api/v1/interviews/{mock_interview.id}/audio",
                files=files,
                headers={"Authorization": f"Bearer {mock_candidate.auth_token}"}
            )
            
            assert response.status_code == 422
            error_data = response.json()["detail"]
            assert error_data["error"] == "AUDIO_VALIDATION_FAILED"

    @pytest.mark.asyncio
    async def test_interview_engine_failure_graceful_degradation(
        self,
        async_client: AsyncClient,
        mock_audio_file,
        mock_transcription_result,
        mock_candidate,
        mock_interview,
        mock_interview_session
    ):
        """Test graceful degradation when interview engine fails."""
        
        with patch("app.services.speech_service.SpeechService.transcribe_candidate_audio") as mock_transcribe, \
             patch("app.services.interview_engine.InterviewEngine.process_candidate_response") as mock_engine, \
             patch("app.repositories.interview.InterviewRepository.get_by_id") as mock_get_interview, \
             patch("app.repositories.interview_session.InterviewSessionRepository.get_by_interview_id") as mock_get_session, \
             patch("app.repositories.interview_message.InterviewMessageRepository.create_message") as mock_create_message, \
             patch("app.repositories.interview_message.InterviewMessageRepository.get_message_count_for_session") as mock_count:
            
            # Setup successful transcription but failing engine
            mock_transcribe.return_value = mock_transcription_result
            mock_engine.side_effect = Exception("Interview engine error")
            mock_get_interview.return_value = mock_interview
            mock_get_session.return_value = mock_interview_session
            mock_count.return_value = 3
            
            mock_message = MagicMock()
            mock_message.id = uuid4()
            mock_create_message.return_value = mock_message
            
            files = {"audio_file": ("test.mp3", mock_audio_file.file, "audio/mp3")}
            
            response = await async_client.post(
                f"/api/v1/interviews/{mock_interview.id}/audio",
                files=files,
                headers={"Authorization": f"Bearer {mock_candidate.auth_token}"}
            )
            
            # Should still succeed with transcription, but next_question_ready = False
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["transcription"] == mock_transcription_result.text
            assert response_data["next_question_ready"] is False

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self,
        async_client: AsyncClient,
        mock_audio_file
    ):
        """Test unauthorized access handling."""
        
        files = {"audio_file": ("test.mp3", mock_audio_file.file, "audio/mp3")}
        
        response = await async_client.post(
            f"/api/v1/interviews/{uuid4()}/audio",
            files=files
            # No authorization header
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_interview_not_found(
        self,
        async_client: AsyncClient,
        mock_audio_file,
        mock_candidate
    ):
        """Test handling of non-existent interview."""
        
        with patch("app.repositories.interview.InterviewRepository.get_by_id") as mock_get_interview:
            mock_get_interview.return_value = None
            
            files = {"audio_file": ("test.mp3", mock_audio_file.file, "audio/mp3")}
            
            response = await async_client.post(
                f"/api/v1/interviews/{uuid4()}/audio",
                files=files,
                headers={"Authorization": f"Bearer {mock_candidate.auth_token}"}
            )
            
            assert response.status_code == 404
            error_data = response.json()["detail"]
            assert error_data["error"] == "INTERVIEW_NOT_FOUND"