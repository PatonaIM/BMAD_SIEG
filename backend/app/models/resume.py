"""Resume model for candidate resumes (placeholder for later stories)."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Resume(Base):
    """
    Resume model for storing candidate resume information.

    Note: Minimal implementation for Story 1.2. Full parsing logic in later stories.

    Attributes:
        id: Unique identifier (UUID)
        candidate_id: Foreign key to Candidate
        file_url: URL/path to resume file
        file_name: Original filename
        file_size: File size in bytes
        uploaded_at: Timestamp of upload
        parsed_at: Timestamp when parsing completed
        parsing_status: Status of parsing process
        parsed_data: JSONB with parsed resume data
        candidate: Related Candidate record
        interviews: Related Interview records
    """

    __tablename__ = "resumes"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # File metadata
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    parsed_at = Column(DateTime, nullable=True)

    # Parsing status
    parsing_status = Column(
        SQLEnum("pending", "processing", "completed", "failed", name="parsing_status"),
        default="pending",
        nullable=False,
        index=True
    )

    # Parsed content (JSONB for flexible structure)
    parsed_data = Column(JSONB, nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")
    interviews = relationship("Interview", back_populates="resume")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Resume {self.file_name} - {self.parsing_status}>"
