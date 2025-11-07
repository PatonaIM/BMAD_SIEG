"""Resume parsing service using OpenAI GPT-4o-mini."""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

import structlog
from pydantic import ValidationError

from app.core.exceptions import OpenAIProviderError
from app.providers.openai_provider import OpenAIProvider
from app.repositories.candidate import CandidateRepository
from app.repositories.resume import ResumeRepository
from app.schemas.resume import ResumeParsedDataSchema

logger = structlog.get_logger(__name__)


class ResumeParsingService:
    """Service for parsing resume text using GPT-4o-mini."""

    def __init__(
        self,
        openai_provider: OpenAIProvider,
        resume_repo: ResumeRepository,
        candidate_repo: CandidateRepository,
    ):
        """
        Initialize resume parsing service.

        Args:
            openai_provider: OpenAI provider for GPT-4o-mini calls
            resume_repo: Resume repository for database operations
            candidate_repo: Candidate repository for profile updates
        """
        self.openai_provider = openai_provider
        self.resume_repo = resume_repo
        self.candidate_repo = candidate_repo
        self._load_prompt_template()

    def _load_prompt_template(self) -> None:
        """Load resume parsing prompt template from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "resume_parsing.txt"
        with open(prompt_path) as f:
            self.prompt_template = f.read()

        logger.info("resume_parsing_prompt_loaded", prompt_path=str(prompt_path))

    async def parse_resume_text(
        self, resume_id: UUID, resume_text: str
    ) -> ResumeParsedDataSchema:
        """
        Parse resume text using GPT-4o-mini with retry logic.

        Implements:
        - 3 retry attempts with exponential backoff (1s, 2s, 4s)
        - 30-second timeout per attempt
        - Auto-population of candidate skills and experience_years
        - Structured error logging

        Args:
            resume_id: UUID of the resume to parse
            resume_text: Plain text content of the resume

        Returns:
            Parsed resume data schema

        Raises:
            ValueError: If resume not found or text is empty
            OpenAIProviderError: If parsing fails after all retries
        """
        # Validate inputs
        if not resume_text or not resume_text.strip():
            logger.error("empty_resume_text", resume_id=str(resume_id))
            await self.resume_repo.update_parsing_status(
                resume_id=resume_id,
                status="failed",
                parsed_at=None,
                parsed_data={"error": "No text content to parse"},
            )
            raise ValueError("No text content to parse")

        # Get resume to fetch candidate_id
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        # Set status to processing
        await self.resume_repo.update_parsing_status(
            resume_id=resume_id,
            status="processing",
            parsed_at=None,
            parsed_data=None,
        )

        logger.info(
            "resume_parsing_started",
            resume_id=str(resume_id),
            candidate_id=str(resume.candidate_id),
            text_length=len(resume_text),
        )

        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            try:
                attempt += 1

                # Prepare prompt with resume text
                prompt = self.prompt_template.format(resume_text=resume_text)

                # Call OpenAI with GPT-4o-mini
                response = await asyncio.wait_for(
                    self.openai_provider.generate_completion(
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2000,
                        temperature=0.3,  # Lower for deterministic parsing
                    ),
                    timeout=30.0,  # 30-second timeout per attempt
                )

                # Parse JSON response
                parsed_json = self._extract_json_from_response(response)
                parsed_data = ResumeParsedDataSchema(**parsed_json)

                # Update resume with parsed data
                await self.resume_repo.update_parsing_status(
                    resume_id=resume_id,
                    status="completed",
                    parsed_at=datetime.utcnow(),
                    parsed_data=parsed_data.model_dump(),
                )

                # Auto-populate candidate profile
                await self._auto_populate_candidate_profile(
                    candidate_id=resume.candidate_id, parsed_data=parsed_data
                )

                logger.info(
                    "resume_parsing_completed",
                    resume_id=str(resume_id),
                    candidate_id=str(resume.candidate_id),
                    skills_count=len(parsed_data.skills),
                    experience_years=parsed_data.experience_years,
                    attempt=attempt,
                )

                return parsed_data

            except TimeoutError as e:
                logger.warning(
                    "resume_parsing_timeout",
                    resume_id=str(resume_id),
                    attempt=attempt,
                    max_retries=max_retries,
                )

                if attempt >= max_retries:
                    error_msg = f"Parsing timeout after {max_retries} attempts"
                    await self.resume_repo.update_parsing_status(
                        resume_id=resume_id,
                        status="failed",
                        parsed_at=None,
                        parsed_data={"error": error_msg},
                    )
                    logger.error(
                        "resume_parsing_failed_timeout",
                        resume_id=str(resume_id),
                        max_retries=max_retries,
                    )
                    raise OpenAIProviderError(error_msg) from e

                # Exponential backoff
                delay = 2 ** (attempt - 1)
                await asyncio.sleep(delay)

            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(
                    "resume_parsing_invalid_response",
                    resume_id=str(resume_id),
                    attempt=attempt,
                    error=str(e),
                )

                if attempt >= max_retries:
                    error_msg = f"Invalid JSON response after {max_retries} attempts"
                    await self.resume_repo.update_parsing_status(
                        resume_id=resume_id,
                        status="failed",
                        parsed_at=None,
                        parsed_data={"error": error_msg},
                    )
                    logger.error(
                        "resume_parsing_failed_invalid_json",
                        resume_id=str(resume_id),
                        max_retries=max_retries,
                    )
                    raise OpenAIProviderError(error_msg) from e

                # Retry with exponential backoff
                delay = 2 ** (attempt - 1)
                await asyncio.sleep(delay)

            except OpenAIProviderError as e:
                logger.error(
                    "resume_parsing_openai_error",
                    resume_id=str(resume_id),
                    attempt=attempt,
                    error=str(e),
                )

                if attempt >= max_retries:
                    await self.resume_repo.update_parsing_status(
                        resume_id=resume_id,
                        status="failed",
                        parsed_at=None,
                        parsed_data={"error": str(e)},
                    )
                    logger.error(
                        "resume_parsing_failed_openai",
                        resume_id=str(resume_id),
                        max_retries=max_retries,
                    )
                    raise

                # Exponential backoff
                delay = 2 ** (attempt - 1)
                await asyncio.sleep(delay)

            except Exception as e:
                # Unexpected error - don't retry
                error_msg = f"Unexpected error during parsing: {str(e)}"
                await self.resume_repo.update_parsing_status(
                    resume_id=resume_id,
                    status="failed",
                    parsed_at=None,
                    parsed_data={"error": error_msg},
                )
                logger.error(
                    "resume_parsing_unexpected_error",
                    resume_id=str(resume_id),
                    error=str(e),
                )
                raise OpenAIProviderError(error_msg) from e

        # Should not reach here, but just in case
        raise OpenAIProviderError("Parsing failed after all retries")

    def _extract_json_from_response(self, response: str) -> dict:
        """
        Extract JSON from OpenAI response, handling various formats.

        Args:
            response: Raw response from OpenAI

        Returns:
            Parsed JSON dictionary

        Raises:
            json.JSONDecodeError: If no valid JSON found
        """
        # Try to parse directly
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to find JSON block in markdown code fence
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)

        # Try to find JSON object by looking for { and }
        if "{" in response and "}" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end].strip()
            return json.loads(json_str)

        # If all else fails, raise error
        raise json.JSONDecodeError("No valid JSON found in response", response, 0)

    async def _auto_populate_candidate_profile(
        self, candidate_id: UUID, parsed_data: ResumeParsedDataSchema
    ) -> None:
        """
        Auto-populate candidate profile with parsed resume data.

        Updates:
        - Merges skills into candidates.skills (deduplicated)
        - Sets candidates.experience_years (only if currently null)

        Args:
            candidate_id: UUID of the candidate
            parsed_data: Parsed resume data
        """
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            logger.warning(
                "candidate_not_found_for_profile_update", candidate_id=str(candidate_id)
            )
            return

        # Merge skills (deduplicate)
        existing_skills = candidate.skills or []
        if isinstance(existing_skills, list):
            merged_skills = list(set(existing_skills + parsed_data.skills))
        else:
            merged_skills = parsed_data.skills

        candidate.skills = merged_skills

        # Set experience_years only if currently null
        if candidate.experience_years is None and parsed_data.experience_years > 0:
            candidate.experience_years = parsed_data.experience_years

        await self.candidate_repo.db.commit()
        await self.candidate_repo.db.refresh(candidate)

        logger.info(
            "candidate_profile_auto_populated",
            candidate_id=str(candidate_id),
            skills_count=len(merged_skills),
            experience_years=candidate.experience_years,
        )
