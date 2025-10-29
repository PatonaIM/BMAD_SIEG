"""Interview Engine service for managing AI-powered interviews."""
from datetime import datetime
from typing import Dict
from uuid import UUID

import structlog

from app.providers.base_ai_provider import AIProvider
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.models.interview_session import InterviewSession
from app.models.interview_message import InterviewMessage
from app.services.progressive_assessment_engine import (
    ProgressiveAssessmentEngine,
    DifficultyLevel
)

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
    ):
        """
        Initialize Interview Engine with dependencies.

        Args:
            ai_provider: OpenAI provider from Story 1.4
            session_repo: Session management repository
            message_repo: Message persistence repository
        """
        self.ai_provider = ai_provider
        self.session_repo = session_repo
        self.message_repo = message_repo
        
        # Initialize Progressive Assessment Engine
        self.assessment_engine = ProgressiveAssessmentEngine(ai_provider=self.ai_provider)
        
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
        session_id: UUID,
        response: str
    ) -> Dict:
        """
        Process candidate response and determine next action.
        
        Workflow:
        1. Load session from database
        2. Analyze response quality using ProgressiveAssessmentEngine
        3. Detect skill boundaries for the question's skill area
        4. Determine next difficulty level
        5. Update progression state with response data
        6. Save interview message to database
        7. Generate next question
        8. Update conversation memory
        9. Persist all changes to database

        Args:
            session_id: UUID of the interview session
            response: Candidate's text response

        Returns:
            Dict containing:
                - next_question: Next question text
                - difficulty_level: Current difficulty level
                - skill_area: Target skill area for next question
                - progression_data: Summary of progression state

        Raises:
            ValueError: If session not found
            OpenAIProviderError: If AI operations fail
        """
        logger.info(
            "processing_candidate_response",
            session_id=str(session_id),
            response_length=len(response)
        )
        
        # Load session
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Get last question from conversation memory
        conversation_memory = session.conversation_memory or {}
        messages = conversation_memory.get("messages", [])
        last_question = messages[-1].get("content", "") if messages else "General interview question"
        
        # Extract role_type and skill_area from session or use defaults
        # (In real implementation, this would come from interview record)
        role_type = "general"  # Placeholder - would come from interview.role_type
        current_difficulty = self.assessment_engine.get_current_phase(session)
        
        # Analyze response quality
        question_context = {
            "question": last_question,
            "role_type": role_type,
            "difficulty_level": current_difficulty.value,
            "skill_area": "general"  # Would be extracted from question metadata
        }
        
        analysis = await self.assessment_engine.analyze_response_quality(
            response_text=response,
            question_context=question_context
        )
        
        logger.info(
            "response_analyzed",
            session_id=str(session_id),
            confidence=analysis.confidence_level,
            accuracy=analysis.technical_accuracy,
            proficiency=analysis.proficiency_signal
        )
        
        # Detect skill boundaries
        skill_area = question_context.get("skill_area", "general")
        proficiency_level = await self.assessment_engine.detect_skill_boundaries(
            session=session,
            skill_area=skill_area,
            analysis=analysis
        )
        
        # Determine next difficulty
        next_difficulty = await self.assessment_engine.determine_next_difficulty(
            session=session,
            analysis=analysis
        )
        
        # Update progression state with response data
        self.assessment_engine.update_progression_state(
            session=session,
            update_data={
                "type": "response",
                "data": {
                    "question_num": session.questions_asked_count,
                    "confidence": analysis.confidence_level,
                    "accuracy": analysis.technical_accuracy,
                    "proficiency": analysis.proficiency_signal
                }
            }
        )
        
        # If difficulty changed, update progression state
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
        
        # Add skill to explored list
        self.assessment_engine.update_progression_state(
            session=session,
            update_data={
                "type": "skill_explored",
                "data": {
                    "skill": skill_area
                }
            }
        )
        
        # Save candidate response message
        response_message = InterviewMessage(
            interview_id=session.interview_id,
            session_id=session.id,
            sequence_number=len(messages) + 1,
            message_type="candidate_response",
            content_text=response,
            message_metadata={
                "analysis": {
                    "confidence_level": analysis.confidence_level,
                    "technical_accuracy": analysis.technical_accuracy,
                    "proficiency_signal": analysis.proficiency_signal
                },
                "skill_area": skill_area,
                "difficulty_level": current_difficulty.value
            },
            created_at=datetime.utcnow()
        )
        await self.message_repo.create(response_message)
        
        # Update conversation memory with response
        messages.append({
            "role": "user",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation_memory["messages"] = messages
        conversation_memory["memory_metadata"]["message_count"] = len(messages)
        conversation_memory["memory_metadata"]["last_updated"] = datetime.utcnow().isoformat()
        session.conversation_memory = conversation_memory
        
        # Generate next question
        next_question_data = await self.assessment_engine.generate_next_question(
            session=session,
            role_type=role_type
        )
        
        # Save next question message
        question_message = InterviewMessage(
            interview_id=session.interview_id,
            session_id=session.id,
            sequence_number=len(messages) + 1,
            message_type="ai_question",
            content_text=next_question_data["question"],
            message_metadata={
                "skill_area": next_question_data.get("skill_area"),
                "difficulty_level": next_question_data.get("difficulty_level"),
                "is_followup": next_question_data.get("is_followup", False)
            },
            created_at=datetime.utcnow()
        )
        await self.message_repo.create(question_message)
        
        # Update conversation memory with question
        messages.append({
            "role": "assistant",
            "content": next_question_data["question"],
            "timestamp": datetime.utcnow().isoformat()
        })
        session.conversation_memory = conversation_memory
        
        # Persist session updates
        await self.session_repo.update_session_state(session)
        
        logger.info(
            "candidate_response_processed",
            session_id=str(session_id),
            next_difficulty=next_difficulty.value,
            questions_asked=session.questions_asked_count,
            skill_proficiency=proficiency_level
        )
        
        return {
            "next_question": next_question_data["question"],
            "difficulty_level": next_difficulty.value,
            "skill_area": next_question_data.get("skill_area"),
            "progression_data": {
                "questions_asked": session.questions_asked_count,
                "current_difficulty": next_difficulty.value,
                "skills_explored": self.assessment_engine.get_skills_explored(session),
                "skill_boundaries": session.skill_boundaries_identified
            }
        }

    async def get_next_question(self, session_id: UUID) -> Dict:
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
