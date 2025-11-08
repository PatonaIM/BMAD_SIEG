"""Pydantic schemas for resume data."""
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResumeParsedDataSchema(BaseModel):
    """
    Schema for structured resume parsing results.

    This schema defines the expected output format from GPT-4o-mini resume parsing.
    All fields are required but can be empty (list/0) if data cannot be extracted.

    Attributes:
        skills: Array of technical and soft skills extracted from resume
        experience_years: Total years of professional experience (0-50)
        education: Array of degree names/titles
        past_roles: Array of previous job titles (chronological order)
    """

    model_config = ConfigDict(from_attributes=True)

    skills: list[str] = Field(
        default_factory=list,
        description="Technical and soft skills mentioned in resume"
    )
    experience_years: int = Field(
        default=0,
        ge=0,
        le=50,
        description="Total years of professional experience"
    )
    education: list[str] = Field(
        default_factory=list,
        description="Degrees earned (e.g., Bachelor of Computer Science)"
    )
    past_roles: list[str] = Field(
        default_factory=list,
        description="Previous job titles in chronological order"
    )

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, v: list[str] | None) -> list[str]:
        """
        Normalize skills: lowercase, strip whitespace, deduplicate.

        Args:
            v: List of skill strings

        Returns:
            Normalized and deduplicated list of skills
        """
        if not v:
            return []

        # Normalize: lowercase and strip whitespace
        normalized = [skill.lower().strip() for skill in v if skill and skill.strip()]

        # Deduplicate while preserving order
        seen = set()
        result = []
        for skill in normalized:
            if skill not in seen:
                seen.add(skill)
                result.append(skill)

        return result


class ResumeParsingResponse(BaseModel):
    """
    Schema for resume parsing API response.

    Attributes:
        resume_id: UUID of the parsed resume
        parsing_status: Current status (pending, processing, completed, failed)
        parsed_data: Structured parsed data (if completed)
        error_message: Error details (if failed)
    """

    model_config = ConfigDict(from_attributes=True)

    resume_id: UUID
    parsing_status: str
    parsed_data: ResumeParsedDataSchema | None = None
    error_message: str | None = None


# Story 4.10: Resume Upload & AI Evaluation Schemas

from datetime import datetime


class ResumeUploadResponse(BaseModel):
    """
    Schema for resume upload API response.

    Attributes:
        id: Resume UUID
        file_name: Original filename
        file_size: File size in bytes
        uploaded_at: Upload timestamp
        storage_url: Storage path
        is_active: Whether this is the active resume
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    file_size: int
    uploaded_at: datetime
    storage_url: str = Field(alias="file_url")
    is_active: bool


class ResumeResponse(BaseModel):
    """Schema for resume metadata in list/detail responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    file_size: int
    uploaded_at: datetime
    is_active: bool
    parsing_status: str | None = None


class ResumeAnalysisResponse(BaseModel):
    """
    Schema for resume analysis API response.

    Attributes:
        id: Analysis UUID
        resume_id: UUID of analyzed resume
        overall_score: Quality score (0-100)
        strengths: Array of positive points
        weaknesses: Array of improvement areas
        suggestions: Array of actionable tips
        keywords_missing: Array of missing industry keywords
        analysis_model: AI model used
        analyzed_at: Analysis timestamp
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resume_id: UUID
    overall_score: int
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    keywords_missing: list[str]
    analysis_model: str
    analyzed_at: datetime
