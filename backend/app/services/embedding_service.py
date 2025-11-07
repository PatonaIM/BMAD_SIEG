"""OpenAI embedding generation service for semantic matching."""

import asyncio
import random
from uuid import UUID

import structlog
from openai import (
    APIError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)

from app.core.config import settings
from app.core.exceptions import OpenAIProviderError, RateLimitExceededError
from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.repositories.candidate import CandidateRepository
from app.repositories.job_posting_repository import JobPostingRepository


def build_candidate_embedding_text(candidate: Candidate) -> str:
    """
    Build structured text for candidate embedding.

    Format:
        Skills: [skill1, skill2, skill3]
        Experience: X years
        Preferences: Locations [loc1, loc2], Employment [types], Work Setup [setups],
                     Salary Range [min-max], Role Categories [cats]

    Example:
        Skills: python, react, typescript, aws
        Experience: 5 years
        Preferences: Locations Remote Australia, Sydney NSW, Employment permanent,
                     Work Setup remote hybrid, Salary Range 120000-150000 AUD,
                     Role Categories engineering quality_assurance

    Args:
        candidate: Candidate model instance

    Returns:
        Structured text string for embedding generation
    """
    parts = []

    # Skills (most important for matching)
    if candidate.skills:
        parts.append(f"Skills: {', '.join(candidate.skills)}")

    # Experience level
    if candidate.experience_years is not None:
        parts.append(f"Experience: {candidate.experience_years} years")

    # Job preferences
    if candidate.job_preferences:
        prefs = candidate.job_preferences
        pref_parts = []

        if prefs.get("locations"):
            pref_parts.append(f"Locations {' '.join(prefs['locations'])}")
        if prefs.get("employment_types"):
            pref_parts.append(f"Employment {' '.join(prefs['employment_types'])}")
        if prefs.get("work_setups"):
            pref_parts.append(f"Work Setup {' '.join(prefs['work_setups'])}")
        if prefs.get("salary_min") and prefs.get("salary_max"):
            pref_parts.append(
                f"Salary Range {prefs['salary_min']}-{prefs['salary_max']} AUD"
            )
        if prefs.get("role_categories"):
            pref_parts.append(f"Role Categories {' '.join(prefs['role_categories'])}")

        if pref_parts:
            parts.append(f"Preferences: {', '.join(pref_parts)}")

    return "\n".join(parts)


def build_job_embedding_text(job: JobPosting) -> str:
    """
    Build structured text for job posting embedding.

    Format:
        Title: [job title]
        Company: [company name]
        Description: [truncated to 500 chars]
        Required Skills: [skill1, skill2, skill3]
        Experience Level: [level]
        Employment: [type], Work Setup: [setup], Location: [location]

    Example:
        Title: Senior React Developer
        Company: TechCorp
        Description: We are seeking an experienced React developer...
        Required Skills: react, typescript, redux, graphql
        Experience Level: Senior
        Employment: permanent, Work Setup: remote, Location: Remote Australia

    Args:
        job: JobPosting model instance

    Returns:
        Structured text string for embedding generation
    """
    parts = []

    # Job title and company
    parts.append(f"Title: {job.title}")
    parts.append(f"Company: {job.company}")

    # Description (truncated to avoid token bloat)
    if job.description:
        desc = job.description[:500]
        if len(job.description) > 500:
            desc += "..."
        parts.append(f"Description: {desc}")

    # Required skills
    if job.required_skills:
        skills = ", ".join(job.required_skills)
        parts.append(f"Required Skills: {skills}")

    # Experience level
    parts.append(f"Experience Level: {job.experience_level}")

    # Job details
    parts.append(
        f"Employment: {job.employment_type}, "
        f"Work Setup: {job.work_setup}, "
        f"Location: {job.location}"
    )

    return "\n".join(parts)


class EmbeddingService:
    """OpenAI embedding generation for semantic matching."""

    def __init__(
        self,
        candidate_repo: CandidateRepository,
        job_repo: JobPostingRepository
    ):
        """
        Initialize embedding service with dependencies.

        Args:
            candidate_repo: Candidate repository instance
            job_repo: JobPosting repository instance
        """
        self.candidate_repo = candidate_repo
        self.job_repo = job_repo
        self.client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
        self.model = "text-embedding-3-large"
        self.dimensions = 3072
        self.logger = structlog.get_logger().bind(service="embedding_service")

        self.logger.info(
            "embedding_service_initialized",
            model=self.model,
            dimensions=self.dimensions
        )

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for text using OpenAI API.

        Implements exponential backoff retry logic for:
        - Rate limit errors (429)
        - Server errors (500)
        - Timeout errors

        Args:
            text: Input text to embed (candidate profile or job description)

        Returns:
            list[float]: 3072-dimensional embedding vector

        Raises:
            OpenAIProviderError: For unrecoverable errors
            RateLimitExceededError: After all retry attempts exhausted
        """
        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=text,
                    dimensions=self.dimensions
                )

                embedding = response.data[0].embedding
                tokens_used = response.usage.total_tokens

                self.logger.info(
                    "embedding_generated",
                    model=self.model,
                    tokens=tokens_used,
                    text_length=len(text)
                )

                return embedding

            except RateLimitError as e:
                attempt += 1
                if attempt >= max_retries:
                    self.logger.error("embedding_rate_limit_exceeded", max_retries=max_retries)
                    raise RateLimitExceededError(f"Rate limit after {max_retries} attempts") from e

                delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                self.logger.warning("embedding_rate_limit_retry", attempt=attempt, delay=delay)
                await asyncio.sleep(delay)

            except APITimeoutError as e:
                self.logger.error("embedding_timeout", error=str(e))
                raise OpenAIProviderError("Embedding generation timed out") from e

            except AuthenticationError as e:
                self.logger.critical("openai_auth_failed", error=str(e))
                raise

            except APIError as e:
                attempt += 1
                if attempt >= max_retries:
                    self.logger.error("embedding_api_error", error=str(e))
                    raise OpenAIProviderError(f"API error after {max_retries} attempts") from e

                self.logger.warning("embedding_api_retry", attempt=attempt)
                await asyncio.sleep(2)

        # Fallback (should not reach here)
        raise OpenAIProviderError("Max retries exhausted")

    async def batch_generate_embeddings(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts in batch (max 100).

        Args:
            texts: List of texts to embed (max 100)

        Returns:
            list[list[float]]: List of embedding vectors

        Raises:
            ValueError: If batch size exceeds 100
            OpenAIProviderError: For unrecoverable API errors
            RateLimitExceededError: After all retry attempts exhausted
        """
        if len(texts) > 100:
            raise ValueError("Batch size must be <= 100")

        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                    dimensions=self.dimensions
                )

                embeddings = [item.embedding for item in response.data]
                tokens_used = response.usage.total_tokens

                self.logger.info(
                    "batch_embeddings_generated",
                    count=len(texts),
                    tokens=tokens_used
                )

                return embeddings

            except RateLimitError as e:
                attempt += 1
                if attempt >= max_retries:
                    raise RateLimitExceededError(f"Rate limit after {max_retries} attempts") from e

                delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                self.logger.warning("batch_embedding_rate_limit_retry", attempt=attempt, delay=delay)
                await asyncio.sleep(delay)

            except APITimeoutError as e:
                self.logger.error("batch_embedding_timeout", error=str(e))
                raise OpenAIProviderError("Batch embedding generation timed out") from e

            except AuthenticationError as e:
                self.logger.critical("openai_auth_failed", error=str(e))
                raise

            except APIError as e:
                attempt += 1
                if attempt >= max_retries:
                    self.logger.error("batch_embedding_api_error", error=str(e))
                    raise OpenAIProviderError(f"API error after {max_retries} attempts") from e

                self.logger.warning("batch_embedding_api_retry", attempt=attempt)
                await asyncio.sleep(2)

        # Fallback (should not reach here)
        raise OpenAIProviderError("Max retries exhausted")

    async def generate_candidate_embedding(self, candidate_id: UUID) -> list[float]:
        """
        Generate and store embedding for candidate profile.

        Args:
            candidate_id: UUID of the candidate

        Returns:
            list[float]: Generated embedding vector

        Raises:
            HTTPException: If candidate not found (404)
            OpenAIProviderError: For API errors
        """
        from fastapi import HTTPException

        # Fetch candidate
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Build embedding text
        text = build_candidate_embedding_text(candidate)

        # Generate embedding
        embedding = await self.generate_embedding(text)

        # Store in database
        await self.candidate_repo.update_embedding(candidate_id, embedding)

        self.logger.info(
            "candidate_embedding_stored",
            candidate_id=str(candidate_id),
            text_preview=text[:100]
        )

        return embedding

    async def generate_job_embedding(self, job_id: UUID) -> list[float]:
        """
        Generate and store embedding for job posting.

        Args:
            job_id: UUID of the job posting

        Returns:
            list[float]: Generated embedding vector

        Raises:
            HTTPException: If job posting not found (404)
            OpenAIProviderError: For API errors
        """
        from fastapi import HTTPException

        # Fetch job posting
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found")

        # Build embedding text
        text = build_job_embedding_text(job)

        # Generate embedding
        embedding = await self.generate_embedding(text)

        # Store in database
        await self.job_repo.update_embedding(job_id, embedding)

        self.logger.info(
            "job_embedding_stored",
            job_id=str(job_id),
            text_preview=text[:100]
        )

        return embedding

    async def batch_generate_candidate_embeddings(
        self,
        force: bool = False,
        limit: int = 100
    ) -> dict:
        """
        Batch generate embeddings for candidates.

        Only processes candidates with profile_completeness_score >= 40%
        to ensure sufficient data for meaningful matching.

        Args:
            force: If true, regenerate even if embedding exists
            limit: Max number of records to process (default 100, max 1000)

        Returns:
            dict: Statistics with keys: total_processed, successful, failed, skipped, errors
        """
        # Get candidates for embedding
        candidates = await self.candidate_repo.get_candidates_for_embedding(
            skip_with_embedding=not force,
            limit=limit
        )

        stats = {
            "total_processed": len(candidates),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }

        if not candidates:
            self.logger.info("batch_candidate_embeddings_no_candidates")
            return stats

        # Process in chunks of 100 (API limit)
        chunk_size = 100
        for i in range(0, len(candidates), chunk_size):
            chunk = candidates[i:i + chunk_size]

            try:
                # Build texts
                texts = [build_candidate_embedding_text(c) for c in chunk]

                # Generate embeddings
                embeddings = await self.batch_generate_embeddings(texts)

                # Store embeddings
                for candidate, embedding in zip(chunk, embeddings, strict=False):
                    try:
                        await self.candidate_repo.update_embedding(candidate.id, embedding)
                        stats["successful"] += 1
                    except Exception as e:
                        stats["failed"] += 1
                        error_msg = f"Failed to store embedding for candidate {candidate.id}: {str(e)}"
                        stats["errors"].append(error_msg)
                        self.logger.error("candidate_embedding_storage_failed", candidate_id=str(candidate.id), error=str(e))

            except Exception as e:
                stats["failed"] += len(chunk)
                error_msg = f"Batch generation failed for chunk: {str(e)}"
                stats["errors"].append(error_msg)
                self.logger.error("batch_candidate_embeddings_failed", chunk_size=len(chunk), error=str(e))

        self.logger.info(
            "batch_candidate_embeddings_completed",
            **stats
        )

        return stats

    async def batch_generate_job_embeddings(
        self,
        force: bool = False,
        limit: int = 100
    ) -> dict:
        """
        Batch generate embeddings for job postings.

        Only processes active job postings (status='active').

        Args:
            force: If true, regenerate even if embedding exists
            limit: Max number of records to process (default 100, max 1000)

        Returns:
            dict: Statistics with keys: total_processed, successful, failed, skipped, errors
        """
        # Get jobs for embedding
        jobs = await self.job_repo.get_jobs_for_embedding(
            skip_with_embedding=not force,
            limit=limit
        )

        stats = {
            "total_processed": len(jobs),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }

        if not jobs:
            self.logger.info("batch_job_embeddings_no_jobs")
            return stats

        # Process in chunks of 100 (API limit)
        chunk_size = 100
        for i in range(0, len(jobs), chunk_size):
            chunk = jobs[i:i + chunk_size]

            try:
                # Build texts
                texts = [build_job_embedding_text(j) for j in chunk]

                # Generate embeddings
                embeddings = await self.batch_generate_embeddings(texts)

                # Store embeddings
                for job, embedding in zip(chunk, embeddings, strict=False):
                    try:
                        await self.job_repo.update_embedding(job.id, embedding)
                        stats["successful"] += 1
                    except Exception as e:
                        stats["failed"] += 1
                        error_msg = f"Failed to store embedding for job {job.id}: {str(e)}"
                        stats["errors"].append(error_msg)
                        self.logger.error("job_embedding_storage_failed", job_id=str(job.id), error=str(e))

            except Exception as e:
                stats["failed"] += len(chunk)
                error_msg = f"Batch generation failed for chunk: {str(e)}"
                stats["errors"].append(error_msg)
                self.logger.error("batch_job_embeddings_failed", chunk_size=len(chunk), error=str(e))

        self.logger.info(
            "batch_job_embeddings_completed",
            **stats
        )

        return stats
