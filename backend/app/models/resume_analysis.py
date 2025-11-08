"""Resume analysis model for AI-powered resume evaluation."""
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ResumeAnalysis(Base):
    """
    Resume analysis model for storing AI evaluation results.

    Attributes:
        id: Unique identifier (UUID)
        resume_id: Foreign key to Resume
        overall_score: Score from 0-100 rating resume quality
        strengths: Array of positive points (JSONB)
        weaknesses: Array of improvement areas (JSONB)
        suggestions: Array of actionable tips (JSONB)
        keywords_missing: Array of missing industry keywords (JSONB)
        analysis_model: AI model used for analysis (e.g., 'gpt-4o-mini')
        tokens_used: Number of tokens consumed for analysis
        analyzed_at: Timestamp when analysis completed
        created_at: Timestamp when record created
        resume: Related Resume record
    """

    __tablename__ = "resume_analyses"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Analysis results
    overall_score = Column(Integer, nullable=False)
    strengths = Column(JSONB, nullable=False, default=list)
    weaknesses = Column(JSONB, nullable=False, default=list)
    suggestions = Column(JSONB, nullable=False, default=list)
    keywords_missing = Column(JSONB, nullable=False, default=list)

    # AI model tracking
    analysis_model = Column(String(50), default="gpt-4o-mini")
    tokens_used = Column(Integer, default=0)

    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("overall_score >= 0 AND overall_score <= 100", name="check_score_range"),
    )

    # Relationships
    resume = relationship("Resume", backref="analyses")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<ResumeAnalysis score={self.overall_score} resume_id={self.resume_id}>"
