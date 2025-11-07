"""Candidate model representing job seekers."""
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Candidate(Base):
    """
    Candidate model representing job seekers.

    Attributes:
        id: Unique identifier (UUID)
        email: Unique email address (indexed)
        full_name: Candidate's full name
        password_hash: Hashed password for authentication
        phone: Optional phone number
        status: Account status (active, inactive, deleted)
        skills: Array of skill strings (JSONB)
        experience_years: Years of professional experience (INTEGER)
        job_preferences: Job search preferences object (JSONB)
        profile_completeness_score: Profile completion percentage 0-100 (DECIMAL)
        profile_embedding: Semantic embedding vector for matching (vector(3072))
        created_at: Timestamp of account creation
        updated_at: Timestamp of last update
        resumes: Related Resume records
        interviews: Related Interview records
    """

    __tablename__ = "candidates"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)

    # Status enum
    status = Column(
        SQLEnum("active", "inactive", "deleted", name="candidate_status"),
        default="active",
        nullable=False,
        index=True
    )

    # Epic 04: Profile fields for intelligent job matching
    skills = Column(JSONB, nullable=True, comment="Array of skill strings")
    experience_years = Column(Integer, nullable=True, comment="Years of professional experience")
    job_preferences = Column(JSONB, nullable=True, comment="Job search preferences object")
    profile_completeness_score = Column(
        Numeric(5, 2), nullable=True, comment="Profile completion percentage 0-100"
    )
    profile_embedding = Column(
        Vector(3072), nullable=True, comment="Semantic embedding for matching"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    resumes = relationship(
        "Resume",
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    interviews = relationship(
        "Interview",
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    applications = relationship(
        "Application",
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Candidate {self.email}>"
