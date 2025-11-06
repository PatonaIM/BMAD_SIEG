"""Job posting model representing available job positions."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class JobPosting(Base):
    """
    Job posting model representing available job positions.

    Attributes:
        id: Unique identifier (UUID)
        title: Job title/position name
        company: Company name offering the position
        description: Detailed job description
        role_category: Job function category (engineering, quality_assurance, data, devops,
                      design, product, sales, support, operations, management, other)
        tech_stack: Primary technology/stack (e.g., 'React', 'Python', 'TypeScript', 'Playwright')
                   Nullable for non-technical roles
        employment_type: Type of employment (permanent, contract, part_time)
        work_setup: Work arrangement (remote, hybrid, onsite)
        location: Job location (city, state, country)
        salary_min: Minimum salary range
        salary_max: Maximum salary range
        salary_currency: Salary currency code (default 'AUD')
        required_skills: JSON array of required skills/qualifications
        experience_level: Required experience level (e.g., 'Junior', 'Mid', 'Senior')
        status: Job posting status (active, paused, closed) - default 'active'
        is_cancelled: Whether job posting has been cancelled
        cancellation_reason: Reason for cancellation if applicable
        created_at: Timestamp of job posting creation
        updated_at: Timestamp of last update
        applications: Related Application records
    """

    __tablename__ = "job_postings"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic fields
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Job categorization
    role_category = Column(
        SQLEnum(
            "engineering",
            "quality_assurance",
            "data",
            "devops",
            "design",
            "product",
            "sales",
            "support",
            "operations",
            "management",
            "other",
            name="role_category"
        ),
        nullable=False,
        index=True
    )
    tech_stack = Column(String(100), nullable=True)  # Flexible VARCHAR for any tech

    # Employment details
    employment_type = Column(
        SQLEnum("permanent", "contract", "part_time", name="employment_type"),
        nullable=False
    )
    work_setup = Column(
        SQLEnum("remote", "hybrid", "onsite", name="work_setup"),
        nullable=False
    )
    location = Column(String(255), nullable=False)

    # Compensation
    salary_min = Column(Numeric(10, 2), nullable=True)
    salary_max = Column(Numeric(10, 2), nullable=True)
    salary_currency = Column(String(3), nullable=False, default="AUD")

    # Requirements
    required_skills = Column(JSONB, nullable=True)
    experience_level = Column(String(50), nullable=False)

    # Status management
    status = Column(
        SQLEnum("active", "paused", "closed", name="job_posting_status"),
        default="active",
        nullable=False
    )
    is_cancelled = Column(Boolean, default=False, nullable=False)
    cancellation_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    applications = relationship(
        "Application",
        back_populates="job_posting",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    interviews = relationship(
        "Interview",
        back_populates="job_posting"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<JobPosting {self.title} at {self.company}>"
