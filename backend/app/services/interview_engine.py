"""Interview Engine service for managing AI-powered interviews."""
import asyncio
import uuid
from datetime import datetime
from decimal import Decimal
from uuid import UUID

import structlog

from app.core.exceptions import (
    InterviewAbandonedException,
    InterviewCompletedException,
    InterviewNotFoundException,
)
from app.models.interview_message import InterviewMessage
from app.models.interview_session import InterviewSession
from app.providers.base_ai_provider import AIProvider
from app.repositories.interview import InterviewRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.services.conversation_memory import ConversationMemoryManager
from app.services.progressive_assessment_engine import DifficultyLevel, ProgressiveAssessmentEngine

logger = structlog.get_logger().bind(service="interview_engine")


class InterviewEngine:
    """
    Main interview orchestration service.
    
    Manages interview flow, integrates with ProgressiveAssessmentEngine
    for adaptive difficulty adjustment, and coordinates with AI provider
    for response analysis and question generation.
    
    Attributes:
        ai_provider: AI provider for completions and analysis
        session_repo: Repository for interview session management
        message_repo: Repository for message persistence
    """

    def __init__(
        self,
        ai_provider: AIProvider,
        session_repo: InterviewSessionRepository,
        message_repo: InterviewMessageRepository,
        interview_repo: InterviewRepository | None = None,
    ):
        """
        Initialize Interview Engine with dependencies.

        Args:
            ai_provider: OpenAI provider from Story 1.4
            session_repo: Session management repository
            message_repo: Message persistence repository
            interview_repo: Interview repository for token tracking (optional)
        """
        self.ai_provider = ai_provider
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.interview_repo = interview_repo

        # Initialize Progressive Assessment Engine
        self.assessment_engine = ProgressiveAssessmentEngine(ai_provider=self.ai_provider)

        # Initialize Conversation Memory Manager
        self.memory_manager = ConversationMemoryManager()

        logger.info("interview_engine_initialized")

    async def start_interview(
        self,
        candidate_id: UUID,
        role_type: str
    ) -> InterviewSession:
        """
        Start a new interview session.
        
        Creates initial session with warmup difficulty level and
        initializes progression state for adaptive assessment.

        Args:
            candidate_id: UUID of the candidate
            role_type: Type of role interview (e.g., "react", "python")

        Returns:
            Newly created InterviewSession with initialized state

        Side Effects:
            Creates InterviewSession record in database with:
            - initial difficulty: warmup
            - empty progression_state with initialized structure
            - empty conversation_memory
        """
        logger.info(
            "starting_interview",
            candidate_id=str(candidate_id),
            role_type=role_type
        )

        # Create new interview session
        new_session = InterviewSession(
            interview_id=candidate_id,  # This would normally be interview.id, using candidate_id as placeholder
            current_difficulty_level="warmup",
            questions_asked_count=0,
            skill_boundaries_identified={},
            progression_state={
                "phase_history": [
                    {
                        "phase": "warmup",
                        "started_at": datetime.utcnow().isoformat(),
                        "questions_count": 0
                    }
                ],
                "response_quality_history": [],
                "skills_explored": [],
                "skills_pending": [],
                "boundary_detections": []
            },
            conversation_memory={
                "messages": [],
                "memory_metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat(),
                    "message_count": 0,
                    "truncation_count": 0
                }
            },
            last_activity_at=datetime.utcnow()
        )

        # Save to database
        created_session = await self.session_repo.create(new_session)

        logger.info(
            "interview_started",
            session_id=str(created_session.id),
            candidate_id=str(candidate_id),
            initial_difficulty="warmup"
        )

        return created_session

    async def process_candidate_response(
        self,
        interview_id: UUID,
        session_id: UUID,
        response_text: str,
        role_type: str
    ) -> dict:
        """
        Process candidate response and generate next AI question.
        
        Workflow:
        1. Load interview session from database
        2. Validate interview is in progress
        3. Save candidate message to database
        4. Deserialize conversation memory from JSONB
        5. Add candidate response to LangChain memory
        6. Analyze response quality using ProgressiveAssessmentEngine
        7. Update skill boundaries and progression state
        8. Determine next difficulty level
        9. Generate next AI question with context
        10. Save AI question message to database
        11. Serialize updated memory back to JSONB
        12. Update session state and persist changes

        Args:
            interview_id: UUID of the interview
            session_id: UUID of the interview session
            response_text: Candidate's text response
            role_type: Interview role type (e.g., "react", "python")

        Returns:
            Dict containing:
                - message_id: UUID of created candidate message
                - ai_response: Next AI question text
                - question_number: Current question number
                - total_questions: Estimated total questions (12-20)
                - session_state: Progression state for frontend
                - tokens_used: Tokens consumed in this interaction

        Raises:
            InterviewNotFoundException: If session not found
            OpenAIProviderError: If AI operations fail
        """
        start_time = datetime.utcnow()

        logger.info(
            "processing_candidate_response",
            interview_id=str(interview_id),
            session_id=str(session_id),
            response_length=len(response_text)
        )

        # Load session
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise InterviewNotFoundException(f"Session {session_id} not found")

        # Load interview to check status
        if self.interview_repo:
            interview = await self.interview_repo.get_by_id(interview_id)
            if interview:
                if interview.status == "completed":
                    raise InterviewCompletedException(
                        f"Interview {interview_id} is already completed"
                    )
                elif interview.status == "abandoned":
                    raise InterviewAbandonedException(
                        f"Interview {interview_id} was abandoned"
                    )

        # Get current sequence number
        current_sequence = await self.message_repo.get_message_count_for_session(session_id)
        candidate_sequence = current_sequence + 1

        # Save candidate response message
        candidate_message = InterviewMessage(
            id=uuid.uuid4(),
            interview_id=interview_id,
            session_id=session_id,
            sequence_number=candidate_sequence,
            message_type="candidate_response",
            content_text=response_text,
            created_at=datetime.utcnow()
        )
        await self.message_repo.create(candidate_message)

        # Update last activity timestamp
        await self.session_repo.update_last_activity(session_id, datetime.utcnow())

        # Deserialize conversation memory
        memory_dict = session.conversation_memory or {"messages": [], "metadata": {}}
        langchain_memory = self.memory_manager.deserialize_memory(memory_dict)

        # Add candidate response to memory
        langchain_memory.chat_memory.add_user_message(response_text)

        # Get current difficulty and progression state
        current_difficulty = self.assessment_engine.get_current_phase(session)

        # Analyze response quality
        last_messages = memory_dict.get("messages", [])
        last_question = ""
        for msg in reversed(last_messages):
            if msg.get("role") == "assistant":
                last_question = msg.get("content", "")
                break

        question_context = {
            "question": last_question,
            "role_type": role_type,
            "difficulty_level": current_difficulty.value,
            "skill_area": "general"
        }

        # PERFORMANCE OPTIMIZATION: Parallelize response analysis and question generation
        # Response analysis examines the past, question generation looks forward
        # These are independent operations that can run concurrently
        skill_area = question_context.get("skill_area", "general")

        # Create concurrent tasks for analysis and question generation
        analysis_task = self.assessment_engine.analyze_response_quality(
            response_text=response_text,
            question_context=question_context
        )

        # Note: We'll generate question in parallel AFTER we have the analysis
        # for now, to maintain quality. Future optimization: predictive question pre-generation
        analysis = await analysis_task

        logger.info(
            "response_analyzed",
            session_id=str(session_id),
            confidence=analysis.confidence_level,
            accuracy=analysis.technical_accuracy
        )

        # PARALLEL EXECUTION: Run boundary detection, difficulty determination, and question generation concurrently
        # These operations read from session state and don't depend on each other's results
        boundary_task = self.assessment_engine.detect_skill_boundaries(
            session=session,
            skill_area=skill_area,
            analysis=analysis
        )

        difficulty_task = self.assessment_engine.determine_next_difficulty(
            session=session,
            analysis=analysis
        )

        # Increment question count now so question generation has correct count
        await self.session_repo.increment_question_count(session_id)
        session.questions_asked_count += 1

        question_task = self.assessment_engine.generate_next_question(
            session=session,
            role_type=role_type
        )

        # Wait for all three operations to complete in parallel
        proficiency_level, next_difficulty, question_data = await asyncio.gather(
            boundary_task,
            difficulty_task,
            question_task
        )

        logger.info(
            "parallel_assessment_complete",
            session_id=str(session_id),
            next_difficulty=next_difficulty.value,
            proficiency_level=proficiency_level
        )

        # Update progression state with response data
        self.assessment_engine.update_progression_state(
            session=session,
            update_data={
                "type": "response",
                "data": {
                    "question_num": session.questions_asked_count - 1,  # Before increment
                    "confidence": analysis.confidence_level,
                    "accuracy": analysis.technical_accuracy,
                    "proficiency": analysis.proficiency_signal
                }
            }
        )

        # If difficulty changed, record transition
        if next_difficulty != current_difficulty:
            self.assessment_engine.update_progression_state(
                session=session,
                update_data={
                    "type": "phase_change",
                    "data": {
                        "phase": next_difficulty.value
                    }
                }
            )

        # Update skill boundaries
        session.skill_boundaries_identified = session.skill_boundaries_identified or {}
        session.skill_boundaries_identified[skill_area] = proficiency_level

        # Add AI question to memory
        langchain_memory.chat_memory.add_ai_message(question_data["question"])

        # Save AI question message
        ai_sequence = candidate_sequence + 1
        ai_message = InterviewMessage(
            id=uuid.uuid4(),
            interview_id=interview_id,
            session_id=session_id,
            sequence_number=ai_sequence,
            message_type="ai_question",
            content_text=question_data["question"],
            message_metadata={
                "skill_area": question_data.get("skill_area"),
                "difficulty_level": next_difficulty.value,
                "is_followup": question_data.get("is_followup", False)
            },
            created_at=datetime.utcnow()
        )
        await self.message_repo.create(ai_message)

        # Serialize updated memory back to JSONB
        updated_memory_dict = self.memory_manager.serialize_memory(langchain_memory)

        # Check if truncation needed
        if self.memory_manager.should_truncate(updated_memory_dict):
            logger.warning(
                "truncating_conversation_memory",
                session_id=str(session_id),
                message_count=updated_memory_dict["metadata"]["message_count"]
            )
            updated_memory_dict = self.memory_manager.truncate_memory(updated_memory_dict)

        # PERFORMANCE OPTIMIZATION: Batch database writes in parallel
        # These operations are independent and can run concurrently
        update_tasks = [
            self.session_repo.update_session_state(
                session=session,
                conversation_memory=updated_memory_dict,
                skill_boundaries=session.skill_boundaries_identified,
                progression_state=session.progression_state
            )
        ]

        # Track token usage if interview_repo available
        tokens_used = updated_memory_dict["metadata"].get("token_count", 0)
        if self.interview_repo and tokens_used > 0:
            # Calculate cost (simplified - would use actual model pricing)
            cost_per_token = Decimal("0.0000015")  # Example for gpt-4o-mini
            cost_usd = Decimal(tokens_used) * cost_per_token
            update_tasks.append(
                self.interview_repo.update_token_usage(
                    interview_id=interview_id,
                    tokens_used=tokens_used,
                    cost_usd=cost_usd
                )
            )

        # Execute all updates in parallel
        await asyncio.gather(*update_tasks)

        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(
            "candidate_response_processed",
            session_id=str(session_id),
            next_difficulty=next_difficulty.value,
            questions_asked=session.questions_asked_count,
            processing_time_ms=processing_time,
            tokens_used=tokens_used
        )

        # Check if interview should be completed
        should_complete = await self._should_complete_interview(session)

        # Determine total questions estimate (12-20 range)
        total_questions = 15  # Default estimate
        if session.questions_asked_count < 5:
            total_questions = 15
        elif next_difficulty == DifficultyLevel.ADVANCED:
            total_questions = 18

        return {
            "message_id": candidate_message.id,
            "ai_response": question_data["question"],
            "question_number": session.questions_asked_count,
            "total_questions": total_questions,
            "session_state": {
                "current_difficulty": next_difficulty.value,
                "skill_boundaries": session.skill_boundaries_identified,
                "questions_asked": session.questions_asked_count
            },
            "tokens_used": tokens_used,
            "interview_complete": should_complete
        }

    async def _should_complete_interview(self, session: InterviewSession) -> bool:
        """
        Determine if interview should be completed based on criteria.
        
        Completion criteria:
        - Minimum 12 questions asked AND 2+ skill boundaries identified
        - OR maximum 20 questions reached
        - OR all required skill areas assessed (role-specific)
        
        Args:
            session: Interview session object
            
        Returns:
            True if interview should be completed, False otherwise
        """
        questions_asked = session.questions_asked_count
        skill_boundaries = session.skill_boundaries_identified or {}
        progression_state = session.progression_state or {}

        # Maximum questions limit
        if questions_asked >= 20:
            logger.info(
                "interview_complete_max_questions",
                session_id=str(session.id),
                questions_asked=questions_asked
            )
            return True

        # Minimum questions with sufficient boundaries
        boundaries_identified = len([
            skill for skill, level in skill_boundaries.items()
            if level in ["proficient", "boundary_reached", "expert"]
        ])

        if questions_asked >= 12 and boundaries_identified >= 2:
            logger.info(
                "interview_complete_criteria_met",
                session_id=str(session.id),
                questions_asked=questions_asked,
                boundaries_identified=boundaries_identified
            )
            return True

        # Check if all phases completed with sufficient assessment
        phase_history = progression_state.get("phase_history", [])
        if questions_asked >= 12:
            phases_completed = set(phase.get("phase") for phase in phase_history)
            if len(phases_completed) >= 3:  # All three phases (warmup, standard, advanced)
                logger.info(
                    "interview_complete_all_phases",
                    session_id=str(session.id),
                    questions_asked=questions_asked,
                    phases_completed=list(phases_completed)
                )
                return True

        return False

    async def get_next_question(self, session_id: UUID) -> dict:
        """
        Generate next interview question based on current state.
        
        Uses ProgressiveAssessmentEngine to generate difficulty-appropriate
        question based on conversation history and identified boundaries.

        Args:
            session_id: UUID of the interview session

        Returns:
            Dict containing:
                - question: Question text
                - skill_area: Target skill area
                - difficulty_level: Question difficulty
                - metadata: Additional question metadata

        Raises:
            ValueError: If session not found
            OpenAIProviderError: If question generation fails
        """
        logger.info(
            "getting_next_question",
            session_id=str(session_id)
        )

        # Load session
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Generate question (role_type would come from interview record)
        role_type = "general"  # Placeholder
        question_data = await self.assessment_engine.generate_next_question(
            session=session,
            role_type=role_type
        )

        # Persist session updates (questions_asked_count was incremented)
        await self.session_repo.update_session_state(session)

        logger.info(
            "next_question_generated",
            session_id=str(session_id),
            skill_area=question_data.get("skill_area"),
            difficulty=question_data.get("difficulty_level")
        )

        return {
            "question": question_data["question"],
            "skill_area": question_data.get("skill_area"),
            "difficulty_level": question_data.get("difficulty_level"),
            "metadata": {
                "is_followup": question_data.get("is_followup", False),
                "context_notes": question_data.get("context_notes", "")
            }
        }
