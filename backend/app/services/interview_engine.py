"""Interview Engine service for managing AI-powered interviews."""
import asyncio
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
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

if TYPE_CHECKING:
    from app.models.job_posting import JobPosting

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
        role_type: str,
        use_realtime: bool = True
    ) -> InterviewSession:
        """
        Start a new interview session.
        
        Creates initial session with warmup difficulty level and
        initializes progression state for adaptive assessment.

        Args:
            candidate_id: UUID of the candidate
            role_type: Type of role interview (e.g., "react", "python")
            use_realtime: Whether to use Realtime API (default: True) or legacy STT/TTS

        Returns:
            Newly created InterviewSession with initialized state

        Side Effects:
            Creates InterviewSession record in database with:
            - initial difficulty: warmup
            - empty progression_state with initialized structure
            - empty conversation_memory
            - realtime_mode flag set based on use_realtime parameter
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
                "use_realtime": use_realtime,  # Store realtime mode preference
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
            initial_difficulty="warmup",
            use_realtime=use_realtime
        )

        return created_session
    
    def get_realtime_system_prompt(
        self,
        role_type: str,
        session: InterviewSession | None = None,
        job_posting: "JobPosting | None" = None  # NEW: Optional job context
    ) -> str:
        """
        Generate system prompt for OpenAI Realtime API.
        
        Creates comprehensive instructions for the AI interviewer that guide:
        - Interview tone and approach
        - Question progression logic
        - Answer evaluation criteria
        - Technical depth for the specific role
        - Job-specific context (if job_posting provided)
        
        Args:
            role_type: Type of role interview (e.g., "react", "python", "fullstack")
            session: Optional session for context (questions asked, difficulty level)
            job_posting: Optional JobPosting for job-context-aware interviews
        
        Returns:
            Formatted system prompt string for Realtime API
        
        Example:
            >>> prompt = engine.get_realtime_system_prompt("react")
            >>> # Use in realtime session configuration
            >>> # With job context:
            >>> prompt = engine.get_realtime_system_prompt("react", session, job_posting)
        """
        # Get current interview state
        questions_asked = 0
        current_difficulty = "fundamental"
        if session:
            questions_asked = session.questions_asked_count
            current_difficulty = session.current_difficulty_level or "warmup"
        
        # Role-specific technical areas
        role_technical_areas = {
            "react": "React fundamentals, hooks, state management, component lifecycle, performance optimization",
            "python": "Python syntax, data structures, OOP, async/await, libraries and frameworks",
            "javascript": "ES6+, closures, promises, async patterns, DOM manipulation, Node.js",
            "fullstack": "Frontend frameworks, backend APIs, databases, authentication, deployment"
        }
        
        technical_focus = role_technical_areas.get(
            role_type.lower(),
            "general software engineering principles and problem-solving"
        )
        
        prompt = f"""You are an expert technical interviewer conducting a {role_type} software engineering interview.

## Your Role and Approach

You are conducting a friendly yet thorough technical interview. Your goal is to:
- Assess the candidate's technical knowledge and problem-solving abilities
- Create a comfortable, conversational atmosphere
- Ask clear, focused questions appropriate to their skill level
- Listen actively and provide natural, encouraging feedback
- Adjust difficulty based on their responses

## Interview Structure

**Current State:**
- Role: {role_type.upper()}
- Questions Asked: {questions_asked}
- Current Difficulty: {current_difficulty}
- Target: 12-20 questions over 20-30 minutes

**Technical Focus Areas:**
{technical_focus}

**Progression Path:**
1. **Warmup (2-3 questions)**: Fundamental concepts, basic syntax, common patterns
2. **Core Skills (5-8 questions)**: Role-specific technical knowledge, best practices
3. **Advanced Topics (3-5 questions)**: Architecture, optimization, edge cases, trade-offs
4. **Wrap-up (1-2 questions)**: Open-ended, experience-based, or scenario questions

## Question Guidelines

- Ask ONE question at a time and wait for complete response
- Questions should be clear, specific, and relevant to {role_type}
- Start with fundamentals before advancing to complex topics
- Build on previous answers when appropriate
- If an answer is unclear, ask a follow-up for clarification

## Answer Evaluation and Skill Assessment

CRITICAL: Only evaluate AFTER the candidate has provided a substantial answer to your question. 

**Do NOT respond or evaluate if you hear:**
- Brief acknowledgments like "okay", "yes", "I see", "uh-huh", "mm-hmm"
- Short clarifying questions from the candidate (e.g., "Can you repeat that?")
- Mid-thought pauses while the candidate is formulating their response
- Background noise, echoes, or unclear audio
- Single words or very short phrases (less than 5 words)
- The candidate is clearly still thinking or speaking

**When in doubt, WAIT 2-3 seconds of silence before responding to ensure the candidate has finished speaking.**

Wait for a COMPLETE, SUBSTANTIAL answer that addresses the question before calling `evaluate_candidate_answer` with:
- **answer_quality**: "excellent" | "good" | "needs_clarification" | "off_topic"
- **key_points_covered**: List of technical concepts mentioned
- **skill_area**: The specific skill being assessed (e.g., "react_hooks", "state_management", "async_programming", "python_basics", "data_structures", "testing", "security", "database")
- **proficiency_level**: The candidate's demonstrated proficiency in this skill area:
  - "novice": Basic awareness, struggles with fundamentals, needs significant guidance
  - "intermediate": Understands core concepts, can work independently with some gaps
  - "proficient": Strong grasp, applies best practices, handles most scenarios well
  - "expert": Deep expertise, optimizes solutions, understands trade-offs and edge cases
- **next_action**: "continue" | "follow_up" | "move_to_next_topic"
- **follow_up_needed**: true/false

**Skill Assessment Guidelines:**
- Assess proficiency based on the DEPTH and ACCURACY of their answer
- Consider: correctness, use of terminology, awareness of best practices, ability to explain trade-offs
- Be consistent: Similar quality answers should get similar proficiency ratings
- Track multiple skill areas throughout the interview to build a comprehensive skill profile

Use evaluation results to:
- Adjust question difficulty up/down based on performance
- Identify knowledge boundaries (what they know vs. don't know)
- Build a skill proficiency map for personalized feedback
- Determine when to move to next topic area

## Tone and Style

- **Professional yet friendly**: Make candidate feel comfortable
- **Conversational**: Natural speech patterns, not robotic
- **Encouraging**: Acknowledge good answers, gently guide on weak areas
- **Clear and concise**: Avoid overly long questions or explanations
- **Patient**: Give candidates time to think and formulate responses

## CRITICAL: Initial Greeting Protocol

**When questions_asked = 0, you MUST follow this exact structure before asking any technical questions:**

1. **Warm Welcome**: Greet the candidate warmly and thank them for joining
2. **Interview Overview**: Explain what to expect in a clear, structured way:
   - Number of questions: "We'll go through about 12 to 20 questions"
   - Duration: "This should take approximately 20 to 30 minutes"
   - Format: "I'll start with some fundamental concepts and progressively adjust the difficulty based on your responses"
   - Approach: "This is a conversation, not a test to trick you - feel free to think out loud and ask for clarification if needed"
3. **Readiness Check**: Ask "Are you ready to begin?" or "Do you have any questions before we start?"
4. **WAIT FOR CONFIRMATION**: Do NOT proceed to the first technical question until the candidate responds with confirmation (e.g., "yes", "ready", "let's go", "sure")

**Example Opening (USE THIS STRUCTURE):**

"Hi! Thanks for joining today. I'm excited to learn about your experience with {role_type}. Let me give you a quick overview of what to expect. We'll go through about 12 to 20 technical questions tailored to your skill level, and this should take approximately 20 to 30 minutes. I'll adjust the difficulty based on your responses as we go. This is a conversation, not a test to trick you, so feel free to think out loud and ask for clarification whenever you need it. Are you ready to begin?"

**CRITICAL - DO NOT SKIP THIS STEP**: After delivering the greeting above, you MUST:
1. STOP SPEAKING immediately after saying "Are you ready to begin?"
2. WAIT in complete silence for the candidate to respond
3. Do NOT ask any technical questions yet
4. Do NOT assume they're ready just because a few seconds passed
5. Do NOT continue talking or answer your own question
6. ONLY after hearing the candidate say "yes", "ready", "sure", or similar confirmation words should you then proceed with: "Great! Let's begin with our first question..."

## Closing the Interview

After 12-20 questions or when 20-30 minutes have passed:
1. Thank the candidate for their time
2. Ask if they have any questions
3. Provide next steps (e.g., "We'll be in touch within a few days")
4. End on a positive, encouraging note

Remember: Your goal is to accurately assess technical skills while creating a positive candidate experience. Be thorough but fair, challenging but supportive."""
        
        # NEW: Inject job-specific context if job_posting is provided
        if job_posting:
            # Truncate description to avoid token limit issues (max 500 chars)
            description_preview = job_posting.description[:500]
            if len(job_posting.description) > 500:
                description_preview += "..."
            
            # Format required skills
            required_skills_str = ", ".join(job_posting.required_skills or [])
            
            # Build job context section
            job_context = f"""

---

## JOB-SPECIFIC CONTEXT

You are interviewing the candidate for this specific position:

**Position:** {job_posting.title}
**Company:** {job_posting.company}
**Role Category:** {job_posting.role_category}
**Experience Level:** {job_posting.experience_level}

**Job Description:**
{description_preview}

**Required Skills/Qualifications:**
{required_skills_str}

**CRITICAL INSTRUCTIONS FOR JOB-CONTEXT INTERVIEWS:**

1. **Tailor ALL questions to assess the required skills listed above**
2. **Focus on technologies and tools mentioned in the job description**
3. **Use the base technical framework as a foundation, but adapt every question to this specific role**
4. **Ask follow-up questions about relevant experience with the required tech stack**
5. **For non-technical roles (sales, support, product, design, marketing, operations, management):**
   - **DO NOT ask coding or technical programming questions**
   - **Focus on role-appropriate behavioral, situational, and skill-based questions**
   - **Use the required skills list to guide your assessment areas**
   - **Example for Sales: Ask about sales process, CRM experience, deal closing, objection handling**
   - **Example for Support: Ask about customer service scenarios, conflict resolution, tool proficiency**

6. **Evaluate the candidate's fit for THIS SPECIFIC JOB, not just general skills**

Remember: This interview is for the "{job_posting.title}" position at {job_posting.company}. Every question should assess the candidate's ability to succeed in THIS SPECIFIC ROLE."""
            
            prompt = prompt + job_context
            
            logger.info(
                "job_context_injected",
                job_posting_id=str(job_posting.id),
                job_title=job_posting.title,
                role_category=str(job_posting.role_category),
                prompt_length=len(prompt),
            )
        
        return prompt

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

    async def complete_interview(self, interview_id: UUID) -> dict:
        """
        Complete an interview and calculate final metrics.
        
        Updates interview status to 'completed', calculates duration,
        and compiles completion statistics.
        
        Args:
            interview_id: UUID of the interview to complete
            
        Returns:
            Dict containing:
                - interview_id: UUID of completed interview
                - completed_at: Timestamp of completion
                - duration_seconds: Total interview duration
                - questions_answered: Number of questions answered
                - skill_boundaries_identified: Number of skill boundaries found
                - message: Completion confirmation message
                
        Raises:
            InterviewNotFoundException: If interview not found
            InterviewCompletedException: If interview already completed
            ValueError: If interview status is invalid for completion
        """
        logger.info(
            "completing_interview",
            interview_id=str(interview_id)
        )
        
        # Load interview record
        interview = await self.interview_repo.get_by_id(interview_id)
        if not interview:
            raise InterviewNotFoundException(interview_id=interview_id)
        
        # Verify interview can be completed
        if interview.status == "completed":
            raise InterviewCompletedException(
                interview_id=interview_id,
                message="Interview has already been completed"
            )
        
        if interview.status not in ["in_progress", "scheduled"]:
            raise ValueError(
                f"Interview {interview_id} cannot be completed with status '{interview.status}'"
            )
        
        # Load session for metrics
        session = await self.session_repo.get_by_interview_id(interview_id)
        if not session:
            raise ValueError(f"No session found for interview {interview_id}")
        
        # Calculate completion timestamp and duration
        completed_at = datetime.utcnow()
        started_at = interview.started_at or completed_at
        duration_seconds = int((completed_at - started_at).total_seconds())
        
        # Count questions answered - use session.questions_asked_count for accuracy
        # NOTE: In voice/realtime mode, candidate_response messages can be fragmented
        # (multiple transcripts per question), so counting messages is inaccurate.
        # The session.questions_asked_count is incremented once per AI question.
        questions_answered = session.questions_asked_count
        
        # Load messages for generating highlights (still needed)
        messages = await self.message_repo.get_by_interview_id(interview_id)
        
        # Count skill boundaries identified
        skill_boundaries = session.skill_boundaries_identified or {}
        skill_boundaries_count = len(skill_boundaries)
        
        # Generate enhanced feedback
        skill_assessments = self._generate_skill_assessments(skill_boundaries)
        highlights = await self._generate_interview_highlights(messages, skill_boundaries)
        growth_areas = self._generate_growth_areas(skill_boundaries, session)
        
        # Update interview record
        interview.status = "completed"
        interview.completed_at = completed_at
        interview.duration_seconds = duration_seconds
        
        # Persist changes
        await self.interview_repo.update(interview)
        
        logger.info(
            "interview_completed",
            interview_id=str(interview_id),
            duration_seconds=duration_seconds,
            questions_answered=questions_answered,
            skill_boundaries=skill_boundaries_count,
            feedback_generated=True
        )
        
        return {
            "interview_id": interview_id,
            "completed_at": completed_at,
            "duration_seconds": duration_seconds,
            "questions_answered": questions_answered,
            "skill_boundaries_identified": skill_boundaries_count,
            "message": "Interview completed successfully",
            "skill_assessments": skill_assessments,
            "highlights": highlights,
            "growth_areas": growth_areas
        }

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

    def _generate_skill_assessments(self, skill_boundaries: dict) -> list[dict]:
        """
        Generate structured skill assessment breakdown.
        
        Args:
            skill_boundaries: Dict mapping skill_area -> proficiency_level
            
        Returns:
            List of skill assessment dicts with display names
        """
        skill_display_names = {
            "react_fundamentals": "React Fundamentals",
            "react_hooks": "React Hooks",
            "state_management": "State Management",
            "async_programming": "Async Programming",
            "python_basics": "Python Basics",
            "data_structures": "Data Structures",
            "algorithms": "Algorithms",
            "web_apis": "Web APIs",
            "testing": "Testing & QA",
            "performance_optimization": "Performance Optimization",
            "security": "Security Best Practices",
            "database": "Database Design",
            "general": "General Programming"
        }
        
        assessments = []
        for skill_area, proficiency in skill_boundaries.items():
            assessments.append({
                "skill_area": skill_area,
                "proficiency_level": proficiency,
                "display_name": skill_display_names.get(skill_area, skill_area.replace("_", " ").title())
            })
        
        # Sort by proficiency (expert -> novice) for better UX
        proficiency_order = {"expert": 0, "proficient": 1, "intermediate": 2, "novice": 3}
        assessments.sort(key=lambda x: proficiency_order.get(x["proficiency_level"], 4))
        
        return assessments

    async def _generate_interview_highlights(
        self,
        messages: list,
        skill_boundaries: dict
    ) -> list[dict]:
        """
        Generate positive highlights from interview performance.
        
        Identifies strong areas based on proficiency levels and creates
        encouraging feedback for the candidate.
        
        Args:
            messages: List of interview messages
            skill_boundaries: Dict mapping skill_area -> proficiency_level
            
        Returns:
            List of highlight dicts with title, description, skill_area
        """
        highlights = []
        
        # Identify strong skills (proficient or expert)
        strong_skills = {
            skill: level for skill, level in skill_boundaries.items()
            if level in ["proficient", "expert"]
        }
        
        skill_descriptions = {
            "react_fundamentals": {
                "proficient": ("Strong React Foundation", "You showed solid understanding of React core concepts and component architecture"),
                "expert": ("React Expert", "Excellent command of React patterns, demonstrating deep knowledge of component lifecycle and best practices")
            },
            "react_hooks": {
                "proficient": ("Hooks Proficiency", "Good grasp of React Hooks patterns and their practical applications"),
                "expert": ("Hooks Mastery", "Outstanding understanding of advanced hooks patterns and custom hook design")
            },
            "state_management": {
                "proficient": ("State Management Skills", "Demonstrated solid understanding of state management strategies"),
                "expert": ("State Management Expert", "Exceptional knowledge of complex state patterns and optimization techniques")
            },
            "async_programming": {
                "proficient": ("Async Programming", "Clear understanding of asynchronous patterns and best practices"),
                "expert": ("Async Expert", "Masterful handling of async operations, promises, and concurrent programming")
            },
            "python_basics": {
                "proficient": ("Python Proficiency", "Strong foundation in Python syntax and programming concepts"),
                "expert": ("Python Expert", "Excellent command of Pythonic idioms and advanced language features")
            },
            "data_structures": {
                "proficient": ("Data Structures Knowledge", "Good understanding of common data structures and their applications"),
                "expert": ("Data Structures Mastery", "Deep knowledge of data structures, complexity analysis, and optimization")
            }
        }
        
        for skill, level in strong_skills.items():
            if skill in skill_descriptions and level in skill_descriptions[skill]:
                title, description = skill_descriptions[skill][level]
                highlights.append({
                    "title": title,
                    "description": description,
                    "skill_area": skill
                })
        
        # Count candidate responses
        candidate_responses = [m for m in messages if m.message_type == "candidate_response"]
        num_responses = len(candidate_responses)
        
        # Add general highlight based on participation
        if num_responses >= 10:
            highlights.append({
                "title": "Great Engagement",
                "description": f"You actively participated throughout the interview, answering {num_responses} questions with thoughtful responses",
                "skill_area": None
            })
        elif num_responses >= 5:
            highlights.append({
                "title": "Active Participation",
                "description": f"You engaged well with the interview process, answering {num_responses} questions thoughtfully",
                "skill_area": None
            })
        elif num_responses >= 1:
            highlights.append({
                "title": "Good Start",
                "description": f"You began the interview process and provided {num_responses} response{'s' if num_responses > 1 else ''}. Every interview is a learning opportunity!",
                "skill_area": None
            })
        
        # If still no highlights, add default encouraging message
        if not highlights:
            highlights.append({
                "title": "Thanks for Participating",
                "description": "You took the time to start the interview process. We appreciate your effort and encourage you to complete a full interview session next time for detailed feedback.",
                "skill_area": None
            })
        
        # Limit to top 3 highlights for cleaner UX
        return highlights[:3]

    def _generate_growth_areas(
        self,
        skill_boundaries: dict,
        session
    ) -> list[dict]:
        """
        Generate constructive growth area suggestions.
        
        Identifies skills at novice/intermediate level or skills that
        were questioned but not fully explored.
        
        Args:
            skill_boundaries: Dict mapping skill_area -> proficiency_level
            session: Interview session with progression state
            
        Returns:
            List of growth area dicts with skill_area, suggestion, display_name
        """
        growth_areas = []
        
        skill_suggestions = {
            "react_hooks": {
                "novice": "Start with the basics of useState and useEffect. Practice building simple components using hooks.",
                "intermediate": "Deepen your understanding of useCallback and useMemo for performance optimization."
            },
            "react_basics": {
                "novice": "Focus on understanding JSX, components, and props. Build small projects to practice React fundamentals.",
                "intermediate": "Study component lifecycle, conditional rendering, and list rendering patterns in depth."
            },
            "react_components": {
                "novice": "Practice creating functional and class components. Learn the difference between controlled and uncontrolled components.",
                "intermediate": "Master component composition, higher-order components (HOCs), and render props patterns."
            },
            "react_router": {
                "novice": "Learn the basics of client-side routing with React Router. Practice creating multi-page applications.",
                "intermediate": "Explore nested routes, route protection, and programmatic navigation techniques."
            },
            "react_forms": {
                "novice": "Start with simple form handling using controlled components and basic validation.",
                "intermediate": "Implement complex form libraries like React Hook Form or Formik with advanced validation schemas."
            },
            "react_context": {
                "novice": "Understand the Context API basics for passing data through component trees without props drilling.",
                "intermediate": "Learn to optimize Context usage, avoid unnecessary re-renders, and structure context providers effectively."
            },
            "state_management": {
                "novice": "Begin with local component state before exploring Redux or Context API.",
                "intermediate": "Consider learning about Redux Toolkit or Zustand for more complex state scenarios."
            },
            "async_programming": {
                "novice": "Focus on understanding promises and async/await syntax with practical examples.",
                "intermediate": "Explore error handling patterns and concurrent request management."
            },
            "performance_optimization": {
                "novice": "Learn about basic React performance concepts like re-rendering and memoization.",
                "intermediate": "Study React DevTools profiler and advanced optimization techniques."
            },
            "typescript": {
                "novice": "Start with basic TypeScript types, interfaces, and type annotations in React components.",
                "intermediate": "Master generics, utility types, and advanced TypeScript patterns for React applications."
            },
            "next_js": {
                "novice": "Learn Next.js fundamentals including pages, routing, and basic data fetching methods.",
                "intermediate": "Explore server-side rendering (SSR), static site generation (SSG), and API routes."
            },
            "css_styling": {
                "novice": "Practice CSS fundamentals, Flexbox, and Grid. Learn CSS Modules or styled-components basics.",
                "intermediate": "Master CSS-in-JS solutions, Tailwind CSS, and responsive design patterns."
            },
            "api_integration": {
                "novice": "Learn to fetch data from APIs using fetch or axios. Handle loading and error states.",
                "intermediate": "Implement advanced data fetching with React Query or SWR, including caching and mutations."
            },
            "python_basics": {
                "novice": "Practice Python fundamentals with small coding challenges and exercises.",
                "intermediate": "Explore more advanced features like decorators, generators, and context managers."
            },
            "data_structures": {
                "novice": "Start with arrays, linked lists, and basic sorting algorithms.",
                "intermediate": "Study trees, graphs, and more complex algorithmic patterns."
            },
            "testing": {
                "novice": "Begin with unit testing fundamentals using Jest or pytest.",
                "intermediate": "Learn integration testing, mocking strategies, and TDD practices."
            }
        }
        
        skill_display_names = {
            "react_hooks": "React Hooks",
            "react_basics": "React Fundamentals",
            "react_components": "React Components",
            "react_router": "React Router",
            "react_forms": "React Forms",
            "react_context": "React Context API",
            "state_management": "State Management",
            "async_programming": "Async Programming",
            "performance_optimization": "Performance Optimization",
            "typescript": "TypeScript",
            "next_js": "Next.js",
            "css_styling": "CSS & Styling",
            "api_integration": "API Integration",
            "python_basics": "Python Programming",
            "data_structures": "Data Structures & Algorithms",
            "testing": "Testing & Quality Assurance",
            "security": "Security Best Practices",
            "database": "Database Design"
        }
        
        # Log skill boundaries for debugging
        logger.info(
            "generating_growth_areas",
            skill_boundaries=skill_boundaries,
            skill_count=len(skill_boundaries)
        )
        
        # Identify areas needing improvement (novice or intermediate)
        for skill, level in skill_boundaries.items():
            if level in ["novice", "intermediate"]:
                # Try to get specific suggestion, or generate generic one
                if skill in skill_suggestions and level in skill_suggestions[skill]:
                    suggestion = skill_suggestions[skill][level]
                else:
                    # Generate generic suggestion for any skill not in predefined list
                    suggestion = (
                        f"Continue practicing {skill.replace('_', ' ')} to build confidence. "
                        f"Focus on fundamental concepts and gradually work towards more advanced topics."
                        if level == "novice"
                        else f"Strengthen your {skill.replace('_', ' ')} skills through hands-on projects "
                        f"and real-world scenarios to reach proficiency."
                    )
                
                growth_areas.append({
                    "skill_area": skill,
                    "suggestion": suggestion,
                    "display_name": skill_display_names.get(skill, skill.replace("_", " ").title())
                })
        
        # If no specific growth areas identified, provide general recommendations
        if not growth_areas:
            # Get role type from session if available
            progression_state = session.progression_state or {}
            
            # Provide default growth areas based on common interview best practices
            default_areas = [
                {
                    "skill_area": "interview_completion",
                    "suggestion": "Complete a full interview session to get detailed skill assessments and personalized feedback on your technical abilities.",
                    "display_name": "Complete Full Assessment"
                },
                {
                    "skill_area": "communication",
                    "suggestion": "Practice articulating your thought process clearly when answering technical questions. This helps interviewers understand your problem-solving approach.",
                    "display_name": "Communication Skills"
                },
                {
                    "skill_area": "fundamentals",
                    "suggestion": "Review fundamental concepts in your target role. Strong foundational knowledge helps you tackle more complex problems with confidence.",
                    "display_name": "Core Fundamentals"
                }
            ]
            
            growth_areas = default_areas
        
        # Limit to top 3 for cleaner UX
        return growth_areas[:3]
