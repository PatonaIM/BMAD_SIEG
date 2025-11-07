"""Matching service for AI-powered job recommendations."""
from decimal import Decimal
from typing import Any

import structlog
from fastapi import HTTPException, status

from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.repositories.matching_repository import MatchingRepository
from app.schemas.matching import (
    JobMatchListResponse,
    JobMatchResponse,
    PreferenceMatches,
)
from app.services.profile_service import ProfileService


class MatchingService:
    """
    Service for AI-powered job matching using semantic similarity.
    
    Combines vector embeddings with candidate preferences to recommend
    relevant job opportunities. Uses pgvector for fast similarity search.
    """

    # Profile completeness threshold
    MIN_COMPLETENESS_THRESHOLD = Decimal("40.00")

    def __init__(
        self,
        matching_repo: MatchingRepository,
        profile_service: ProfileService
    ):
        """
        Initialize matching service with dependencies.

        Args:
            matching_repo: Repository for vector similarity queries
            profile_service: Service for profile operations
        """
        self.matching_repo = matching_repo
        self.profile_service = profile_service
        self.logger = structlog.get_logger().bind(service="matching_service")

    def check_preference_matches(
        self,
        job: JobPosting,
        candidate_preferences: dict[str, Any] | None
    ) -> dict[str, bool]:
        """
        Check which candidate preferences the job matches.
        
        Compares job attributes against candidate preferences to determine
        compatibility. Returns boolean flags for each preference type.
        
        Args:
            job: JobPosting instance to evaluate
            candidate_preferences: Candidate's job_preferences JSONB field
        
        Returns:
            Dict with boolean flags for each matched preference type.
            Empty dict if candidate has no preferences.
        """
        if not candidate_preferences:
            return {}

        matches: dict[str, bool] = {}

        # Location match (includes remote jobs)
        if candidate_preferences.get("locations"):
            preferred_locs = candidate_preferences["locations"]
            matches["location"] = (
                job.location in preferred_locs
                or job.work_setup == "remote"
                or "Remote" in preferred_locs
            )

        # Work setup match
        if candidate_preferences.get("work_setups"):
            matches["work_setup"] = (
                job.work_setup in candidate_preferences["work_setups"]
            )

        # Employment type match
        if candidate_preferences.get("employment_types"):
            matches["employment_type"] = (
                job.employment_type in candidate_preferences["employment_types"]
            )

        # Salary range overlap
        if (candidate_preferences.get("salary_min") is not None
            and candidate_preferences.get("salary_max") is not None):
            candidate_min = candidate_preferences["salary_min"]
            candidate_max = candidate_preferences["salary_max"]

            if job.salary_min is not None and job.salary_max is not None:
                # Ranges overlap if max of one >= min of other
                matches["salary"] = (
                    float(job.salary_max) >= candidate_min
                    and float(job.salary_min) <= candidate_max
                )
            else:
                # Job has no salary info, consider it a non-match
                matches["salary"] = False

        return matches

    def calculate_match_score(
        self,
        similarity: float,
        preference_matches: dict[str, bool]
    ) -> Decimal:
        """
        Calculate overall match score combining similarity and preferences.
        
        Formula: score = (similarity * 0.7) + (preference_match_rate * 0.3) * 100
        
        - Semantic similarity weighted 70%
        - Preference matching weighted 30%
        - If no preferences, preference component = 1.0 (perfect)
        
        Args:
            similarity: Cosine similarity score 0-1
            preference_matches: Dict with boolean flags for each preference
        
        Returns:
            Match score 0-100 (Decimal with 2 decimal places)
        """
        # Semantic similarity component (70%)
        similarity_component = similarity * 0.7

        # Preference matching component (30%)
        if not preference_matches:
            # No preferences specified = perfect preference match
            preference_component = 1.0
        else:
            matches = sum(1 for matched in preference_matches.values() if matched)
            total_prefs = len(preference_matches)
            preference_component = (matches / total_prefs) if total_prefs > 0 else 1.0

        preference_weighted = preference_component * 0.3

        # Final score 0-100
        final_score = (similarity_component + preference_weighted) * 100

        return Decimal(str(round(final_score, 2)))

    def classify_match(self, score: Decimal) -> str:
        """
        Classify match quality based on score.
        
        Classification tiers:
        - Excellent: ≥85%
        - Great: 70-84%
        - Good: 55-69%
        - Fair: 40-54%
        - Poor: <40%
        
        Args:
            score: Match score 0-100
        
        Returns:
            Classification string: Excellent, Great, Good, Fair, or Poor
        """
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Great"
        elif score >= 55:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"

    async def get_job_matches(
        self,
        candidate: Candidate,
        page: int = 1,
        page_size: int = 20
    ) -> JobMatchListResponse:
        """
        Get AI-powered job recommendations for candidate.
        
        Retrieves jobs ranked by semantic similarity and preference matching.
        Requires candidate to have sufficient profile completeness (≥40%)
        and a profile embedding.
        
        Args:
            candidate: Authenticated candidate
            page: Page number (1-indexed)
            page_size: Results per page (max 100)
        
        Returns:
            JobMatchListResponse with ranked matches and pagination metadata
        
        Raises:
            HTTPException 403: Profile completeness below 40%
            HTTPException 400: No profile embedding available
        """
        self.logger.info(
            "get_job_matches_started",
            candidate_id=str(candidate.id),
            page=page,
            page_size=page_size
        )

        # Profile completeness gate
        if (candidate.profile_completeness_score is None
            or candidate.profile_completeness_score < self.MIN_COMPLETENESS_THRESHOLD):
            self.logger.warning(
                "profile_completeness_insufficient",
                candidate_id=str(candidate.id),
                completeness_score=str(candidate.profile_completeness_score) if candidate.profile_completeness_score else None
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Profile completeness must be at least {self.MIN_COMPLETENESS_THRESHOLD}% to access job matching. "
                       "Please complete your profile including skills, experience, and preferences."
            )

        # Embedding availability check
        if candidate.profile_embedding is None:
            self.logger.warning(
                "profile_embedding_missing",
                candidate_id=str(candidate.id)
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile embedding not available. Please update your profile to generate embeddings."
            )

        # Build preference filters for repository query
        filters: dict[str, Any] = {}

        if candidate.job_preferences:
            prefs = candidate.job_preferences

            if prefs.get("locations"):
                filters["preferred_locations"] = prefs["locations"]

            if prefs.get("work_setups"):
                filters["preferred_work_setups"] = prefs["work_setups"]

            if prefs.get("employment_types"):
                filters["preferred_employment_types"] = prefs["employment_types"]

            if prefs.get("salary_min") is not None and prefs.get("salary_max") is not None:
                filters["candidate_salary_min"] = prefs["salary_min"]
                filters["candidate_salary_max"] = prefs["salary_max"]

        # Calculate pagination
        offset = (page - 1) * page_size

        # Get vector matches from repository
        raw_matches = await self.matching_repo.get_vector_matches(
            candidate_embedding=candidate.profile_embedding,
            filters=filters,
            limit=page_size,
            offset=offset
        )

        # Get total count for pagination
        total_count = await self.matching_repo.count_matching_jobs(
            candidate_embedding=candidate.profile_embedding,
            filters=filters
        )

        self.logger.info(
            "vector_matches_retrieved",
            candidate_id=str(candidate.id),
            match_count=len(raw_matches),
            total_count=total_count
        )

        # Process matches: Calculate scores and build response objects
        match_responses: list[JobMatchResponse] = []

        for raw_match in raw_matches:
            job = raw_match["job"]
            similarity_score = raw_match["similarity_score"]

            # Check preference matches
            preference_matches_dict = self.check_preference_matches(
                job,
                candidate.job_preferences
            )

            # Calculate match score
            match_score = self.calculate_match_score(
                similarity_score,
                preference_matches_dict
            )

            # Classify match
            classification = self.classify_match(match_score)

            # Build preference matches schema (None if no preferences)
            pref_matches_schema = None
            if preference_matches_dict:
                pref_matches_schema = PreferenceMatches(**preference_matches_dict)

            # Build response object
            match_response = JobMatchResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                description=job.description,
                role_category=job.role_category,
                tech_stack=job.tech_stack,
                employment_type=job.employment_type,
                work_setup=job.work_setup,
                location=job.location,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                required_skills=job.required_skills,
                experience_level=job.experience_level,
                match_score=match_score,
                match_classification=classification,
                similarity_score=Decimal(str(round(similarity_score, 4))),
                preference_matches=pref_matches_schema
            )

            match_responses.append(match_response)

        # Sort by match_score descending (highest scores first)
        match_responses.sort(key=lambda m: m.match_score, reverse=True)

        # Build pagination metadata
        has_more = (offset + len(match_responses)) < total_count

        self.logger.info(
            "get_job_matches_completed",
            candidate_id=str(candidate.id),
            returned_matches=len(match_responses),
            total_count=total_count,
            has_more=has_more
        )

        return JobMatchListResponse(
            matches=match_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_more=has_more
        )
