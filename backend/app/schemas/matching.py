"""Pydantic schemas for job matching API endpoints."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class PreferenceMatches(BaseModel):
    """
    Breakdown of which candidate preferences matched the job.
    
    Each field represents whether a specific preference criterion was met.
    None indicates the candidate didn't specify that preference.
    """
    location: bool | None = Field(
        None,
        description="Whether job location matches candidate preference (or is remote)"
    )
    work_setup: bool | None = Field(
        None,
        description="Whether work setup (remote/hybrid/onsite) matches preference"
    )
    employment_type: bool | None = Field(
        None,
        description="Whether employment type (permanent/contract) matches preference"
    )
    salary: bool | None = Field(
        None,
        description="Whether salary range overlaps with candidate expectation"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location": True,
                "work_setup": True,
                "employment_type": True,
                "salary": False
            }
        }
    )


class JobMatchResponse(BaseModel):
    """
    Single job match result with similarity score and classification.
    
    Includes complete job details plus matching metadata:
    - match_score: Overall score 0-100 combining similarity and preferences
    - match_classification: Human-readable quality tier
    - similarity_score: Raw semantic similarity 0-1
    - preference_matches: Breakdown of which preferences matched
    """
    # Job details
    id: UUID
    title: str
    company: str
    description: str
    role_category: str
    tech_stack: str | None
    employment_type: str
    work_setup: str
    location: str
    salary_min: Decimal | None
    salary_max: Decimal | None
    salary_currency: str
    required_skills: list[str] | None
    experience_level: str

    # Match metadata
    match_score: Decimal = Field(
        ...,
        ge=0,
        le=100,
        description="Overall match score combining semantic similarity and preference matches"
    )
    match_classification: str = Field(
        ...,
        pattern="^(Excellent|Great|Good|Fair|Poor)$",
        description="Match quality classification: Excellent (≥85%), Great (70-84%), Good (55-69%), Fair (40-54%), Poor (<40%)"
    )
    similarity_score: Decimal = Field(
        ...,
        ge=0,
        le=1,
        description="Semantic similarity score from vector embedding comparison (0-1)"
    )
    preference_matches: PreferenceMatches | None = Field(
        None,
        description="Breakdown of which candidate preferences this job matched"
    )

    @field_serializer('salary_min', 'salary_max', 'match_score', 'similarity_score')
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "description": "Building scalable backend systems...",
                "role_category": "engineering",
                "tech_stack": "Python",
                "employment_type": "permanent",
                "work_setup": "remote",
                "location": "Sydney",
                "salary_min": 100000,
                "salary_max": 140000,
                "salary_currency": "AUD",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience_level": "senior",
                "match_score": 87.5,
                "match_classification": "Excellent",
                "similarity_score": 0.92,
                "preference_matches": {
                    "location": True,
                    "work_setup": True,
                    "employment_type": True,
                    "salary": True
                }
            }
        }
    )


class JobMatchListResponse(BaseModel):
    """
    Paginated list of job matches ranked by match score.
    
    Returns matches in descending order of match_score (best matches first).
    Includes pagination metadata for fetching additional pages.
    """
    matches: list[JobMatchResponse] = Field(
        ...,
        description="List of job matches ranked by match score (highest first)"
    )
    total_count: int = Field(
        ...,
        ge=0,
        description="Total number of matching jobs across all pages"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-indexed)"
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of results per page"
    )
    has_more: bool = Field(
        ...,
        description="Whether more results are available on subsequent pages"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "matches": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Senior Python Developer",
                        "company": "TechCorp",
                        "description": "Building scalable backend systems...",
                        "role_category": "engineering",
                        "tech_stack": "Python",
                        "employment_type": "permanent",
                        "work_setup": "remote",
                        "location": "Sydney",
                        "salary_min": 100000,
                        "salary_max": 140000,
                        "salary_currency": "AUD",
                        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                        "experience_level": "senior",
                        "match_score": 87.5,
                        "match_classification": "Excellent",
                        "similarity_score": 0.92,
                        "preference_matches": {
                            "location": True,
                            "work_setup": True,
                            "employment_type": True,
                            "salary": True
                        }
                    }
                ],
                "total_count": 42,
                "page": 1,
                "page_size": 20,
                "has_more": True
            }
        }
    )


class JobMatchQueryParams(BaseModel):
    """
    Query parameters for job matching endpoint.
    
    Controls pagination of match results.
    """
    page: int = Field(
        1,
        ge=1,
        description="Page number (1-indexed)"
    )
    page_size: int = Field(
        20,
        ge=1,
        le=100,
        description="Number of results per page (max 100)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "page_size": 20
            }
        }
    )


class MatchExplanationResponse(BaseModel):
    """
    AI-generated explanation for job-candidate match.
    
    Provides detailed reasoning about why a job matches a candidate's profile,
    including specific matching factors, missing requirements, and an overall
    assessment. Generated using GPT-4o-mini for cost efficiency.
    """
    matching_factors: list[str] = Field(
        ...,
        description="List of reasons why the job matches the candidate (3-10 items)",
        min_length=1,
        max_length=10
    )
    missing_requirements: list[str] = Field(
        ...,
        description="List of gaps or missing qualifications (0-5 items)",
        max_length=5
    )
    overall_reasoning: str = Field(
        ...,
        description="2-3 sentence summary of the match quality",
        min_length=50,
        max_length=500
    )
    confidence_score: Decimal = Field(
        ...,
        ge=0,
        le=1,
        description="AI confidence in the explanation (0-1)"
    )

    @field_serializer('confidence_score')
    def serialize_confidence(self, value: Decimal) -> float:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "matching_factors": [
                    "5+ years Python experience matches Senior requirement",
                    "Remote preference aligns with job's remote work setup",
                    "React and TypeScript skills match 80% of required skills",
                    "Salary expectation aligns with job's compensation range"
                ],
                "missing_requirements": [
                    "Job requires GraphQL experience, not listed in profile",
                    "Preferred experience with AWS cloud services"
                ],
                "overall_reasoning": "This is a Great match based on strong technical skill alignment and work setup preferences. The candidate has most required skills and the remote setup is ideal. Some additional skills like GraphQL would strengthen the application.",
                "confidence_score": 0.85
            }
        }
    )
