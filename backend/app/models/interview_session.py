"""InterviewSession model for managing conversation state."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class InterviewSession(Base):
    """
    Interview session model managing LangChain conversation state.

    Attributes:
        id: Unique identifier (UUID)
        interview_id: Foreign key to Interview (unique, one-to-one)
        conversation_memory: JSONB storing LangChain memory state
        current_difficulty_level: Current question difficulty
        questions_asked_count: Number of questions asked
        skill_boundaries_identified: JSONB of identified skill boundaries
        progression_state: JSONB of progression algorithm state
        last_activity_at: Timestamp of last activity
        interview: Related Interview record
    """

    __tablename__ = "interview_sessions"

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

    # LangChain conversation state (JSONB for flexibility)
    conversation_memory = Column(JSONB, nullable=True)

    # Progressive assessment state
    current_difficulty_level = Column(
        SQLEnum("warmup", "standard", "advanced", name="difficulty_level"),
        default="warmup",
        nullable=False
    )
    questions_asked_count = Column(Integer, default=0, nullable=False)

    # Skill mapping (JSONB for flexible AI data)
    skill_boundaries_identified = Column(JSONB, nullable=True)
    progression_state = Column(JSONB, nullable=True)

    # Activity tracking
    last_activity_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    interview = relationship("Interview", back_populates="session")
    messages = relationship(
        "InterviewMessage",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<InterviewSession {self.id} - {self.current_difficulty_level}>"


# Create GIN indexes for JSONB columns for efficient querying
Index(
    "idx_conversation_memory_gin",
    InterviewSession.conversation_memory,
    postgresql_using="gin"
)
Index(
    "idx_skill_boundaries_gin",
    InterviewSession.skill_boundaries_identified,
    postgresql_using="gin"
)
Index(
    "idx_progression_state_gin",
    InterviewSession.progression_state,
    postgresql_using="gin"
)
