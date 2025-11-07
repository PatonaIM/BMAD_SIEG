"""Profile management service for candidate profile operations."""
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

import structlog
from fastapi import HTTPException, status

from app.models.candidate import Candidate
from app.repositories.candidate import CandidateRepository

if TYPE_CHECKING:
    from app.services.embedding_service import EmbeddingService
    from app.services.explanation_cache import ExplanationCache


class ProfileService:
    """
    Service for profile management operations.

    Handles profile retrieval, updates to skills/experience/preferences,
    and profile completeness score calculation.
    """

    def __init__(
        self,
        candidate_repo: CandidateRepository,
        embedding_service: "EmbeddingService | None" = None,
        explanation_cache: "ExplanationCache | None" = None
    ):
        """
        Initialize profile service with repository.

        Args:
            candidate_repo: Candidate repository instance
            embedding_service: Optional embedding service for auto-regeneration
            explanation_cache: Optional explanation cache for invalidation on updates
        """
        self.candidate_repo = candidate_repo
        self.embedding_service = embedding_service
        self.explanation_cache = explanation_cache
        self.logger = structlog.get_logger().bind(service="profile_service")

    async def get_profile(self, candidate_id: UUID) -> Candidate:
        """
        Get candidate profile by ID.

        Args:
            candidate_id: UUID of the candidate

        Returns:
            Candidate instance with all profile data

        Raises:
            HTTPException: If candidate not found (404)
        """
        candidate = await self.candidate_repo.get_by_id(candidate_id)

        if candidate is None:
            self.logger.warning(
                "profile_not_found",
                candidate_id=str(candidate_id)
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        self.logger.info(
            "profile_retrieved",
            candidate_id=str(candidate_id),
            completeness_score=str(candidate.profile_completeness_score) if candidate.profile_completeness_score else None
        )

        return candidate

    async def update_skills(self, candidate_id: UUID, skills: list[str]) -> Candidate:
        """
        Update candidate skills with normalization.

        Skills are normalized to lowercase, deduplicated, and sorted
        before storing to ensure consistent matching.

        Args:
            candidate_id: UUID of the candidate
            skills: List of skill strings (will be normalized)

        Returns:
            Updated candidate with new skills and completeness score

        Raises:
            HTTPException: If candidate not found (404)
        """
        candidate = await self.get_profile(candidate_id)

        old_score = candidate.profile_completeness_score

        # Normalize skills
        normalized_skills = self._normalize_skills(skills)

        # Update candidate
        candidate.skills = normalized_skills
        candidate.profile_completeness_score = self.calculate_completeness(candidate)

        # Commit changes
        await self.candidate_repo.update(candidate)

        self.logger.info(
            "profile_updated",
            candidate_id=str(candidate_id),
            field="skills",
            skill_count=len(normalized_skills),
            old_completeness=str(old_score) if old_score else None,
            new_completeness=str(candidate.profile_completeness_score)
        )

        # Regenerate embedding (async, don't block on failure)
        if self.embedding_service:
            try:
                await self.embedding_service.generate_candidate_embedding(candidate_id)
                self.logger.info(
                    "profile_embedding_regenerated",
                    candidate_id=str(candidate_id),
                    trigger="skills_update"
                )
            except Exception as e:
                # Log but don't fail the profile update
                self.logger.error(
                    "embedding_regeneration_failed",
                    candidate_id=str(candidate_id),
                    error=str(e)
                )

        # Invalidate explanation cache for this candidate
        # Skills update affects match explanations, so clear cached explanations
        if self.explanation_cache:
            try:
                invalidated_count = await self.explanation_cache.invalidate(
                    candidate_id=candidate_id
                )
                if invalidated_count > 0:
                    self.logger.info(
                        "explanation_cache_invalidated",
                        candidate_id=str(candidate_id),
                        trigger="skills_update",
                        invalidated_count=invalidated_count
                    )
            except Exception as e:
                # Log but don't fail the profile update
                self.logger.error(
                    "cache_invalidation_failed",
                    candidate_id=str(candidate_id),
                    error=str(e)
                )

        return candidate

    async def update_experience(self, candidate_id: UUID, years: int) -> Candidate:
        """
        Update candidate experience years.

        Args:
            candidate_id: UUID of the candidate
            years: Years of professional experience (0-50)

        Returns:
            Updated candidate with new experience and completeness score

        Raises:
            HTTPException: If candidate not found (404)
        """
        candidate = await self.get_profile(candidate_id)

        old_score = candidate.profile_completeness_score

        # Update experience
        candidate.experience_years = years
        candidate.profile_completeness_score = self.calculate_completeness(candidate)

        # Commit changes
        await self.candidate_repo.update(candidate)

        self.logger.info(
            "profile_updated",
            candidate_id=str(candidate_id),
            field="experience_years",
            experience_years=years,
            old_completeness=str(old_score) if old_score else None,
            new_completeness=str(candidate.profile_completeness_score)
        )

        # Regenerate embedding (async, don't block on failure)
        if self.embedding_service:
            try:
                await self.embedding_service.generate_candidate_embedding(candidate_id)
                self.logger.info(
                    "profile_embedding_regenerated",
                    candidate_id=str(candidate_id),
                    trigger="experience_update"
                )
            except Exception as e:
                # Log but don't fail the profile update
                self.logger.error(
                    "embedding_regeneration_failed",
                    candidate_id=str(candidate_id),
                    error=str(e)
                )

        # Invalidate explanation cache for this candidate
        # Experience update affects match explanations, so clear cached explanations
        if self.explanation_cache:
            try:
                invalidated_count = await self.explanation_cache.invalidate(
                    candidate_id=candidate_id
                )
                if invalidated_count > 0:
                    self.logger.info(
                        "explanation_cache_invalidated",
                        candidate_id=str(candidate_id),
                        trigger="experience_update",
                        invalidated_count=invalidated_count
                    )
            except Exception as e:
                # Log but don't fail the profile update
                self.logger.error(
                    "cache_invalidation_failed",
                    candidate_id=str(candidate_id),
                    error=str(e)
                )

        return candidate

    async def update_preferences(self, candidate_id: UUID, preferences: dict) -> Candidate:
        """
        Update candidate job preferences.

        Args:
            candidate_id: UUID of the candidate
            preferences: Job preferences object (JSONB)

        Returns:
            Updated candidate with new preferences and completeness score

        Raises:
            HTTPException: If candidate not found (404)
        """
        candidate = await self.get_profile(candidate_id)

        old_score = candidate.profile_completeness_score

        # Update preferences
        candidate.job_preferences = preferences
        candidate.profile_completeness_score = self.calculate_completeness(candidate)

        # Commit changes
        await self.candidate_repo.update(candidate)

        self.logger.info(
            "profile_updated",
            candidate_id=str(candidate_id),
            field="job_preferences",
            old_completeness=str(old_score) if old_score else None,
            new_completeness=str(candidate.profile_completeness_score)
        )

        # Regenerate embedding (async, don't block on failure)
        if self.embedding_service:
            try:
                await self.embedding_service.generate_candidate_embedding(candidate_id)
                self.logger.info(
                    "profile_embedding_regenerated",
                    candidate_id=str(candidate_id),
                    trigger="preferences_update"
                )
            except Exception as e:
                # Log but don't fail the profile update
                self.logger.error(
                    "embedding_regeneration_failed",
                    candidate_id=str(candidate_id),
                    error=str(e)
                )

        # Invalidate explanation cache for this candidate
        # Preferences update affects match explanations, so clear cached explanations
        if self.explanation_cache:
            try:
                invalidated_count = await self.explanation_cache.invalidate(
                    candidate_id=candidate_id
                )
                if invalidated_count > 0:
                    self.logger.info(
                        "explanation_cache_invalidated",
                        candidate_id=str(candidate_id),
                        trigger="preferences_update",
                        invalidated_count=invalidated_count
                    )
            except Exception as e:
                # Log but don't fail the profile update
                self.logger.error(
                    "cache_invalidation_failed",
                    candidate_id=str(candidate_id),
                    error=str(e)
                )

        return candidate

    def calculate_completeness(self, candidate: Candidate) -> Decimal:
        """
        Calculate profile completeness score (0-100%).

        Scoring breakdown:
        - Email: 10% (always present for registered users)
        - Full name: 10% (always present for registered users)
        - Phone: 10% (optional field)
        - Skills: 20% (0% if empty, 10% if 1-3 skills, 20% if 4+ skills)
        - Experience years: 15% (0% if null, 15% if set)
        - Job preferences: 20% (incremental based on fields set)
          - Locations: 5%
          - Employment types: 5%
          - Work setups: 5%
          - Salary range: 5%
        - Resume uploaded: 15% (check if resumes relationship has records)

        Args:
            candidate: Candidate model instance

        Returns:
            Decimal percentage 0.00-100.00
        """
        score = Decimal("0.00")

        # Base fields (always present for registered users)
        if candidate.email:
            score += Decimal("10.00")
        if candidate.full_name:
            score += Decimal("10.00")

        # Optional phone
        if candidate.phone:
            score += Decimal("10.00")

        # Skills scoring (graduated based on count)
        if candidate.skills:
            skill_count = len(candidate.skills)
            if skill_count >= 4:
                score += Decimal("20.00")
            elif skill_count >= 1:
                score += Decimal("10.00")

        # Experience years
        if candidate.experience_years is not None:
            score += Decimal("15.00")

        # Job preferences (JSONB object)
        if candidate.job_preferences:
            prefs = candidate.job_preferences
            if prefs.get("locations"):
                score += Decimal("5.00")
            if prefs.get("employment_types"):
                score += Decimal("5.00")
            if prefs.get("work_setups"):
                score += Decimal("5.00")
            if prefs.get("salary_min") and prefs.get("salary_max"):
                score += Decimal("5.00")

        # Resume uploaded (check relationship)
        if candidate.resumes and len(candidate.resumes) > 0:
            score += Decimal("15.00")

        return score

    def _normalize_skills(self, skills: list[str]) -> list[str]:
        """
        Normalize skills array: lowercase, trim, deduplicate, sort.

        Example:
            Input: ["React", "  TypeScript ", "react", "Node.js"]
            Output: ["node.js", "react", "typescript"]

        Args:
            skills: List of skill strings

        Returns:
            Normalized list of unique skills, sorted alphabetically
        """
        normalized = set()
        for skill in skills:
            cleaned = skill.strip().lower()
            if cleaned:  # Skip empty strings
                normalized.add(cleaned)

        return sorted(normalized)
