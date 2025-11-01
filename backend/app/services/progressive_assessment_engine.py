"""Progressive Assessment Engine for adaptive interview difficulty."""
import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import structlog

from app.core.config import settings
from app.models.interview_session import InterviewSession
from app.providers.base_ai_provider import AIProvider

logger = structlog.get_logger().bind(service="progressive_assessment")

# Resolve prompt file paths relative to this file's location
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
RESPONSE_ANALYSIS_PROMPT = PROMPTS_DIR / "response_analysis.txt"
ADAPTIVE_QUESTION_PROMPT = PROMPTS_DIR / "adaptive_question.txt"


class DifficultyLevel(str, Enum):
    """
    Interview difficulty levels for progressive assessment.
    
    Attributes:
        WARMUP: Confidence-building phase (2-3 questions)
        STANDARD: Core competency evaluation (5-8 questions)
        ADVANCED: Boundary exploration (3-5 questions until struggles)
    """
    WARMUP = "warmup"
    STANDARD = "standard"
    ADVANCED = "advanced"


@dataclass
class ResponseAnalysis:
    """
    Analysis result for a candidate's response.
    
    Attributes:
        confidence_level: Response confidence (0.0-1.0)
        technical_accuracy: Technical correctness (0.0-1.0)
        depth_of_understanding: Depth vs surface-level (0.0-1.0)
        hesitation_indicators: List of detected hesitation markers
        proficiency_signal: Overall proficiency (novice, intermediate, proficient, expert)
    """
    confidence_level: float
    technical_accuracy: float
    depth_of_understanding: float
    hesitation_indicators: list[str]
    proficiency_signal: str


class ProgressiveAssessmentEngine:
    """
    Progressive assessment engine for adaptive interview difficulty.
    
    Implements three-phase approach:
    1. Warmup Phase (2-3 questions): Confidence-building, basic concepts
    2. Standard Phase (5-8 questions): Core competency evaluation
    3. Advanced Phase (3-5 questions): Boundary exploration
    
    Features:
    - AI-powered response quality analysis
    - Automatic difficulty progression based on performance
    - Skill boundary detection to avoid re-testing
    - Adaptive question generation tailored to candidate level
    - Never regresses to lower difficulty levels
    
    Attributes:
        ai_provider: AI provider for response analysis and question generation
        thresholds: Configurable progression thresholds from settings
    """

    def __init__(self, ai_provider: AIProvider):
        """
        Initialize Progressive Assessment Engine.

        Args:
            ai_provider: AI provider for completions and analysis
        """
        self.ai_provider = ai_provider

        # Load configurable thresholds from settings
        self.warmup_min_questions = settings.warmup_min_questions
        self.warmup_confidence_threshold = settings.warmup_confidence_threshold
        self.standard_min_questions = settings.standard_min_questions
        self.standard_accuracy_threshold = settings.standard_accuracy_threshold
        self.boundary_confidence_threshold = settings.boundary_confidence_threshold

        # Phase limits to prevent infinite loops
        self.warmup_max_questions = 5
        self.standard_max_questions = 12
        self.advanced_max_questions = 8

        logger.info(
            "progressive_assessment_initialized",
            warmup_min=self.warmup_min_questions,
            warmup_threshold=self.warmup_confidence_threshold,
            standard_min=self.standard_min_questions,
            standard_threshold=self.standard_accuracy_threshold,
            boundary_threshold=self.boundary_confidence_threshold
        )

    def get_current_phase(self, session: InterviewSession) -> DifficultyLevel:
        """
        Get current difficulty phase from session state.

        Args:
            session: Interview session with current state

        Returns:
            Current DifficultyLevel enum value
        """
        if session.current_difficulty_level == "warmup":
            return DifficultyLevel.WARMUP
        elif session.current_difficulty_level == "standard":
            return DifficultyLevel.STANDARD
        elif session.current_difficulty_level == "advanced":
            return DifficultyLevel.ADVANCED
        else:
            # Default to warmup if unrecognized
            logger.warning(
                "unrecognized_difficulty_level",
                session_id=str(session.id),
                level=session.current_difficulty_level
            )
            return DifficultyLevel.WARMUP

    def should_advance_difficulty(
        self,
        session: InterviewSession,
        response_analysis: ResponseAnalysis
    ) -> bool:
        """
        Determine if difficulty should advance based on current performance.
        
        Evaluates progression criteria:
        - Minimum questions met for current phase
        - Performance thresholds exceeded
        - No recent boundary detections

        Args:
            session: Interview session with progression state
            response_analysis: Latest response analysis result

        Returns:
            True if should advance to next difficulty level
        """
        current_phase = self.get_current_phase(session)
        progression_state = session.progression_state or {}

        # Get questions in current phase
        phase_history = progression_state.get("phase_history", [])
        current_phase_questions = 0
        if phase_history:
            latest_phase = phase_history[-1]
            if latest_phase.get("phase") == current_phase.value:
                current_phase_questions = latest_phase.get("questions_count", 0)

        # Get response quality history for current phase
        response_history = progression_state.get("response_quality_history", [])

        # Warmup → Standard transition criteria
        if current_phase == DifficultyLevel.WARMUP:
            if current_phase_questions < self.warmup_min_questions:
                return False

            # Calculate average confidence for warmup phase
            warmup_responses = [
                r for r in response_history
                if r.get("question_num", 0) <= current_phase_questions
            ]
            if not warmup_responses:
                return False

            avg_confidence = sum(r.get("confidence", 0) for r in warmup_responses) / len(warmup_responses)

            # Check for critical errors (technical_accuracy < 0.6)
            has_critical_errors = any(r.get("accuracy", 1.0) < 0.6 for r in warmup_responses)

            should_advance = (
                avg_confidence >= self.warmup_confidence_threshold
                and not has_critical_errors
            )

            logger.info(
                "warmup_transition_check",
                session_id=str(session.id),
                questions=current_phase_questions,
                avg_confidence=avg_confidence,
                has_errors=has_critical_errors,
                should_advance=should_advance
            )
            return should_advance

        # Standard → Advanced transition criteria
        elif current_phase == DifficultyLevel.STANDARD:
            if current_phase_questions < self.standard_min_questions:
                return False

            # Get standard phase responses
            standard_start_idx = sum(
                p.get("questions_count", 0)
                for p in phase_history[:-1]
            ) if len(phase_history) > 1 else 0

            standard_responses = [
                r for r in response_history
                if r.get("question_num", 0) > standard_start_idx
            ]
            if not standard_responses:
                return False

            avg_accuracy = sum(r.get("accuracy", 0) for r in standard_responses) / len(standard_responses)

            # Check proficiency signals
            proficiency_signals = [r.get("proficiency", "novice") for r in standard_responses[-3:]]
            high_proficiency = sum(1 for p in proficiency_signals if p in ["proficient", "expert"])

            # Check for recent boundary detections
            boundary_detections = progression_state.get("boundary_detections", [])
            recent_boundaries = [
                b for b in boundary_detections
                if b.get("question_num", 0) > (len(response_history) - 3)
            ]

            should_advance = (
                avg_accuracy >= self.standard_accuracy_threshold
                and high_proficiency >= 2
                and len(recent_boundaries) == 0
            )

            logger.info(
                "standard_transition_check",
                session_id=str(session.id),
                questions=current_phase_questions,
                avg_accuracy=avg_accuracy,
                high_proficiency_count=high_proficiency,
                recent_boundaries=len(recent_boundaries),
                should_advance=should_advance
            )
            return should_advance

        # Already at advanced - no further progression
        return False

    # Placeholder methods to be implemented in subsequent tasks
    async def analyze_response_quality(
        self,
        response_text: str,
        question_context: dict
    ) -> ResponseAnalysis:
        """
        Analyze candidate response for quality and proficiency.
        
        Uses AI to evaluate:
        - Technical correctness and accuracy
        - Depth vs surface-level understanding
        - Appropriate terminology usage
        - Evidence of hands-on experience
        - Confidence level based on hesitation markers

        Args:
            response_text: Candidate's response text
            question_context: Context dict with:
                - question: The question that was asked
                - role_type: Interview role (e.g., "react", "python")
                - difficulty_level: Current difficulty level
                - skill_area: Target skill area (optional)

        Returns:
            ResponseAnalysis with confidence, accuracy, depth, hesitations, proficiency

        Raises:
            OpenAIProviderError: If AI analysis fails
        """
        import json

        # Load response analysis prompt
        if not RESPONSE_ANALYSIS_PROMPT.exists():
            logger.error(
                "response_analysis_prompt_not_found",
                prompt_path=str(RESPONSE_ANALYSIS_PROMPT)
            )
            raise FileNotFoundError(f"Response analysis prompt not found: {RESPONSE_ANALYSIS_PROMPT}")

        with open(RESPONSE_ANALYSIS_PROMPT) as f:
            prompt_template = f.read()

        # Replace placeholders (using simple string replacement to avoid format() issues with JSON in template)
        prompt = prompt_template.replace("{question}", question_context.get("question", ""))
        prompt = prompt.replace("{response}", response_text)
        prompt = prompt.replace("{role_type}", question_context.get("role_type", "general"))
        prompt = prompt.replace("{difficulty_level}", question_context.get("difficulty_level", "standard"))

        try:
            # Call AI provider for analysis
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please analyze the above response and provide your assessment in JSON format."}
            ]

            logger.info(
                "analyzing_response",
                response_length=len(response_text),
                difficulty=question_context.get("difficulty_level", "unknown")
            )

            # Call AI with timeout
            analysis_json = await asyncio.wait_for(
                self.ai_provider.generate_completion(
                    messages=messages,
                    temperature=0.3,  # Lower temperature for consistent analysis
                    max_tokens=500
                ),
                timeout=settings.progressive_assessment_timeout
            )

            # Parse JSON response
            # Remove markdown code blocks if present
            analysis_json = analysis_json.strip()
            if analysis_json.startswith("```json"):
                analysis_json = analysis_json[7:]
            if analysis_json.startswith("```"):
                analysis_json = analysis_json[3:]
            if analysis_json.endswith("```"):
                analysis_json = analysis_json[:-3]
            analysis_json = analysis_json.strip()

            analysis_data = json.loads(analysis_json)

            # Create ResponseAnalysis object
            response_analysis = ResponseAnalysis(
                confidence_level=float(analysis_data.get("confidence_level", 0.5)),
                technical_accuracy=float(analysis_data.get("technical_accuracy", 0.5)),
                depth_of_understanding=float(analysis_data.get("depth_of_understanding", 0.5)),
                hesitation_indicators=analysis_data.get("hesitation_indicators", []),
                proficiency_signal=analysis_data.get("proficiency_signal", "intermediate")
            )

            logger.info(
                "response_analyzed",
                confidence=response_analysis.confidence_level,
                accuracy=response_analysis.technical_accuracy,
                proficiency=response_analysis.proficiency_signal,
                skill_area=analysis_data.get("skill_area", "unknown")
            )

            return response_analysis

        except json.JSONDecodeError as e:
            logger.error(
                "response_analysis_json_parse_error",
                error=str(e),
                raw_response=analysis_json[:500]
            )
            # Return default moderate analysis on parse error
            return ResponseAnalysis(
                confidence_level=0.5,
                technical_accuracy=0.5,
                depth_of_understanding=0.5,
                hesitation_indicators=["parse_error"],
                proficiency_signal="intermediate"
            )
        except TimeoutError:
            logger.error(
                "response_analysis_timeout",
                timeout_seconds=settings.progressive_assessment_timeout
            )
            # Return default moderate analysis on timeout
            return ResponseAnalysis(
                confidence_level=0.5,
                technical_accuracy=0.5,
                depth_of_understanding=0.5,
                hesitation_indicators=["timeout_error"],
                proficiency_signal="intermediate"
            )
        except Exception as e:
            logger.error(
                "response_analysis_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            # Return default moderate analysis on error
            return ResponseAnalysis(
                confidence_level=0.5,
                technical_accuracy=0.5,
                depth_of_understanding=0.5,
                hesitation_indicators=["analysis_error"],
                proficiency_signal="intermediate"
            )

    async def determine_next_difficulty(
        self,
        session: InterviewSession,
        analysis: ResponseAnalysis
    ) -> DifficultyLevel:
        """
        Determine next difficulty level based on performance.
        
        Implements transition logic:
        - Warmup → Standard: Min questions met, avg confidence >= threshold, no critical errors
        - Standard → Advanced: Min questions met, avg accuracy >= threshold, proficient signals
        - Never regresses to lower difficulty
        - Stays at current level if criteria not met

        Args:
            session: Interview session with progression state
            analysis: Latest response analysis result

        Returns:
            DifficultyLevel for next question (may be same as current)

        Note:
            Updates session.current_difficulty_level in database if transition occurs
        """
        current_phase = self.get_current_phase(session)
        progression_state = session.progression_state or {}

        # Check if should advance difficulty
        if self.should_advance_difficulty(session, analysis):
            # Determine next level
            if current_phase == DifficultyLevel.WARMUP:
                new_difficulty = DifficultyLevel.STANDARD
            elif current_phase == DifficultyLevel.STANDARD:
                new_difficulty = DifficultyLevel.ADVANCED
            else:
                # Already at advanced
                new_difficulty = current_phase

            # Update session difficulty level if changed
            if new_difficulty != current_phase:
                session.current_difficulty_level = new_difficulty.value

                logger.info(
                    "difficulty_transition",
                    session_id=str(session.id),
                    from_difficulty=current_phase.value,
                    to_difficulty=new_difficulty.value,
                    questions_count=session.questions_asked_count
                )

                return new_difficulty

        # Stay at current level - check for stay conditions
        # If confidence drops below boundary threshold, log it
        if analysis.confidence_level < self.boundary_confidence_threshold:
            logger.info(
                "staying_at_current_difficulty",
                session_id=str(session.id),
                difficulty=current_phase.value,
                confidence=analysis.confidence_level,
                boundary_threshold=self.boundary_confidence_threshold,
                reason="low_confidence"
            )

        # Check for consecutive low accuracy (< 0.6)
        response_history = progression_state.get("response_quality_history", [])
        recent_responses = response_history[-2:] if len(response_history) >= 2 else []
        if len(recent_responses) == 2:
            both_low_accuracy = all(r.get("accuracy", 1.0) < 0.6 for r in recent_responses)
            if both_low_accuracy:
                logger.info(
                    "staying_at_current_difficulty",
                    session_id=str(session.id),
                    difficulty=current_phase.value,
                    reason="consecutive_low_accuracy"
                )

        return current_phase

    async def detect_skill_boundaries(
        self,
        session: InterviewSession,
        skill_area: str,
        analysis: ResponseAnalysis
    ) -> str:
        """
        Detect skill boundary for specific technical area.
        
        Proficiency levels:
        - comfortable: High confidence (>= 0.8), accurate responses
        - proficient: Generally accurate (>= 0.7), minor hesitations
        - intermediate: Partial understanding (>= 0.5), some errors
        - boundary_reached: Struggling (< 0.5), significant errors, confusion

        Args:
            session: Interview session with skill boundaries
            skill_area: Technical skill being evaluated (e.g., "react_hooks")
            analysis: Response analysis result from AI

        Returns:
            Proficiency level string: comfortable, proficient, intermediate, boundary_reached

        Side Effects:
            Updates session.skill_boundaries_identified JSONB
            Updates session.progression_state with boundary detection timestamp
        """
        # Determine proficiency level based on analysis
        confidence = analysis.confidence_level
        accuracy = analysis.technical_accuracy

        # Decision logic based on thresholds
        if confidence >= 0.8 and accuracy >= 0.8:
            proficiency_level = "comfortable"
        elif confidence >= 0.7 and accuracy >= 0.7:
            proficiency_level = "proficient"
        elif confidence >= self.boundary_confidence_threshold and accuracy >= 0.5:
            proficiency_level = "intermediate"
        else:
            # confidence < boundary_threshold OR accuracy < 0.5
            proficiency_level = "boundary_reached"

        # Update skill_boundaries_identified JSONB
        if session.skill_boundaries_identified is None:
            session.skill_boundaries_identified = {}

        session.skill_boundaries_identified[skill_area] = proficiency_level

        # If boundary reached, add to progression_state boundary_detections
        if proficiency_level == "boundary_reached":
            progression_state = session.progression_state or {}
            if "boundary_detections" not in progression_state:
                progression_state["boundary_detections"] = []

            # Extract evidence from analysis
            evidence = f"Confidence: {confidence:.2f}, Accuracy: {accuracy:.2f}"
            if analysis.hesitation_indicators:
                evidence += f", Hesitations: {', '.join(analysis.hesitation_indicators[:3])}"

            boundary_detection = {
                "skill": skill_area,
                "detected_at": datetime.utcnow().isoformat(),
                "evidence": evidence,
                "question_num": session.questions_asked_count
            }
            progression_state["boundary_detections"].append(boundary_detection)
            session.progression_state = progression_state

            logger.info(
                "skill_boundary_detected",
                session_id=str(session.id),
                skill_area=skill_area,
                proficiency_level=proficiency_level,
                evidence=evidence
            )
        else:
            logger.info(
                "skill_proficiency_assessed",
                session_id=str(session.id),
                skill_area=skill_area,
                proficiency_level=proficiency_level,
                confidence=confidence,
                accuracy=accuracy
            )

        return proficiency_level

    def is_skill_boundary_reached(
        self,
        session: InterviewSession,
        skill_area: str
    ) -> bool:
        """
        Check if skill boundary has been reached for a specific area.

        Args:
            session: Interview session with skill boundaries
            skill_area: Technical skill to check (e.g., "react_hooks")

        Returns:
            True if skill marked as "boundary_reached", False otherwise
        """
        if not session.skill_boundaries_identified:
            return False

        proficiency = session.skill_boundaries_identified.get(skill_area)
        return proficiency == "boundary_reached"

    async def generate_next_question(
        self,
        session: InterviewSession,
        role_type: str
    ) -> dict:
        """
        Generate next interview question based on current state.
        
        Uses AI to generate difficulty-appropriate question considering:
        - Current difficulty level
        - Conversation history (last 5 exchanges)
        - Identified skill boundaries (to avoid re-testing)
        - Skills already explored
        - Role-specific technical areas

        Args:
            session: Interview session with progression state
            role_type: Interview role type (e.g., "react", "python", "javascript")

        Returns:
            Dict with:
                - question: Question text
                - skill_area: Target skill area
                - difficulty_level: Expected difficulty
                - is_followup: Boolean indicating if follow-up question
                - context_notes: Generation context notes

        Side Effects:
            Increments session.questions_asked_count
            Updates session.last_activity_at

        Raises:
            OpenAIProviderError: If question generation fails
        """
        import json

        # Get current state
        current_difficulty = self.get_current_phase(session)
        progression_state = session.progression_state or {}

        # Build conversation history (last 5 exchanges)
        conversation_memory = session.conversation_memory or {}
        messages = conversation_memory.get("messages", [])
        last_messages = messages[-10:] if len(messages) >= 10 else messages  # Last 5 Q&A pairs

        conversation_history = "No previous conversation" if not last_messages else "\n".join([
            f"- {msg.get('role', 'unknown').upper()}: {msg.get('content', '')[:200]}"
            for msg in last_messages
        ])

        # Get skills explored and boundaries
        skills_explored = progression_state.get("skills_explored", [])
        skill_boundaries = session.skill_boundaries_identified or {}

        # Filter boundaries to show only boundary_reached
        boundary_areas = {
            skill: level for skill, level in skill_boundaries.items()
            if level == "boundary_reached"
        }

        # Load adaptive question prompt
        if not ADAPTIVE_QUESTION_PROMPT.exists():
            logger.error(
                "adaptive_question_prompt_not_found",
                prompt_path=str(ADAPTIVE_QUESTION_PROMPT)
            )
            raise FileNotFoundError(f"Adaptive question prompt not found: {ADAPTIVE_QUESTION_PROMPT}")

        with open(ADAPTIVE_QUESTION_PROMPT) as f:
            prompt_template = f.read()

        # Replace placeholders (using simple string replacement to avoid format() issues with JSON in template)
        prompt = prompt_template.replace("{current_difficulty}", current_difficulty.value)
        prompt = prompt.replace("{role_type}", role_type)
        prompt = prompt.replace("{questions_asked}", str(session.questions_asked_count))
        prompt = prompt.replace("{conversation_history}", conversation_history)
        prompt = prompt.replace("{skills_explored}", ", ".join(skills_explored) if skills_explored else "None yet")
        prompt = prompt.replace("{skill_boundaries}", ", ".join(boundary_areas.keys()) if boundary_areas else "None identified")

        try:
            # Call AI provider for question generation
            messages_for_ai = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Generate the next interview question in JSON format."}
            ]

            logger.info(
                "generating_question",
                session_id=str(session.id),
                difficulty=current_difficulty.value,
                questions_asked=session.questions_asked_count
            )

            # Call AI with timeout
            question_json = await asyncio.wait_for(
                self.ai_provider.generate_completion(
                    messages=messages_for_ai,
                    temperature=0.7,  # Higher temperature for creative questions
                    max_tokens=300
                ),
                timeout=settings.progressive_assessment_timeout
            )

            # Parse JSON response
            question_json = question_json.strip()
            if question_json.startswith("```json"):
                question_json = question_json[7:]
            if question_json.startswith("```"):
                question_json = question_json[3:]
            if question_json.endswith("```"):
                question_json = question_json[:-3]
            question_json = question_json.strip()

            question_data = json.loads(question_json)

            # Increment questions asked count
            session.questions_asked_count += 1

            # Update last_activity_at
            session.last_activity_at = datetime.utcnow()

            logger.info(
                "question_generated",
                session_id=str(session.id),
                skill_area=question_data.get("skill_area", "unknown"),
                difficulty=question_data.get("difficulty_level", current_difficulty.value),
                is_followup=question_data.get("is_followup", False)
            )

            return question_data

        except json.JSONDecodeError as e:
            logger.error(
                "question_generation_json_parse_error",
                session_id=str(session.id),
                error=str(e),
                raw_response=question_json[:500]
            )
            # Return fallback generic question
            session.questions_asked_count += 1
            session.last_activity_at = datetime.utcnow()

            return {
                "question": f"Tell me about your experience with {role_type} development.",
                "skill_area": "general_experience",
                "difficulty_level": current_difficulty.value,
                "is_followup": False,
                "context_notes": "Fallback question due to generation error"
            }
        except TimeoutError:
            logger.error(
                "question_generation_timeout",
                session_id=str(session.id),
                timeout_seconds=settings.progressive_assessment_timeout
            )
            # Return fallback generic question
            session.questions_asked_count += 1
            session.last_activity_at = datetime.utcnow()

            return {
                "question": f"Tell me about a recent project you worked on with {role_type}.",
                "skill_area": "general_experience",
                "difficulty_level": current_difficulty.value,
                "is_followup": False,
                "context_notes": "Fallback question due to timeout"
            }
        except Exception as e:
            logger.error(
                "question_generation_failed",
                session_id=str(session.id),
                error=str(e),
                error_type=type(e).__name__
            )
            # Return fallback generic question
            session.questions_asked_count += 1
            session.last_activity_at = datetime.utcnow()

            return {
                "question": f"What challenges have you faced in {role_type} development?",
                "skill_area": "general_experience",
                "difficulty_level": current_difficulty.value,
                "is_followup": False,
                "context_notes": "Fallback question due to generation error"
            }

    def update_progression_state(
        self,
        session: InterviewSession,
        update_data: dict
    ) -> None:
        """
        Update progression state with new data.
        
        Updates progression_state JSONB with:
        - Phase history (when phases change)
        - Response quality history (after each response)
        - Skills explored (new skills encountered)
        - Boundary detections (handled in detect_skill_boundaries)

        Args:
            session: Interview session to update
            update_data: Dict containing update information:
                - type: "response" | "phase_change" | "skill_explored"
                - data: Relevant data for the update type

        Side Effects:
            Modifies session.progression_state JSONB

        Note:
            Does not commit to database - caller must handle persistence
        """
        # Initialize progression_state if needed
        if session.progression_state is None:
            session.progression_state = {
                "phase_history": [],
                "response_quality_history": [],
                "skills_explored": [],
                "skills_pending": [],
                "boundary_detections": []
            }

        progression_state = session.progression_state
        update_type = update_data.get("type")
        data = update_data.get("data", {})

        if update_type == "response":
            # Add response quality to history
            response_entry = {
                "question_num": data.get("question_num", session.questions_asked_count),
                "confidence": data.get("confidence", 0.5),
                "accuracy": data.get("accuracy", 0.5),
                "proficiency": data.get("proficiency", "intermediate"),
                "timestamp": datetime.utcnow().isoformat()
            }
            progression_state["response_quality_history"].append(response_entry)

            # Update current phase questions_count
            if progression_state["phase_history"]:
                current_phase = progression_state["phase_history"][-1]
                current_phase["questions_count"] = current_phase.get("questions_count", 0) + 1

            logger.debug(
                "progression_state_response_added",
                session_id=str(session.id),
                question_num=response_entry["question_num"],
                proficiency=response_entry["proficiency"]
            )

        elif update_type == "phase_change":
            # Add new phase to history
            new_phase = data.get("phase", "warmup")
            phase_entry = {
                "phase": new_phase,
                "started_at": datetime.utcnow().isoformat(),
                "questions_count": 0
            }
            progression_state["phase_history"].append(phase_entry)

            logger.info(
                "progression_state_phase_changed",
                session_id=str(session.id),
                new_phase=new_phase,
                phase_count=len(progression_state["phase_history"])
            )

        elif update_type == "skill_explored":
            # Add skill to explored list if not already there
            skill = data.get("skill", "")
            if skill and skill not in progression_state["skills_explored"]:
                progression_state["skills_explored"].append(skill)

                logger.debug(
                    "progression_state_skill_explored",
                    session_id=str(session.id),
                    skill=skill,
                    total_skills=len(progression_state["skills_explored"])
                )

        # Update session
        session.progression_state = progression_state

    def get_phase_history(self, session: InterviewSession) -> list[dict]:
        """
        Get phase transition history from session.

        Args:
            session: Interview session with progression state

        Returns:
            List of phase history entries with phase, started_at, questions_count
        """
        progression_state = session.progression_state or {}
        return progression_state.get("phase_history", [])

    def get_skills_explored(self, session: InterviewSession) -> list[str]:
        """
        Get list of skills explored during interview.

        Args:
            session: Interview session with progression state

        Returns:
            List of skill area strings
        """
        progression_state = session.progression_state or {}
        return progression_state.get("skills_explored", [])

    def get_average_response_quality(
        self,
        session: InterviewSession,
        phase: str
    ) -> float:
        """
        Calculate average response quality for a specific phase.

        Args:
            session: Interview session with progression state
            phase: Phase to calculate for ("warmup", "standard", "advanced")

        Returns:
            Average quality score (0.0-1.0) based on confidence and accuracy,
            or 0.0 if no responses in phase
        """
        progression_state = session.progression_state or {}
        phase_history = progression_state.get("phase_history", [])
        response_history = progression_state.get("response_quality_history", [])

        # Find phase boundaries
        phase_start_idx = 0
        phase_end_idx = len(response_history)

        for i, phase_entry in enumerate(phase_history):
            if phase_entry.get("phase") == phase:
                # Calculate start index
                phase_start_idx = sum(
                    p.get("questions_count", 0)
                    for p in phase_history[:i]
                )
                phase_end_idx = phase_start_idx + phase_entry.get("questions_count", 0)
                break

        # Get responses for this phase
        phase_responses = response_history[phase_start_idx:phase_end_idx]

        if not phase_responses:
            return 0.0

        # Calculate average of confidence and accuracy
        total_quality = sum(
            (r.get("confidence", 0.0) + r.get("accuracy", 0.0)) / 2.0
            for r in phase_responses
        )

        average_quality = total_quality / len(phase_responses)

        return average_quality
