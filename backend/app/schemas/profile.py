"""Pydantic schemas for profile management."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator


class JobPreferencesSchema(BaseModel):
    """
    Job search preferences schema.

    Attributes:
        locations: Preferred work locations (max 10) - DEPRECATED, optional for backward compatibility
        employment_types: permanent, contract, part_time
        work_setups: remote, hybrid, onsite
        salary_min: Minimum desired salary
        salary_max: Maximum desired salary
        salary_currency: Currency code (USD, AUD, etc.)
        salary_period: Salary period (monthly, annually)
        role_categories: engineering, quality_assurance, data, devops, etc.
    """

    locations: list[str] | None = Field(
        None,
        max_length=10,
        description="Preferred work locations (deprecated)"
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
    salary_currency: str | None = Field(
        "USD",
        description="Salary currency code (USD, AUD, EUR, etc.)"
    )
    salary_period: str | None = Field(
        "annually",
        description="Salary period: monthly, annually"
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
    job preferences (flattened for frontend), and calculated completeness score.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    phone: str | None
    skills: list[str] | None
    experience_years: int | None
    
    # Flattened preference fields for frontend compatibility  
    preferred_job_types: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_work_setup: str = "any"
    salary_expectation_min: float | None = None
    salary_expectation_max: float | None = None
    salary_currency: str = "USD"
    salary_period: str = "annually"
    
    profile_completeness_score: Decimal | None

    @model_validator(mode='wrap')
    @classmethod
    def flatten_job_preferences(cls, data, handler):
        """
        Flatten job_preferences JSONB into individual fields.
        
        This wraps the normal validation to transform data before processing.
        """
        # If data is a Candidate object (from database with from_attributes=True)
        if hasattr(data, 'job_preferences'):
            job_prefs = data.job_preferences or {}
            
            # Create dict with all fields
            data_dict = {
                'id': data.id,
                'email': data.email,
                'full_name': data.full_name,
                'phone': data.phone,
                'skills': data.skills,
                'experience_years': data.experience_years,
                'profile_completeness_score': data.profile_completeness_score,
                # Flatten job_preferences
                'preferred_job_types': job_prefs.get('employment_types', []),
                'preferred_locations': job_prefs.get('locations', []),
                'preferred_work_setup': job_prefs.get('work_setups', ['any'])[0] if job_prefs.get('work_setups') else 'any',
                'salary_expectation_min': job_prefs.get('salary_min'),
                'salary_expectation_max': job_prefs.get('salary_max'),
                'salary_currency': job_prefs.get('salary_currency', 'USD'),
                'salary_period': job_prefs.get('salary_period', 'annually'),
            }
            
            # Call the handler with the transformed dict
            return handler(data_dict)
        
        # If it's already a dict, just pass it through
        return handler(data)

    @field_serializer('profile_completeness_score')
    def serialize_completeness(self, value: Decimal | None) -> float | None:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None
    
    @field_serializer('salary_expectation_min', 'salary_expectation_max')
    def serialize_salary(self, value: Decimal | None) -> float | None:
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

    Accepts flattened fields from frontend and transforms to JSONB structure.
    Frontend sends: preferred_job_types, preferred_locations, preferred_work_setup, etc.
    Backend stores: job_preferences JSONB with employment_types, locations, work_setups, etc.
    """

    preferred_job_types: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_work_setup: str = Field(default="any")
    salary_expectation_min: Decimal | None = Field(None, ge=0)
    salary_expectation_max: Decimal | None = Field(None, ge=0)
    salary_currency: str = Field(default="USD")
    salary_period: str = Field(default="annually")

    @field_validator('salary_expectation_max')
    @classmethod
    def validate_salary_range(cls, v: Decimal | None, info) -> Decimal | None:
        """Validate that salary_max >= salary_min if both are provided."""
        if v is not None and info.data.get('salary_expectation_min') is not None:
            if v < info.data['salary_expectation_min']:
                raise ValueError('salary_expectation_max must be >= salary_expectation_min')
        return v

    def to_job_preferences_jsonb(self) -> dict:
        """
        Transform flattened frontend fields to backend JSONB structure.
        
        Frontend format:
            preferred_job_types: ["permanent"]
            preferred_work_setup: "remote"
            salary_expectation_min: 100000
            
        Backend JSONB format:
            employment_types: ["permanent"]
            work_setups: ["remote"]
            salary_min: 100000
        """
        jsonb_data = {}
        
        # Map frontend fields to backend JSONB keys
        if self.preferred_job_types:
            jsonb_data['employment_types'] = self.preferred_job_types
        
        # Only include locations if not empty (deprecated field)
        if self.preferred_locations:
            jsonb_data['locations'] = self.preferred_locations
        
        # Convert single work_setup to array
        if self.preferred_work_setup and self.preferred_work_setup != 'any':
            jsonb_data['work_setups'] = [self.preferred_work_setup]
        
        # Salary fields - convert Decimal to float for JSON serialization
        if self.salary_expectation_min is not None:
            jsonb_data['salary_min'] = float(self.salary_expectation_min)
        
        if self.salary_expectation_max is not None:
            jsonb_data['salary_max'] = float(self.salary_expectation_max)
        
        jsonb_data['salary_currency'] = self.salary_currency
        jsonb_data['salary_period'] = self.salary_period
        
        return jsonb_data
