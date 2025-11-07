"""Pydantic schemas for profile management."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class JobPreferencesSchema(BaseModel):
    """
    Job search preferences schema.

    Attributes:
        locations: Preferred work locations (max 10)
        employment_types: permanent, contract, part_time
        work_setups: remote, hybrid, onsite
        salary_min: Minimum desired salary
        salary_max: Maximum desired salary
        role_categories: engineering, quality_assurance, data, devops, etc.
    """

    locations: list[str] | None = Field(
        None,
        max_length=10,
        description="Preferred work locations"
    )
    employment_types: list[str] | None = Field(
        None,
        description="Employment types: permanent, contract, part_time"
    )
    work_setups: list[str] | None = Field(
        None,
        description="Work setups: remote, hybrid, onsite"
    )
    salary_min: Decimal | None = Field(
        None,
        ge=0,
        description="Minimum desired salary"
    )
    salary_max: Decimal | None = Field(
        None,
        ge=0,
        description="Maximum desired salary"
    )
    role_categories: list[str] | None = Field(
        None,
        description="Role categories: engineering, quality_assurance, data, devops, design, product, etc."
    )

    @field_validator('salary_max')
    @classmethod
    def validate_salary_range(cls, v: Decimal | None, info) -> Decimal | None:
        """Validate that salary_max >= salary_min if both are provided."""
        if v is not None and info.data.get('salary_min') is not None and v < info.data['salary_min']:
            raise ValueError('salary_max must be >= salary_min')
        return v

    @field_serializer('salary_min', 'salary_max')
    def serialize_salary(self, value: Decimal | None) -> float | None:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None


class ProfileResponse(BaseModel):
    """
    Profile data in API responses.

    Returns complete candidate profile including skills, experience,
    job preferences, and calculated completeness score.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    phone: str | None
    skills: list[str] | None
    experience_years: int | None
    job_preferences: dict | None
    profile_completeness_score: Decimal | None

    @field_serializer('profile_completeness_score')
    def serialize_completeness(self, value: Decimal | None) -> float | None:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None


class SkillsUpdateRequest(BaseModel):
    """
    Request schema for updating candidate skills.

    Skills will be automatically normalized (lowercase, deduplicated, sorted).
    """

    skills: list[str] = Field(..., max_length=50, description="List of skills (max 50)")

    @field_validator('skills')
    @classmethod
    def normalize_skills(cls, v: list[str]) -> list[str]:
        """
        Normalize skills: lowercase, trim whitespace, deduplicate, sort.

        Example:
            Input: ["React", "  TypeScript ", "react", "Node.js"]
            Output: ["node.js", "react", "typescript"]
        """
        if v is None:
            return []

        # Normalize: lowercase, trim, filter empty, deduplicate, sort
        normalized = set()
        for skill in v:
            cleaned = skill.strip().lower()
            if cleaned:  # Skip empty strings
                normalized.add(cleaned)

        return sorted(normalized)


class ExperienceUpdateRequest(BaseModel):
    """
    Request schema for updating experience years.

    Experience years must be between 0 and 50.
    """

    experience_years: int = Field(
        ...,
        ge=0,
        le=50,
        description="Years of professional experience (0-50)"
    )


class PreferencesUpdateRequest(BaseModel):
    """
    Request schema for updating job preferences.

    Accepts a JobPreferencesSchema object with flexible fields.
    """

    job_preferences: JobPreferencesSchema = Field(
        ...,
        description="Job search preferences object"
    )
