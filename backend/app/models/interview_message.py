"""InterviewMessage model for storing question-answer exchanges."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class InterviewMessage(Base):
    """
    Interview message model storing each question-answer exchange.

    Attributes:
        id: Unique identifier (UUID)
        interview_id: Foreign key to Interview
        session_id: Foreign key to InterviewSession
        sequence_number: Order of message in conversation
        message_type: Type of message (ai_question or candidate_response)
        content_text: Text content of message
        content_audio_url: Optional URL to audio file
        audio_duration_seconds: Duration of audio in seconds
        audio_metadata: JSONB with audio processing metadata
        response_time_seconds: Time taken for response
        metadata: JSONB with additional metadata
        created_at: Timestamp of message creation
        interview: Related Interview record
        session: Related InterviewSession record
    """

    __tablename__ = "interview_messages"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Message ordering and type
    sequence_number = Column(Integer, nullable=False)
    message_type = Column(
        SQLEnum("ai_question", "candidate_response", name="message_type"),
        nullable=False
    )

    # Content
    content_text = Column(Text, nullable=False)
    content_audio_url = Column(Text, nullable=True)

    # Audio metadata
    audio_duration_seconds = Column(Integer, nullable=True)
    audio_metadata = Column(JSONB, nullable=True)

    # Performance tracking
    response_time_seconds = Column(Integer, nullable=True)

    # Additional metadata (JSONB for flexibility)
    message_metadata = Column(JSONB, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    interview = relationship("Interview", back_populates="messages")
    session = relationship("InterviewSession", back_populates="messages")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<InterviewMessage {self.sequence_number} - "
            f"{self.message_type} - {self.content_text[:50]}>"
        )


# Composite index for efficient chronological retrieval
Index(
    "idx_interview_messages_sequence",
    InterviewMessage.interview_id,
    InterviewMessage.sequence_number
)

# GIN index on message_metadata JSONB for efficient querying
Index(
    "idx_message_metadata_gin",
    InterviewMessage.message_metadata,
    postgresql_using="gin"
)
