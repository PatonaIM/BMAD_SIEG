"""Profile management API endpoints."""
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_db, get_profile_service
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.candidate import Candidate
from app.schemas.profile import (
    BasicInfoUpdateRequest,
    ExperienceUpdateRequest,
    PreferencesUpdateRequest,
    ProfileResponse,
    SkillsUpdateRequest,
)
from app.services.profile_service import ProfileService

logger = structlog.get_logger()

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: Annotated[Candidate, Depends(get_current_user)],
) -> ProfileResponse:
    """
    Get authenticated candidate's profile.

    Returns complete profile with skills, experience, preferences,
    and calculated completeness score.

    **Authentication Required:** Bearer token (JWT)

    **Response:**
    ```json
    {
      "id": "uuid",
      "email": "john@example.com",
      "full_name": "John Doe",
      "phone": "+1234567890",
      "skills": ["python", "react", "typescript"],
      "experience_years": 5,
      "job_preferences": {
        "locations": ["Remote Australia"],
        "employment_types": ["permanent"],
        "work_setups": ["remote"],
        "salary_min": 120000.00,
        "salary_max": 150000.00,
        "role_categories": ["engineering"]
      },
      "profile_completeness_score": 85.00
    }
    ```
    """
    logger.info(
        "get_profile_request",
        candidate_id=str(current_user.id)
    )

    # Debug: log the job_preferences value
    logger.info(
        "get_profile_job_preferences",
        candidate_id=str(current_user.id),
        job_preferences=current_user.job_preferences
    )

    # Return profile directly from current_user (already fetched with relationships)
    response = ProfileResponse.model_validate(current_user)
    
    # Debug: log the response data being sent to frontend
    logger.info(
        "get_profile_response",
        candidate_id=str(current_user.id),
        preferred_job_types=response.preferred_job_types,
        preferred_work_setup=response.preferred_work_setup,
        salary_expectation_min=response.salary_expectation_min,
        salary_expectation_max=response.salary_expectation_max,
        salary_currency=response.salary_currency
    )
    
    return response


@router.put("/skills", response_model=ProfileResponse)
async def update_skills(
    request: SkillsUpdateRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProfileResponse:
    """
    Update candidate skills.

    Skills are automatically normalized (lowercase, deduplicated, sorted).
    Profile completeness score is recalculated after update.

    **Authentication Required:** Bearer token (JWT)

    **Request Body:**
    ```json
    {
      "skills": ["React", "Python", "TypeScript"]
    }
    ```

    **Response:** Updated ProfileResponse with new skills and completeness score.
    """
    logger.info(
        "update_skills_request",
        candidate_id=str(current_user.id),
        skill_count=len(request.skills)
    )

    candidate = await profile_service.update_skills(
        candidate_id=current_user.id,
        skills=request.skills
    )

    await db.commit()

    return ProfileResponse.model_validate(candidate)


@router.put("/basic-info", response_model=ProfileResponse)
async def update_basic_info(
    request: BasicInfoUpdateRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProfileResponse:
    """
    Update candidate basic information (name, phone, experience).

    Profile completeness score is recalculated after update.

    **Authentication Required:** Bearer token (JWT)

    **Request Body:**
    ```json
    {
      "full_name": "John Doe",
      "phone": "+1234567890",
      "experience_years": 5
    }
    ```

    **Response:** Updated ProfileResponse with new basic info and completeness score.
    """
    logger.info(
        "update_basic_info_request",
        candidate_id=str(current_user.id),
        full_name_provided=request.full_name is not None,
        phone_provided=request.phone is not None,
        experience_years_provided=request.experience_years is not None
    )

    candidate = await profile_service.update_basic_info(
        candidate_id=current_user.id,
        full_name=request.full_name,
        phone=request.phone,
        experience_years=request.experience_years
    )

    await db.commit()

    return ProfileResponse.model_validate(candidate)


@router.put("/experience", response_model=ProfileResponse)
async def update_experience(
    request: ExperienceUpdateRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProfileResponse:
    """
    Update candidate experience years.

    Experience years must be between 0 and 50.
    Profile completeness score is recalculated after update.

    **Authentication Required:** Bearer token (JWT)

    **Request Body:**
    ```json
    {
      "experience_years": 5
    }
    ```

    **Response:** Updated ProfileResponse with new experience and completeness score.
    """
    logger.info(
        "update_experience_request",
        candidate_id=str(current_user.id),
        experience_years=request.experience_years
    )

    candidate = await profile_service.update_experience(
        candidate_id=current_user.id,
        years=request.experience_years
    )

    await db.commit()

    return ProfileResponse.model_validate(candidate)


@router.put("/preferences", response_model=ProfileResponse)
async def update_preferences(
    request: PreferencesUpdateRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProfileResponse:
    """
    Update candidate job preferences.

    Accepts flattened preference fields from frontend and stores as JSONB.
    Profile completeness score is recalculated after update.

    **Authentication Required:** Bearer token (JWT)

    **Request Body:**
    ```json
    {
      "preferred_job_types": ["Full Time", "Contract"],
      "preferred_locations": [],
      "preferred_work_setup": "remote",
      "salary_expectation_min": 120000,
      "salary_expectation_max": 150000,
      "salary_currency": "USD",
      "salary_period": "annually"
    }
    ```

    **Response:** Updated ProfileResponse with new preferences and completeness score.
    """
    logger.info(
        "update_preferences_request",
        candidate_id=str(current_user.id)
    )

    # Transform flattened frontend format to JSONB structure
    preferences_dict = request.to_job_preferences_jsonb()

    candidate = await profile_service.update_preferences(
        candidate_id=current_user.id,
        preferences=preferences_dict
    )

    await db.commit()

    return ProfileResponse.model_validate(candidate)
