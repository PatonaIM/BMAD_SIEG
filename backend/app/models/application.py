"""Application model representing candidate job applications."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Application(Base):
    """
    Application model representing candidate applications to job postings.

    Attributes:
        id: Unique identifier (UUID)
        candidate_id: Foreign key to Candidate (CASCADE delete)
        job_posting_id: Foreign key to JobPosting (CASCADE delete)
        interview_id: Optional foreign key to Interview (SET NULL on delete)
        status: Application status (applied, interview_scheduled, interview_completed,
                under_review, rejected, offered, accepted, withdrawn)
        applied_at: Timestamp when candidate applied
        created_at: Timestamp of record creation
        updated_at: Timestamp of last update
        candidate: Related Candidate record
        job_posting: Related JobPosting record
        interview: Related Interview record (nullable)
    """

    __tablename__ = "applications"

    # Table-level constraints
    __table_args__ = (
        UniqueConstraint('candidate_id', 'job_posting_id', name='uq_applications_candidate_job'),
    )

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_posting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Application status
    status = Column(
        SQLEnum(
            "applied",
            "interview_scheduled",
            "interview_completed",
            "under_review",
            "rejected",
            "offered",
            "accepted",
            "withdrawn",
            name="application_status"
        ),
        default="applied",
        nullable=False,
        index=True
    )

    # Timestamps
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job_posting = relationship("JobPosting", back_populates="applications")
    interview = relationship("Interview", back_populates="applications")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Application {self.id} - Candidate:{self.candidate_id} - Job:{self.job_posting_id}>"
