"""Matching API routes for job recommendations."""
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user, get_explanation_service, get_matching_service
from app.models.candidate import Candidate
from app.schemas.matching import JobMatchListResponse, MatchExplanationResponse
from app.services.explanation_service import ExplanationService
from app.services.matching_service import MatchingService

logger = structlog.get_logger().bind(module="matching_api")

router = APIRouter(prefix="/matching", tags=["matching"])


@router.get("/jobs", response_model=JobMatchListResponse)
async def get_job_matches(
    current_user: Annotated[Candidate, Depends(get_current_user)],
    matching_service: Annotated[MatchingService, Depends(get_matching_service)],
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page (max 100)")
) -> JobMatchListResponse:
    """
    Get AI-powered job recommendations for authenticated candidate.
    
    Returns jobs ranked by semantic similarity combined with preference matching.
    Uses vector embeddings to find semantically similar jobs based on candidate's
    skills, experience, and preferences.
    
    **Match Score Calculation:**
    - 70% weight: Semantic similarity from vector embeddings
    - 30% weight: Preference matching (location, work_setup, employment_type, salary)
    - Final score: 0-100 scale
    
    **Match Classifications:**
    - Excellent: ≥85% match
    - Great: 70-84% match
    - Good: 55-69% match
    - Fair: 40-54% match
    - Poor: <40% match
    
    **Requirements:**
    - Authenticated candidate (JWT token)
    - Profile completeness ≥40%
    - Profile embedding available
    
    **Authentication Required:** Bearer token (JWT)
    
    **Returns:**
    - 200 OK: List of job matches with scores and classifications
    - 400 Bad Request: Profile embedding not available
    - 401 Unauthorized: Invalid or missing authentication token
    - 403 Forbidden: Profile completeness below 40%
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - page_size: Results per page (default: 20, max: 100)
    
    **Example Request:**
    ```
    GET /api/v1/matching/jobs?page=1&page_size=20
    Authorization: Bearer <jwt_token>
    ```
    
    **Example Response:**
    ```json
    {
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
                    "location": true,
                    "work_setup": true,
                    "employment_type": true,
                    "salary": true
                }
            }
        ],
        "total_count": 42,
        "page": 1,
        "page_size": 20,
        "has_more": true
    }
    ```
    """
    logger.info(
        "get_job_matches_request",
        candidate_id=str(current_user.id),
        page=page,
        page_size=page_size
    )

    try:
        result = await matching_service.get_job_matches(
            candidate=current_user,
            page=page,
            page_size=page_size
        )

        logger.info(
            "get_job_matches_success",
            candidate_id=str(current_user.id),
            match_count=len(result.matches),
            total_count=result.total_count
        )

        return result

    except Exception as e:
        logger.error(
            "get_job_matches_error",
            candidate_id=str(current_user.id),
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/jobs/{job_id}/explanation", response_model=MatchExplanationResponse)
async def get_match_explanation(
    job_id: UUID,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    explanation_service: Annotated[ExplanationService, Depends(get_explanation_service)],
    matching_service: Annotated[MatchingService, Depends(get_matching_service)]
) -> MatchExplanationResponse:
    """
    Get AI-generated explanation for job match.
    
    Returns detailed reasoning about why a specific job matches the candidate's
    profile, including matching factors, missing requirements, and overall assessment.
    Uses GPT-4o-mini for cost-efficient explanation generation.
    
    **Match Score Requirement:**
    - Explanations only available for matches with score ≥40% (Fair or better)
    - Poor matches (<40%) will return 400 error
    
    **Caching:**
    - Explanations are cached for 24 hours
    - Cache invalidated when candidate profile or job posting is updated
    - Second requests for same match return cached result (<100ms)
    
    **Authentication Required:** Bearer token (JWT)
    
    **Returns:**
    - 200 OK: AI-generated explanation with matching factors and reasoning
    - 400 Bad Request: Match score too low (<40%) or no match exists
    - 401 Unauthorized: Invalid or missing authentication token
    - 404 Not Found: Job not found
    - 500 Internal Server Error: Explanation generation failed
    
    **Path Parameters:**
    - job_id: UUID of job posting to explain match for
    
    **Example Request:**
    ```
    GET /api/v1/matching/jobs/123e4567-e89b-12d3-a456-426614174000/explanation
    Authorization: Bearer <jwt_token>
    ```
    
    **Example Response:**
    ```json
    {
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
    ```
    """
    logger.info(
        "get_match_explanation_request",
        candidate_id=str(current_user.id),
        job_id=str(job_id)
    )

    try:
        # First, verify match exists and get match data
        matches_response = await matching_service.get_job_matches(
            candidate=current_user,
            page=1,
            page_size=100  # Large page size to ensure we find the job
        )
        
        # Find the specific job match
        job_match = next(
            (m for m in matches_response.matches if m.id == job_id),
            None
        )
        
        if not job_match:
            logger.warning(
                "match_not_found_for_explanation",
                candidate_id=str(current_user.id),
                job_id=str(job_id)
            )
            raise HTTPException(
                status_code=404,
                detail="No match found for this job. The job may not be active or may not meet your preferences."
            )
        
        # Extract preference matches as dict
        preference_matches = {}
        if job_match.preference_matches:
            preference_matches = {
                "location": job_match.preference_matches.location,
                "work_setup": job_match.preference_matches.work_setup,
                "employment_type": job_match.preference_matches.employment_type,
                "salary": job_match.preference_matches.salary
            }
        
        # Generate explanation
        explanation = await explanation_service.generate_explanation(
            candidate_id=current_user.id,
            job_id=job_id,
            match_score=job_match.match_score,
            match_classification=job_match.match_classification,
            preference_matches=preference_matches
        )
        
        logger.info(
            "match_explanation_success",
            candidate_id=str(current_user.id),
            job_id=str(job_id),
            confidence=explanation["confidence_score"]
        )
        
        return MatchExplanationResponse(**explanation)
    
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        logger.error(
            "match_explanation_endpoint_failed",
            candidate_id=str(current_user.id),
            job_id=str(job_id),
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate match explanation"
        ) from e
