"""Pydantic schemas for authentication."""
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CandidateRegisterRequest(BaseModel):
    """Schema for candidate registration request."""

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    password: str = Field(..., min_length=8)
    phone: str | None = Field(None, max_length=50)


class CandidateLoginRequest(BaseModel):
    """Schema for candidate login request."""

    email: EmailStr
    password: str


class AuthTokenResponse(BaseModel):
    """Schema for authentication token response."""

    token: str
    candidate_id: UUID
    email: str
    full_name: str


class CandidateResponse(BaseModel):
    """Schema for candidate data in responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    phone: str | None
    status: str
