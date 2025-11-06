"""Pydantic schemas for application API endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreateRequest(BaseModel):
    """
    Request schema for creating a new application.

    Example:
        {
            "job_posting_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    """
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "job_posting_id": "123e4567-e89b-12d3-a456-426614174000"
            }]
        }
    )

    job_posting_id: UUID = Field(
        ...,
        description="ID of the job posting to apply to"
    )


class JobPostingBasicResponse(BaseModel):
    """Basic job posting information for nested responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    company: str
    role_category: str
    tech_stack: str | None
    employment_type: str
    work_setup: str
    location: str
    status: str


class InterviewBasicResponse(BaseModel):
    """Basic interview information for nested responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    role_type: str


class ApplicationResponse(BaseModel):
    """
    Schema for application in API responses with nested relationships.

    Includes full application details with eager-loaded job posting and interview data.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "candidate_id": "123e4567-e89b-12d3-a456-426614174002",
            "job_posting_id": "123e4567-e89b-12d3-a456-426614174000",
            "interview_id": "123e4567-e89b-12d3-a456-426614174003",
            "status": "interview_scheduled",
            "applied_at": "2025-11-04T10:30:00",
            "created_at": "2025-11-04T10:30:00",
            "updated_at": "2025-11-04T10:31:00",
            "job_posting": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Senior React Developer",
                "company": "Tech Corp",
                "role_category": "engineering",
                "tech_stack": "react",
                "employment_type": "permanent",
                "work_setup": "remote",
                "location": "Sydney, NSW, Australia",
                "status": "active"
            },
            "interview": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "status": "in_progress",
                "role_type": "react"
            }
        }
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "candidate_id": "123e4567-e89b-12d3-a456-426614174002",
                "job_posting_id": "123e4567-e89b-12d3-a456-426614174000",
                "interview_id": "123e4567-e89b-12d3-a456-426614174003",
                "status": "interview_scheduled",
                "applied_at": "2025-11-04T10:30:00",
                "created_at": "2025-11-04T10:30:00",
                "updated_at": "2025-11-04T10:31:00",
                "job_posting": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Senior React Developer",
                    "company": "Tech Corp",
                    "role_category": "engineering",
                    "tech_stack": "react",
                    "employment_type": "permanent",
                    "work_setup": "remote",
                    "location": "Sydney, NSW, Australia",
                    "status": "active"
                },
                "interview": {
                    "id": "123e4567-e89b-12d3-a456-426614174003",
                    "status": "in_progress",
                    "role_type": "react"
                }
            }]
        }
    )

    # Application fields
    id: UUID
    candidate_id: UUID
    job_posting_id: UUID
    interview_id: UUID | None
    status: str
    applied_at: datetime
    created_at: datetime
    updated_at: datetime

    # Nested relationships
    job_posting: JobPostingBasicResponse
    interview: InterviewBasicResponse | None = Field(
        None,
        description="Basic interview info if linked"
    )


class ApplicationDetailResponse(BaseModel):
    """
    Schema for single application detail response.

    Same as ApplicationResponse but can be extended for additional detail fields.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "candidate_id": "123e4567-e89b-12d3-a456-426614174002",
            "job_posting_id": "123e4567-e89b-12d3-a456-426614174000",
            "interview_id": "123e4567-e89b-12d3-a456-426614174003",
            "status": "interview_scheduled",
            "applied_at": "2025-11-04T10:30:00",
            "created_at": "2025-11-04T10:30:00",
            "updated_at": "2025-11-04T10:31:00",
            "job_posting": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Senior React Developer",
                "company": "Tech Corp",
                "role_category": "engineering",
                "tech_stack": "react",
                "employment_type": "permanent",
                "work_setup": "remote",
                "location": "Sydney, NSW, Australia",
                "status": "active"
            },
            "interview": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "status": "in_progress",
                "role_type": "react"
            }
        }
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "candidate_id": "123e4567-e89b-12d3-a456-426614174002",
                "job_posting_id": "123e4567-e89b-12d3-a456-426614174000",
                "interview_id": "123e4567-e89b-12d3-a456-426614174003",
                "status": "interview_scheduled",
                "applied_at": "2025-11-04T10:30:00",
                "created_at": "2025-11-04T10:30:00",
                "updated_at": "2025-11-04T10:31:00",
                "job_posting": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Senior React Developer",
                    "company": "Tech Corp",
                    "role_category": "engineering",
                    "tech_stack": "react",
                    "employment_type": "permanent",
                    "work_setup": "remote",
                    "location": "Sydney, NSW, Australia",
                    "status": "active"
                },
                "interview": {
                    "id": "123e4567-e89b-12d3-a456-426614174003",
                    "status": "in_progress",
                    "role_type": "react"
                }
            }]
        }
    )

    # Application fields
    id: UUID
    candidate_id: UUID
    job_posting_id: UUID
    interview_id: UUID | None
    status: str
    applied_at: datetime
    created_at: datetime
    updated_at: datetime

    # Nested relationships
    job_posting: JobPostingBasicResponse
    interview: InterviewBasicResponse | None = Field(
        None,
        description="Basic interview info if linked"
    )
