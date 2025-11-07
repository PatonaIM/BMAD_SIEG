"""Profile management API endpoints."""
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_profile_service
from app.models.candidate import Candidate
from app.schemas.profile import (
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

    # Return profile directly from current_user (already fetched with relationships)
    return ProfileResponse.model_validate(current_user)


@router.put("/skills", response_model=ProfileResponse)
async def update_skills(
    request: SkillsUpdateRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)]
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

    return ProfileResponse.model_validate(candidate)


@router.put("/experience", response_model=ProfileResponse)
async def update_experience(
    request: ExperienceUpdateRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)]
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

    return ProfileResponse.model_validate(candidate)


@router.put("/preferences", response_model=ProfileResponse)
async def update_preferences(
    request: PreferencesUpdateRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)]
) -> ProfileResponse:
    """
    Update candidate job preferences.

    Accepts flexible job preferences object with locations, employment types,
    work setups, salary range, and role categories.
    Profile completeness score is recalculated after update.

    **Authentication Required:** Bearer token (JWT)

    **Request Body:**
    ```json
    {
      "job_preferences": {
        "locations": ["Remote Australia", "Sydney"],
        "employment_types": ["permanent", "contract"],
        "work_setups": ["remote", "hybrid"],
        "salary_min": 120000,
        "salary_max": 150000,
        "role_categories": ["engineering", "quality_assurance"]
      }
    }
    ```

    **Response:** Updated ProfileResponse with new preferences and completeness score.
    """
    logger.info(
        "update_preferences_request",
        candidate_id=str(current_user.id)
    )

    # Convert Pydantic model to dict for JSONB storage
    preferences_dict = request.job_preferences.model_dump(exclude_none=True)

    candidate = await profile_service.update_preferences(
        candidate_id=current_user.id,
        preferences=preferences_dict
    )

    return ProfileResponse.model_validate(candidate)
