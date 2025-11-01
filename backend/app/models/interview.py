"""Interview model representing interview sessions."""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Interview(Base):
    """
    Interview session model.

    Attributes:
        id: Unique identifier (UUID)
        candidate_id: Foreign key to Candidate
        resume_id: Optional foreign key to Resume
        role_type: Type of role being interviewed for
        status: Current status of interview
        started_at: Timestamp when interview started
        completed_at: Timestamp when interview completed
        duration_seconds: Total duration in seconds
        ai_model_used: AI model identifier (e.g., gpt-4o-mini)
        total_tokens_used: Total tokens consumed
        cost_usd: Estimated AI cost in USD
        speech_tokens_used: Total character count for TTS (cost tracking)
        speech_cost_usd: Estimated speech services cost in USD (STT + TTS)
        created_at: Timestamp of record creation
        candidate: Related Candidate record
        resume: Related Resume record
        session: Related InterviewSession record (one-to-one)
        messages: Related InterviewMessage records
    """

    __tablename__ = "interviews"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True
    )

    # Interview metadata
    role_type = Column(
        SQLEnum("react", "python", "javascript", "fullstack", name="role_type"),
        nullable=False
    )
    status = Column(
        SQLEnum(
            "scheduled",
            "in_progress",
            "completed",
            "abandoned",
            name="interview_status"
        ),
        default="scheduled",
        nullable=False,
        index=True
    )

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # AI tracking
    ai_model_used = Column(String(50), nullable=True)
    total_tokens_used = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Numeric(10, 4), default=Decimal("0.0"), nullable=False)

    # Speech services tracking (STT/TTS)
    speech_tokens_used = Column(Integer, default=0, nullable=False)  # Character count for TTS
    speech_cost_usd = Column(Numeric(10, 4), default=Decimal("0.0"), nullable=False)

    # Record timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    session = relationship(
        "InterviewSession",
        uselist=False,
        back_populates="interview",
        cascade="all, delete-orphan"
    )
    messages = relationship(
        "InterviewMessage",
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="InterviewMessage.sequence_number"
    )
    assessment = relationship(
        "AssessmentResult",
        uselist=False,
        back_populates="interview",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Interview {self.id} - {self.role_type} - {self.status}>"
