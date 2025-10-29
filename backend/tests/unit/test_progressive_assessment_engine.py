"""Unit tests for Progressive Assessment Engine."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.progressive_assessment_engine import (
    ProgressiveAssessmentEngine,
    DifficultyLevel,
    ResponseAnalysis
)
from app.models.interview_session import InterviewSession


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider for testing."""
    provider = AsyncMock()
    provider.generate_completion = AsyncMock()
    return provider


@pytest.fixture
def assessment_engine(mock_ai_provider):
    """Create assessment engine with mocked AI provider."""
    return ProgressiveAssessmentEngine(ai_provider=mock_ai_provider)


@pytest.fixture
def sample_session():
    """Create sample interview session for testing."""
    session = InterviewSession(
        interview_id="test-interview-id",
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
        conversation_memory={"messages": []},
        last_activity_at=datetime.utcnow()
    )
    return session


class TestDifficultyLevel:
    """Test DifficultyLevel enum."""
    
    def test_difficulty_levels_exist(self):
        """Test that all difficulty levels are defined."""
        assert DifficultyLevel.WARMUP.value == "warmup"
        assert DifficultyLevel.STANDARD.value == "standard"
        assert DifficultyLevel.ADVANCED.value == "advanced"


class TestResponseAnalysis:
    """Test ResponseAnalysis dataclass."""
    
    def test_response_analysis_creation(self):
        """Test creating ResponseAnalysis instance."""
        analysis = ResponseAnalysis(
            confidence_level=0.8,
            technical_accuracy=0.9,
            depth_of_understanding=0.7,
            hesitation_indicators=["um", "I think"],
            proficiency_signal="proficient"
        )
        
        assert analysis.confidence_level == 0.8
        assert analysis.technical_accuracy == 0.9
        assert analysis.proficiency_signal == "proficient"
        assert len(analysis.hesitation_indicators) == 2


class TestProgressiveAssessmentEngine:
    """Test Progressive Assessment Engine core functionality."""
    
    def test_initialization(self, assessment_engine):
        """Test engine initializes with correct thresholds."""
        assert assessment_engine.warmup_min_questions == 2
        assert assessment_engine.warmup_confidence_threshold == 0.7
        assert assessment_engine.standard_min_questions == 4
        assert assessment_engine.standard_accuracy_threshold == 0.8
        assert assessment_engine.boundary_confidence_threshold == 0.5
    
    def test_get_current_phase_warmup(self, assessment_engine, sample_session):
        """Test get_current_phase returns warmup for new session."""
        phase = assessment_engine.get_current_phase(sample_session)
        assert phase == DifficultyLevel.WARMUP
    
    def test_get_current_phase_standard(self, assessment_engine, sample_session):
        """Test get_current_phase returns standard when set."""
        sample_session.current_difficulty_level = "standard"
        phase = assessment_engine.get_current_phase(sample_session)
        assert phase == DifficultyLevel.STANDARD
    
    def test_get_current_phase_advanced(self, assessment_engine, sample_session):
        """Test get_current_phase returns advanced when set."""
        sample_session.current_difficulty_level = "advanced"
        phase = assessment_engine.get_current_phase(sample_session)
        assert phase == DifficultyLevel.ADVANCED


class TestDifficultyAdvancement:
    """Test difficulty advancement logic."""
    
    def test_should_advance_warmup_insufficient_questions(
        self, assessment_engine, sample_session
    ):
        """Test warmup doesn't advance with < min questions."""
        # Only 1 question in warmup
        sample_session.progression_state["phase_history"][0]["questions_count"] = 1
        sample_session.progression_state["response_quality_history"] = [
            {"question_num": 1, "confidence": 0.9, "accuracy": 0.9, "proficiency": "proficient"}
        ]
        
        analysis = ResponseAnalysis(
            confidence_level=0.9,
            technical_accuracy=0.9,
            depth_of_understanding=0.8,
            hesitation_indicators=[],
            proficiency_signal="proficient"
        )
        
        should_advance = assessment_engine.should_advance_difficulty(sample_session, analysis)
        assert should_advance is False
    
    def test_should_advance_warmup_to_standard(
        self, assessment_engine, sample_session
    ):
        """Test warmup advances to standard when criteria met."""
        # 2 questions with high confidence
        sample_session.progression_state["phase_history"][0]["questions_count"] = 2
        sample_session.progression_state["response_quality_history"] = [
            {"question_num": 1, "confidence": 0.8, "accuracy": 0.9, "proficiency": "proficient"},
            {"question_num": 2, "confidence": 0.75, "accuracy": 0.85, "proficiency": "proficient"}
        ]
        
        analysis = ResponseAnalysis(
            confidence_level=0.75,
            technical_accuracy=0.85,
            depth_of_understanding=0.8,
            hesitation_indicators=[],
            proficiency_signal="proficient"
        )
        
        should_advance = assessment_engine.should_advance_difficulty(sample_session, analysis)
        assert should_advance is True


class TestSkillBoundaryDetection:
    """Test skill boundary detection."""
    
    @pytest.mark.asyncio
    async def test_detect_boundary_comfortable(
        self, assessment_engine, sample_session
    ):
        """Test detection of comfortable proficiency."""
        analysis = ResponseAnalysis(
            confidence_level=0.9,
            technical_accuracy=0.9,
            depth_of_understanding=0.85,
            hesitation_indicators=[],
            proficiency_signal="expert"
        )
        
        level = await assessment_engine.detect_skill_boundaries(
            session=sample_session,
            skill_area="react_hooks",
            analysis=analysis
        )
        
        assert level == "comfortable"
        assert sample_session.skill_boundaries_identified["react_hooks"] == "comfortable"
    
    @pytest.mark.asyncio
    async def test_detect_boundary_reached(
        self, assessment_engine, sample_session
    ):
        """Test detection of boundary_reached."""
        analysis = ResponseAnalysis(
            confidence_level=0.3,
            technical_accuracy=0.4,
            depth_of_understanding=0.3,
            hesitation_indicators=["I'm not sure", "maybe", "I think"],
            proficiency_signal="novice"
        )
        
        level = await assessment_engine.detect_skill_boundaries(
            session=sample_session,
            skill_area="performance_optimization",
            analysis=analysis
        )
        
        assert level == "boundary_reached"
        assert sample_session.skill_boundaries_identified["performance_optimization"] == "boundary_reached"
        assert len(sample_session.progression_state["boundary_detections"]) == 1
    
    def test_is_skill_boundary_reached_true(
        self, assessment_engine, sample_session
    ):
        """Test checking if skill boundary is reached."""
        sample_session.skill_boundaries_identified = {
            "performance_optimization": "boundary_reached"
        }
        
        is_boundary = assessment_engine.is_skill_boundary_reached(
            session=sample_session,
            skill_area="performance_optimization"
        )
        
        assert is_boundary is True
    
    def test_is_skill_boundary_reached_false(
        self, assessment_engine, sample_session
    ):
        """Test checking skill boundary not reached."""
        sample_session.skill_boundaries_identified = {
            "react_hooks": "proficient"
        }
        
        is_boundary = assessment_engine.is_skill_boundary_reached(
            session=sample_session,
            skill_area="react_hooks"
        )
        
        assert is_boundary is False


class TestProgressionStateUpdates:
    """Test progression state tracking."""
    
    def test_update_progression_state_response(
        self, assessment_engine, sample_session
    ):
        """Test updating state with response data."""
        assessment_engine.update_progression_state(
            session=sample_session,
            update_data={
                "type": "response",
                "data": {
                    "question_num": 1,
                    "confidence": 0.8,
                    "accuracy": 0.9,
                    "proficiency": "proficient"
                }
            }
        )
        
        history = sample_session.progression_state["response_quality_history"]
        assert len(history) == 1
        assert history[0]["confidence"] == 0.8
        assert history[0]["proficiency"] == "proficient"
    
    def test_update_progression_state_phase_change(
        self, assessment_engine, sample_session
    ):
        """Test updating state with phase change."""
        assessment_engine.update_progression_state(
            session=sample_session,
            update_data={
                "type": "phase_change",
                "data": {
                    "phase": "standard"
                }
            }
        )
        
        phase_history = sample_session.progression_state["phase_history"]
        assert len(phase_history) == 2  # Warmup + Standard
        assert phase_history[-1]["phase"] == "standard"
    
    def test_update_progression_state_skill_explored(
        self, assessment_engine, sample_session
    ):
        """Test updating state with explored skill."""
        assessment_engine.update_progression_state(
            session=sample_session,
            update_data={
                "type": "skill_explored",
                "data": {
                    "skill": "react_hooks"
                }
            }
        )
        
        skills_explored = sample_session.progression_state["skills_explored"]
        assert "react_hooks" in skills_explored
    
    def test_get_skills_explored(
        self, assessment_engine, sample_session
    ):
        """Test retrieving explored skills."""
        sample_session.progression_state["skills_explored"] = [
            "react_hooks", "state_management"
        ]
        
        skills = assessment_engine.get_skills_explored(sample_session)
        assert len(skills) == 2
        assert "react_hooks" in skills
    
    def test_get_average_response_quality(
        self, assessment_engine, sample_session
    ):
        """Test calculating average response quality."""
        sample_session.progression_state["response_quality_history"] = [
            {"confidence": 0.8, "accuracy": 0.9},
            {"confidence": 0.7, "accuracy": 0.8}
        ]
        sample_session.progression_state["phase_history"][0]["questions_count"] = 2
        
        avg_quality = assessment_engine.get_average_response_quality(
            sample_session,
            "warmup"
        )
        
        # Average of (0.8+0.9)/2 and (0.7+0.8)/2 = 0.85 and 0.75 = 0.8
        assert 0.79 < avg_quality < 0.81


class TestAnalyzeResponseQuality:
    """Test analyze_response_quality async method."""
    
    @pytest.mark.asyncio
    async def test_analyze_response_expert_level(
        self, assessment_engine, mock_ai_provider
    ):
        """Test AI analysis returns expert proficiency for high-quality response."""
        # Mock AI returns expert-level analysis as JSON string
        import json
        mock_ai_provider.generate_completion.return_value = json.dumps({
            "confidence_level": 0.95,
            "technical_accuracy": 0.98,
            "depth_of_understanding": 0.92,
            "hesitation_indicators": [],
            "proficiency_signal": "expert"
        })
        
        # When: Analyzing expert response
        analysis = await assessment_engine.analyze_response_quality(
            response_text="Detailed expert explanation with proper terminology...",
            question_context={"question": "Explain React hooks", "role_type": "react"}
        )
        
        # Then: Returns expert proficiency
        assert analysis.proficiency_signal == "expert"
        assert analysis.confidence_level >= 0.9
        assert analysis.technical_accuracy >= 0.9
    
    @pytest.mark.asyncio
    async def test_analyze_response_novice_level(
        self, assessment_engine, mock_ai_provider
    ):
        """Test AI analysis returns novice proficiency for low-quality response."""
        # Mock AI returns novice-level analysis as JSON string
        import json
        mock_ai_provider.generate_completion.return_value = json.dumps({
            "confidence_level": 0.3,
            "technical_accuracy": 0.4,
            "depth_of_understanding": 0.3,
            "hesitation_indicators": ["um", "I think", "maybe"],
            "proficiency_signal": "novice"
        })
        
        # When: Analyzing novice response
        analysis = await assessment_engine.analyze_response_quality(
            response_text="Um, I think React hooks are like... functions?",
            question_context={"question": "Explain React hooks", "role_type": "react"}
        )
        
        # Then: Returns novice proficiency
        assert analysis.proficiency_signal == "novice"
        assert analysis.confidence_level < 0.5
        assert analysis.technical_accuracy < 0.6
    
    @pytest.mark.asyncio
    async def test_analyze_response_intermediate_level(
        self, assessment_engine, mock_ai_provider
    ):
        """Test AI analysis returns intermediate proficiency."""
        # Mock AI returns intermediate-level analysis as JSON string
        import json
        mock_ai_provider.generate_completion.return_value = json.dumps({
            "confidence_level": 0.6,
            "technical_accuracy": 0.7,
            "depth_of_understanding": 0.6,
            "hesitation_indicators": ["I believe"],
            "proficiency_signal": "intermediate"
        })
        
        # When: Analyzing intermediate response
        analysis = await assessment_engine.analyze_response_quality(
            response_text="React hooks are functions that let you use state in functional components.",
            question_context={"question": "Explain React hooks", "role_type": "react"}
        )
        
        # Then: Returns intermediate proficiency
        assert analysis.proficiency_signal == "intermediate"
        assert 0.5 <= analysis.confidence_level < 0.8
    
    @pytest.mark.asyncio
    async def test_analyze_response_proficient_level(
        self, assessment_engine, mock_ai_provider
    ):
        """Test AI analysis returns proficient level."""
        # Mock AI returns proficient-level analysis as JSON string
        import json
        mock_ai_provider.generate_completion.return_value = json.dumps({
            "confidence_level": 0.85,
            "technical_accuracy": 0.88,
            "depth_of_understanding": 0.82,
            "hesitation_indicators": [],
            "proficiency_signal": "proficient"
        })
        
        # When: Analyzing proficient response
        analysis = await assessment_engine.analyze_response_quality(
            response_text="React hooks like useState and useEffect provide state and lifecycle features to functional components, following React's functional paradigm.",
            question_context={"question": "Explain React hooks", "role_type": "react"}
        )
        
        # Then: Returns proficient level
        assert analysis.proficiency_signal == "proficient"
        assert analysis.confidence_level >= 0.8
        assert analysis.technical_accuracy >= 0.8
    
    @pytest.mark.asyncio
    async def test_analyze_response_handles_json_parse_error(
        self, assessment_engine, mock_ai_provider
    ):
        """Test fallback when AI returns malformed JSON."""
        # Mock AI returns invalid JSON
        mock_ai_provider.generate_completion.return_value = "Invalid JSON string"
        
        # When: Analyzing response with malformed AI output
        with patch('app.services.progressive_assessment_engine.logger') as mock_logger:
            analysis = await assessment_engine.analyze_response_quality(
                response_text="Some response",
                question_context={"question": "Test question", "role_type": "react"}
            )
        
        # Then: Returns fallback analysis with moderate values
        assert analysis.confidence_level == 0.5
        assert analysis.technical_accuracy == 0.5
        assert analysis.proficiency_signal == "intermediate"
        # Verify error was logged
        mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_response_handles_ai_exception(
        self, assessment_engine, mock_ai_provider
    ):
        """Test fallback when AI provider raises exception."""
        # Mock AI raises exception
        mock_ai_provider.generate_completion.side_effect = Exception("API Error")
        
        # When: Analyzing response with AI failure
        with patch('app.services.progressive_assessment_engine.logger') as mock_logger:
            analysis = await assessment_engine.analyze_response_quality(
                response_text="Some response",
                question_context={"question": "Test question", "role_type": "react"}
            )
        
        # Then: Returns fallback analysis
        assert analysis.confidence_level == 0.5
        assert analysis.proficiency_signal == "intermediate"
        # Verify error was logged
        mock_logger.error.assert_called()


class TestGenerateNextQuestion:
    """Test generate_next_question async method."""
    
    @pytest.mark.asyncio
    async def test_generate_warmup_question(
        self, assessment_engine, mock_ai_provider, sample_session
    ):
        """Test warmup question generation."""
        # Mock AI returns warmup question as JSON string
        import json
        mock_ai_provider.generate_completion.return_value = json.dumps({
            "question": "Tell me about your experience with React",
            "skill_area": "general",
            "difficulty_level": "warmup"
        })
        
        # When: Generating next question in warmup phase
        question = await assessment_engine.generate_next_question(
            session=sample_session,
            role_type="react"
        )
        
        # Then: Returns warmup-level question
        assert question["difficulty_level"] == "warmup"
        assert "question" in question
        assert sample_session.questions_asked_count == 1
    
    @pytest.mark.asyncio
    async def test_generate_advanced_question(
        self, assessment_engine, mock_ai_provider, sample_session
    ):
        """Test advanced question generation."""
        # Set session to advanced phase
        sample_session.current_difficulty_level = "advanced"
        
        # Mock AI returns advanced question as JSON string
        import json
        mock_ai_provider.generate_completion.return_value = json.dumps({
            "question": "How would you optimize a React app rendering 10,000 items?",
            "skill_area": "performance_optimization",
            "difficulty_level": "advanced"
        })
        
        # When: Generating advanced question
        question = await assessment_engine.generate_next_question(
            session=sample_session,
            role_type="react"
        )
        
        # Then: Returns advanced question
        assert question["difficulty_level"] == "advanced"
        assert "performance" in question["question"].lower() or "optimize" in question["question"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_question_avoids_boundary_skills(
        self, assessment_engine, mock_ai_provider, sample_session
    ):
        """Test question generation avoids skills at boundary."""
        # Set boundary for performance_optimization
        sample_session.skill_boundaries_identified = {
            "performance_optimization": "boundary_reached"
        }
        
        # Mock AI returns question for different skill as JSON string
        import json
        mock_ai_provider.generate_completion.return_value = json.dumps({
            "question": "Explain the difference between useState and useReducer",
            "skill_area": "state_management",
            "difficulty_level": "standard"
        })
        
        # When: Generating next question
        question = await assessment_engine.generate_next_question(
            session=sample_session,
            role_type="react"
        )
        
        # Then: Should not ask about boundary skill
        assert question["skill_area"] != "performance_optimization"
        assert question["skill_area"] == "state_management"
    
    @pytest.mark.asyncio
    async def test_generate_question_increments_count(
        self, assessment_engine, mock_ai_provider, sample_session
    ):
        """Test question generation increments questions_asked_count."""
        initial_count = sample_session.questions_asked_count
        
        # Mock AI returns question as JSON string
        import json
        mock_ai_provider.generate_completion.return_value = json.dumps({
            "question": "Test question",
            "skill_area": "general",
            "difficulty_level": "warmup"
        })
        
        # When: Generating question
        await assessment_engine.generate_next_question(
            session=sample_session,
            role_type="react"
        )
        
        # Then: Count incremented
        assert sample_session.questions_asked_count == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_generate_question_handles_json_parse_error(
        self, assessment_engine, mock_ai_provider, sample_session
    ):
        """Test fallback when AI returns malformed JSON."""
        # Mock AI returns invalid JSON
        mock_ai_provider.generate_completion.return_value = "Invalid JSON"
        
        # When: Generating question with malformed AI output
        with patch('app.services.progressive_assessment_engine.logger') as mock_logger:
            question = await assessment_engine.generate_next_question(
                session=sample_session,
                role_type="react"
            )
        
        # Then: Returns fallback generic question
        assert "question" in question
        assert question["skill_area"] == "general_experience"  # Fallback uses this value
        # Verify error was logged
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_generate_question_handles_ai_exception(
        self, assessment_engine, mock_ai_provider, sample_session
    ):
        """Test fallback when AI provider raises exception."""
        # Mock AI raises exception
        mock_ai_provider.generate_completion.side_effect = Exception("API Error")
        
        # When: Generating question with AI failure
        with patch('app.services.progressive_assessment_engine.logger') as mock_logger:
            question = await assessment_engine.generate_next_question(
                session=sample_session,
                role_type="react"
            )
        
        # Then: Returns fallback question
        assert "question" in question
        assert question["difficulty_level"] == sample_session.current_difficulty_level
        # Verify error was logged
        mock_logger.error.assert_called()


# Integration tests are in test_progressive_interview_flow.py
