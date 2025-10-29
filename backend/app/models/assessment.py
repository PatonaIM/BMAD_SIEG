"""AssessmentResult model for interview scoring (placeholder for later stories)."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AssessmentResult(Base):
    """
    Assessment result model for interview scoring.

    Note: Minimal implementation for Story 1.2. Full scoring logic in later stories.

    Attributes:
        id: Unique identifier (UUID)
        interview_id: Foreign key to Interview (unique, one-to-one)
        overall_score: Overall candidate score (0-100)
        skill_scores: JSONB with individual skill scores
        skill_boundary_map: JSONB with skill boundary data
        strengths: JSONB with identified strengths
        weaknesses: JSONB with identified weaknesses
        integrity_score: Score for integrity/authenticity (0-100)
        integrity_flags: JSONB with integrity warning flags
        ai_reasoning: JSONB with AI reasoning for scores
        recommended_actions: JSONB with hiring recommendations
        generated_at: Timestamp when assessment was generated
        interview: Related Interview record
    """

    __tablename__ = "assessment_results"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key (unique for one-to-one relationship)
    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # Scores
    overall_score = Column(Numeric(5, 2), nullable=False)
    integrity_score = Column(Numeric(5, 2), nullable=True)

    # Detailed results (JSONB for flexible AI-generated content)
    skill_scores = Column(JSONB, nullable=False)
    skill_boundary_map = Column(JSONB, nullable=True)
    strengths = Column(JSONB, nullable=True)
    weaknesses = Column(JSONB, nullable=True)
    integrity_flags = Column(JSONB, nullable=True)
    ai_reasoning = Column(JSONB, nullable=True)
    recommended_actions = Column(JSONB, nullable=True)

    # Timestamp
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    interview = relationship("Interview", back_populates="assessment")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<AssessmentResult {self.interview_id} - Score: {self.overall_score}>"


# GIN indexes for JSONB columns
Index(
    "idx_skill_scores_gin",
    AssessmentResult.skill_scores,
    postgresql_using="gin"
)
Index(
    "idx_ai_reasoning_gin",
    AssessmentResult.ai_reasoning,
    postgresql_using="gin"
)
