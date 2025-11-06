"""Pydantic schemas for job posting API endpoints."""
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobPostingFilters(BaseModel):
    """
    Query parameters for filtering job postings.

    All filters are optional and can be combined using AND logic.
    """
    role_category: str | None = Field(
        None,
        description="Filter by role category (engineering, quality_assurance, data, devops, design, product, sales, support, operations, management, other)"
    )
    tech_stack: str | None = Field(
        None,
        description="Filter by technology stack (case-insensitive partial match)"
    )
    employment_type: str | None = Field(
        None,
        description="Filter by employment type (permanent, contract, part_time)"
    )
    work_setup: str | None = Field(
        None,
        description="Filter by work arrangement (remote, hybrid, onsite)"
    )
    experience_level: str | None = Field(
        None,
        description="Filter by experience level"
    )
    location: str | None = Field(
        None,
        description="Filter by location (case-insensitive partial match)"
    )
    search: str | None = Field(
        None,
        description="Search in job title and company name (case-insensitive)"
    )
    skip: int = Field(
        0,
        ge=0,
        description="Number of records to skip for pagination"
    )
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Maximum number of records to return (max: 100)"
    )


class JobPostingResponse(BaseModel):
    """
    Schema for individual job posting in API responses.

    Includes all job posting fields for display and filtering.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Senior Frontend Developer",
            "company": "Tech Corp",
            "description": "We are looking for...",
            "role_category": "engineering",
            "tech_stack": "React",
            "employment_type": "permanent",
            "work_setup": "remote",
            "location": "Sydney, NSW, Australia",
            "salary_min": 120000.00,
            "salary_max": 150000.00,
            "salary_currency": "AUD",
            "required_skills": ["React", "TypeScript", "Node.js"],
            "experience_level": "Senior",
            "status": "active",
            "is_cancelled": false,
            "cancellation_reason": null,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    """
    model_config = ConfigDict(from_attributes=True)

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
    required_skills: list[Any] | None
    experience_level: str
    status: str
    is_cancelled: bool
    cancellation_reason: str | None
    created_at: datetime
    updated_at: datetime


class JobPostingListResponse(BaseModel):
    """
    Schema for paginated job posting list responses.

    Includes pagination metadata for frontend display and navigation.

    Example:
        {
            "jobs": [...],
            "total": 42,
            "skip": 0,
            "limit": 20
        }
    """
    jobs: list[JobPostingResponse] = Field(
        ...,
        description="List of job postings matching the filter criteria"
    )
    total: int = Field(
        ...,
        description="Total number of job postings matching filters (for pagination)"
    )
    skip: int = Field(
        ...,
        description="Number of records skipped"
    )
    limit: int = Field(
        ...,
        description="Maximum number of records returned"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "jobs": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "Senior Frontend Developer",
                            "company": "Tech Corp",
                            "description": "We are looking for an experienced frontend developer...",
                            "role_category": "engineering",
                            "tech_stack": "React",
                            "employment_type": "permanent",
                            "work_setup": "remote",
                            "location": "Sydney, NSW, Australia",
                            "salary_min": 120000.00,
                            "salary_max": 150000.00,
                            "salary_currency": "AUD",
                            "required_skills": ["React", "TypeScript", "Node.js"],
                            "experience_level": "Senior",
                            "status": "active",
                            "is_cancelled": False,
                            "cancellation_reason": None,
                            "created_at": "2025-01-01T00:00:00",
                            "updated_at": "2025-01-01T00:00:00"
                        }
                    ],
                    "total": 42,
                    "skip": 0,
                    "limit": 20
                }
            ]
        }
    )
