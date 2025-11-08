"""Realtime Interview Service for managing OpenAI Realtime API WebSocket connections."""

import asyncio
import json
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Callable
from uuid import UUID

import structlog

from app.core.config import settings
from app.models.interview_session import InterviewSession
from app.providers.base_ai_provider import AIProvider
from app.repositories.interview import InterviewRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.utils.realtime_cost import calculate_realtime_cost, check_cost_threshold

if TYPE_CHECKING:
    from app.models.interview import Interview

logger = structlog.get_logger().bind(service="realtime_interview_service")


class RealtimeInterviewService:
    """
    Service for managing OpenAI Realtime API WebSocket interview sessions.
    
    This service orchestrates real-time voice conversations between candidates
    and the AI interviewer using OpenAI's Realtime API. It manages:
    - WebSocket connection lifecycle
    - Audio streaming coordination (bidirectional)
    - Conversation state and context
    - Function calling for answer evaluation
    - Transcript storage and cost tracking
    
    Architecture:
    =============
    Frontend WebSocket ←→ Backend WebSocket Handler ←→ RealtimeInterviewService
                                                      ←→ OpenAI Realtime API
    
    Responsibilities:
    ================
    1. Session Management: Initialize/terminate realtime sessions
    2. Audio Streaming: Coordinate audio flow between frontend and OpenAI
    3. Context Management: Maintain interview context across conversation
    4. Function Handling: Process answer evaluations and determine next questions
    5. Storage: Persist transcripts and metadata to database
    6. Cost Tracking: Monitor and record API usage costs
    
    Usage:
    ======
    >>> service = RealtimeInterviewService(
    ...     ai_provider=ai_provider,
    ...     session_repo=session_repo,
    ...     message_repo=message_repo,
    ...     interview_repo=interview_repo
    ... )
    >>> 
    >>> # Initialize session
    >>> config = await service.initialize_session(
    ...     interview_id=interview_id,
    ...     session_id=session_id
    ... )
    >>> 
    >>> # Handle function calls from OpenAI
    >>> result = await service.handle_function_call(
    ...     function_name="evaluate_candidate_answer",
    ...     arguments={"answer_quality": "good", ...}
    ... )
    """
    
    def __init__(
        self,
        ai_provider: AIProvider,
        session_repo: InterviewSessionRepository,
        message_repo: InterviewMessageRepository,
        interview_repo: InterviewRepository,
    ):
        """
        Initialize Realtime Interview Service.
        
        Args:
            ai_provider: AI provider for question generation context
            session_repo: Repository for session management
            message_repo: Repository for message/transcript storage
            interview_repo: Repository for interview cost tracking
        """
        self.ai_provider = ai_provider
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.interview_repo = interview_repo
        
        logger.info("realtime_interview_service_initialized")
    
    async def commit_transaction(self) -> None:
        """
        Commit the current database transaction.
        
        This ensures that all pending database writes (like transcripts)
        are persisted immediately. Called after each transcript is stored
        to ensure data safety in case of connection drops.
        
        Raises:
            Exception: If commit fails
        """
        # Access the db session from the message repository
        await self.message_repo.db.commit()
        logger.debug("transaction_committed")
    
    async def initialize_session(
        self,
        interview_id: UUID,
        session_id: UUID
    ) -> dict[str, Any]:
        """
        Initialize a realtime interview session with OpenAI configuration.
        
        Loads interview context (job posting, questions, rubric) and prepares
        the session configuration for OpenAI Realtime API connection.
        
        Args:
            interview_id: UUID of the interview
            session_id: UUID of the interview session
        
        Returns:
            Dict containing OpenAI Realtime API session configuration:
                - model: gpt-4o-realtime-preview-2024-10-01
                - modalities: ["text", "audio"]
                - voice: "alloy"
                - instructions: System prompt with interview context
                - tools: Function definitions for answer evaluation
                - turn_detection: Server VAD configuration
                - temperature: 0.7
                - max_response_output_tokens: 1000
        
        Raises:
            ValueError: If session not found
        """
        logger.info(
            "initializing_realtime_session",
            interview_id=str(interview_id),
            session_id=str(session_id)
        )
        
        # Load session
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Load interview for context
        interview = await self.interview_repo.get_by_id(interview_id)
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")
        
        # Build system instructions with interview context
        instructions = await self._build_system_instructions(
            session=session,
            role_type=interview.role_type,
            interview=interview  # Pass interview for job context
        )
        
        # Define function tools for answer evaluation
        tools = self._get_function_definitions()
        
        # Build OpenAI Realtime API configuration using settings
        config = {
            "model": settings.realtime_api_model,
            "modalities": ["text", "audio"],
            "voice": settings.realtime_voice,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": settings.openai_stt_model
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,  # Balanced sensitivity - reduced false positives from echo/noise
                "prefix_padding_ms": 300,
                "silence_duration_ms": 1200  # 1.2 seconds - responsive but prevents AI from jumping in too quickly
            },
            "tools": tools,
            "instructions": instructions,
            "temperature": settings.realtime_temperature,
            "max_response_output_tokens": settings.realtime_max_response_tokens
        }
        
        logger.info(
            "realtime_session_initialized",
            interview_id=str(interview_id),
            session_id=str(session_id),
            instructions_length=len(instructions)
        )
        
        return config
    
    async def _build_system_instructions(
        self,
        session: InterviewSession,
        role_type: str,
        interview: "Interview"  # NEW: Pass interview for job context
    ) -> str:
        """
        Build system instructions for the AI interviewer.
        
        Creates a comprehensive prompt using InterviewEngine's system prompt
        generator, enhanced with current conversation context and job-specific details.
        
        Args:
            session: Interview session with current state
            role_type: Role being interviewed for (e.g., "react", "python")
            interview: Interview model instance for job context lookup
        
        Returns:
            System instructions string for OpenAI Realtime API
        """
        # Import here to avoid circular dependency
        from app.services.interview_engine import InterviewEngine
        
        # Fetch job_posting if job_posting_id exists (for job-context-aware interviews)
        job_posting = None
        if interview.job_posting_id:
            job_posting = await self.interview_repo.db.execute(
                f"SELECT * FROM job_postings WHERE id = '{interview.job_posting_id}'"
            )
            # Actually, let's use the relationship
            if interview.job_posting:
                job_posting = interview.job_posting
                logger.info(
                    "job_posting_loaded_for_context",
                    interview_id=str(interview.id),
                    job_posting_id=str(job_posting.id),
                    job_title=job_posting.title,
                )
        
        # Generate base system prompt (contains full interview guidelines)
        # Now includes job-specific context if available
        base_prompt = InterviewEngine.get_realtime_system_prompt(
            None,  # No need for instance, it's a method we can call statically
            role_type=role_type,
            session=session,
            job_posting=job_posting  # NEW: Pass job context
        )
        
        # Load recent conversation history for context
        messages = await self.message_repo.get_by_session_id(session.id)
        
        # If this is the start of the interview (no messages yet), add explicit first message instruction
        if not messages or len(messages) == 0:
            initial_instruction = f"""

---

**CRITICAL: THIS IS THE START OF THE INTERVIEW - READ THIS CAREFULLY**

You are beginning the interview right now. The candidate has just connected and is waiting for you to speak first.

**YOUR IMMEDIATE TASK (DO ONLY THIS IN YOUR FIRST RESPONSE):**

Say ONLY the greeting and overview, ending with "Are you ready to begin?" - then STOP TALKING.

**EXACT TEXT TO SAY (and nothing more):**

"Hi! Thanks for joining today. I'm excited to learn about your experience with {role_type}. Let me give you a quick overview of what to expect. We'll go through about 12 to 20 technical questions tailored to your skill level, and this should take approximately 20 to 30 minutes. I'll adjust the difficulty based on your responses as we go. This is a conversation, not a test to trick you, so feel free to think out loud and ask for clarification whenever you need it. Are you ready to begin?"

**AFTER SAYING THE ABOVE:**

1. **STOP SPEAKING IMMEDIATELY** - Do not say anything else
2. **WAIT FOR THE CANDIDATE** - They need to respond with "yes", "ready", "sure", etc.
3. **DO NOT ask any technical questions yet** - You haven't started the interview questions yet
4. **DO NOT continue speaking** - Your turn is over after asking if they're ready
5. **DO NOT answer your own question** - Let the candidate speak
6. **DO NOT assume silence means they're ready** - Wait for actual words

**ONLY AFTER** you hear the candidate confirm they're ready (in their next message to you), you can then say "Great! Let's begin with our first question..." and ask your first technical question.

Current state: questions_asked = {session.questions_asked_count}
"""
            base_prompt += initial_instruction
        elif messages and len(messages) > 0:
            # Append conversation context if exists
            conversation_context = "\n\n## Recent Conversation Context\n\n"
            for msg in messages[-5:]:  # Last 5 messages for context
                role = "AI" if msg.message_type == "ai_question" else "Candidate"
                conversation_context += f"**{role}**: {msg.content_text}\n\n"
            
            base_prompt += conversation_context
        
        return base_prompt
    
    def _get_function_definitions(self) -> list[dict[str, Any]]:
        """
        Get function definitions for OpenAI Realtime API.
        
        Defines the evaluate_candidate_answer function that the AI can call
        to evaluate responses and determine conversation flow.
        
        Returns:
            List of function definition dictionaries for OpenAI tools
        """
        return [
            {
                "type": "function",
                "name": "evaluate_candidate_answer",
                "description": "Evaluate the candidate's answer quality, assess their skill proficiency, and determine the next action in the interview",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "answer_quality": {
                            "type": "string",
                            "enum": ["excellent", "good", "needs_clarification", "off_topic"],
                            "description": "Overall quality assessment of the candidate's answer"
                        },
                        "key_points_covered": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key technical points mentioned by the candidate"
                        },
                        "skill_area": {
                            "type": "string",
                            "description": "The specific skill area being assessed (e.g., 'react_hooks', 'state_management', 'async_programming', 'python_basics', 'data_structures')"
                        },
                        "proficiency_level": {
                            "type": "string",
                            "enum": ["novice", "intermediate", "proficient", "expert"],
                            "description": "Assessed proficiency level for this skill area based on the answer"
                        },
                        "next_action": {
                            "type": "string",
                            "enum": ["continue", "follow_up", "move_to_next_topic"],
                            "description": "What to do next in the interview"
                        },
                        "follow_up_needed": {
                            "type": "boolean",
                            "description": "Whether a follow-up question is needed for clarification"
                        }
                    },
                    "required": ["answer_quality", "key_points_covered", "next_action", "follow_up_needed"]
                }
            }
        ]
    
    async def handle_function_call(
        self,
        function_name: str,
        arguments: dict[str, Any],
        session_id: UUID,
        interview_id: UUID
    ) -> dict[str, Any]:
        """
        Handle function calls from OpenAI Realtime API.
        
        Processes answer evaluations and updates interview state accordingly.
        
        Args:
            function_name: Name of the function called
            arguments: Function arguments from OpenAI
            session_id: UUID of the interview session
            interview_id: UUID of the interview
        
        Returns:
            Dict with function result to send back to OpenAI
        
        Raises:
            ValueError: If function_name is not supported
        """
        logger.info(
            "handling_function_call",
            function_name=function_name,
            session_id=str(session_id),
            interview_id=str(interview_id)
        )
        
        # Handle correct spelling and common typo from OpenAI
        if function_name in ["evaluate_candidate_answer", "evaulate_candidate_answer"]:
            if function_name == "evaulate_candidate_answer":
                logger.warning(
                    "function_name_typo_detected",
                    function_name=function_name,
                    corrected_to="evaluate_candidate_answer"
                )
            return await self._handle_answer_evaluation(
                arguments=arguments,
                session_id=session_id,
                interview_id=interview_id
            )
        else:
            raise ValueError(f"Unknown function: {function_name}")
    
    async def _handle_answer_evaluation(
        self,
        arguments: dict[str, Any],
        session_id: UUID,
        interview_id: UUID
    ) -> dict[str, Any]:
        """
        Handle answer evaluation function call.
        
        Stores evaluation results, updates session state, and tracks skill boundaries.
        
        Args:
            arguments: Evaluation arguments from OpenAI
            session_id: UUID of the interview session
            interview_id: UUID of the interview
        
        Returns:
            Dict confirming evaluation was recorded
        """
        logger.info(
            "evaluating_candidate_answer",
            answer_quality=arguments.get("answer_quality"),
            skill_area=arguments.get("skill_area"),
            proficiency_level=arguments.get("proficiency_level"),
            next_action=arguments.get("next_action"),
            session_id=str(session_id)
        )
        
        # Store evaluation in the most recent candidate message
        messages = await self.message_repo.get_by_session_id(session_id)
        if messages:
            latest_candidate_msg = next(
                (m for m in reversed(messages) if m.message_type == "candidate_response"),
                None
            )
            
            if latest_candidate_msg:
                # Update message metadata with evaluation
                # Access the message_metadata column (not .metadata)
                import json
                
                if latest_candidate_msg.message_metadata:
                    # Convert JSONB to dict - use json.loads if it's a string, or direct access
                    try:
                        metadata = json.loads(latest_candidate_msg.message_metadata) if isinstance(latest_candidate_msg.message_metadata, str) else dict(latest_candidate_msg.message_metadata)
                    except (TypeError, json.JSONDecodeError):
                        # Fallback: treat as dict-like object
                        metadata = dict(latest_candidate_msg.message_metadata) if hasattr(latest_candidate_msg.message_metadata, '__iter__') else {}
                else:
                    metadata = {}
                    
                metadata["evaluation"] = {
                    "answer_quality": arguments.get("answer_quality"),
                    "key_points_covered": arguments.get("key_points_covered", []),
                    "skill_area": arguments.get("skill_area"),
                    "proficiency_level": arguments.get("proficiency_level"),
                    "next_action": arguments.get("next_action"),
                    "follow_up_needed": arguments.get("follow_up_needed"),
                    "evaluated_at": datetime.utcnow().isoformat()
                }
                
                # Update message directly
                latest_candidate_msg.message_metadata = metadata
                await self.message_repo.db.flush()
        
        # Update session skill boundaries if skill_area and proficiency_level provided
        skill_area = arguments.get("skill_area")
        proficiency_level = arguments.get("proficiency_level")
        
        if skill_area and proficiency_level:
            session = await self.session_repo.get_by_id(session_id)
            if session:
                # Get current skill boundaries or initialize empty dict
                skill_boundaries = session.skill_boundaries_identified or {}
                
                # Update or add this skill boundary
                skill_boundaries[skill_area] = proficiency_level
                
                # Update session
                session.skill_boundaries_identified = skill_boundaries
                await self.session_repo.db.flush()
                
                logger.info(
                    "skill_boundary_updated",
                    session_id=str(session_id),
                    skill_area=skill_area,
                    proficiency_level=proficiency_level,
                    total_boundaries=len(skill_boundaries)
                )
        
        return {
            "success": True,
            "message": "Answer evaluation recorded",
            "skill_boundary_updated": bool(skill_area and proficiency_level)
        }
    
    async def store_transcript(
        self,
        interview_id: UUID,
        session_id: UUID,
        message_type: str,
        transcript: str,
        audio_metadata: dict[str, Any] | None = None
    ) -> UUID:
        """
        Store transcript from realtime conversation.
        
        Args:
            interview_id: UUID of the interview
            session_id: UUID of the interview session
            message_type: "ai_question" or "candidate_response"
            transcript: Text transcript from Realtime API
            audio_metadata: Optional metadata about audio (latency, duration, etc.)
        
        Returns:
            UUID of created message
        """
        logger.info(
            "storing_realtime_transcript",
            interview_id=str(interview_id),
            message_type=message_type,
            transcript_length=len(transcript)
        )
        
        # Get next sequence number
        message_count = await self.message_repo.get_message_count_for_session(session_id)
        sequence_number = message_count + 1
        
        # Create message record
        message = await self.message_repo.create_message(
            interview_id=interview_id,
            session_id=session_id,
            sequence_number=sequence_number,
            message_type=message_type,
            content_text=transcript,
            audio_metadata={
                "source": "realtime_api",
                "audio_metadata": audio_metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(
            "realtime_transcript_stored",
            message_id=str(message.id),
            interview_id=str(interview_id)
        )
        
        return message.id
    
    async def track_usage_and_cost(
        self,
        interview_id: UUID,
        input_audio_seconds: float,
        output_audio_seconds: float,
        input_text_tokens: int,
        output_text_tokens: int
    ) -> Decimal:
        """
        Track Realtime API usage and update interview cost.
        
        Calculates cost based on audio duration and text tokens, then
        updates the interview's realtime_cost_usd field. Logs alerts
        if cost exceeds threshold ($5).
        
        Args:
            interview_id: UUID of the interview
            input_audio_seconds: Duration of input audio (candidate speaking)
            output_audio_seconds: Duration of output audio (AI speaking)
            input_text_tokens: Number of input text tokens
            output_text_tokens: Number of output text tokens
        
        Returns:
            Total accumulated cost for this interview in USD
        
        Example:
            >>> # Track 30 seconds of conversation
            >>> cost = await service.track_usage_and_cost(
            ...     interview_id=interview_id,
            ...     input_audio_seconds=15.0,
            ...     output_audio_seconds=15.0,
            ...     input_text_tokens=150,
            ...     output_text_tokens=200
            ... )
        """
        # Calculate cost for this exchange
        cost_breakdown = calculate_realtime_cost(
            input_audio_seconds=input_audio_seconds,
            output_audio_seconds=output_audio_seconds,
            input_text_tokens=input_text_tokens,
            output_text_tokens=output_text_tokens
        )
        
        logger.info(
            "realtime_usage_tracked",
            interview_id=str(interview_id),
            input_audio_seconds=input_audio_seconds,
            output_audio_seconds=output_audio_seconds,
            input_tokens=input_text_tokens,
            output_tokens=output_text_tokens,
            exchange_cost=str(cost_breakdown.total_cost)
        )
        
        # Load current interview cost
        interview = await self.interview_repo.get_by_id(interview_id)
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")
        
        # Update accumulated cost
        current_realtime_cost = interview.realtime_cost_usd or Decimal("0.0")
        new_realtime_cost = current_realtime_cost + cost_breakdown.total_cost
        
        await self.interview_repo.update(
            interview_id=interview_id,
            realtime_cost_usd=new_realtime_cost
        )
        
        # Check for cost threshold alert
        if check_cost_threshold(new_realtime_cost, threshold=Decimal("5.0")):
            logger.warning(
                "realtime_cost_threshold_exceeded",
                interview_id=str(interview_id),
                current_cost=str(new_realtime_cost),
                threshold="5.00"
            )
        
        logger.info(
            "realtime_cost_updated",
            interview_id=str(interview_id),
            total_cost=str(new_realtime_cost)
        )
        
        return new_realtime_cost
