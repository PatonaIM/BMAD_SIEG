"""Resume analysis service for AI-powered evaluation."""
import json
from datetime import datetime
from uuid import UUID

import structlog

from app.models.resume_analysis import ResumeAnalysis
from app.providers.openai_provider import OpenAIProvider
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.utils.prompt_loader import PromptTemplateManager

logger = structlog.get_logger(__name__)


class ResumeAnalysisService:
    """Service for analyzing resumes with AI and storing results."""

    def __init__(
        self,
        openai_provider: OpenAIProvider,
        analysis_repo: ResumeAnalysisRepository,
        prompt_manager: PromptTemplateManager,
    ):
        """
        Initialize resume analysis service.

        Args:
            openai_provider: OpenAI provider for GPT-4o-mini
            analysis_repo: Repository for storing analysis results
            prompt_manager: Manager for loading prompt templates
        """
        self.openai_provider = openai_provider
        self.analysis_repo = analysis_repo
        self.prompt_manager = prompt_manager

    async def analyze_resume(
        self, resume_id: UUID, resume_text: str, max_retries: int = 3
    ) -> ResumeAnalysis:
        """
        Analyze resume text with GPT-4o-mini and store results.

        Args:
            resume_id: UUID of the resume being analyzed
            resume_text: Extracted text from resume PDF
            max_retries: Maximum number of retry attempts

        Returns:
            ResumeAnalysis instance with analysis results

        Raises:
            ValueError: If analysis response is invalid
            Exception: If analysis fails after retries
        """
        logger.info(
            "resume_analysis_started",
            resume_id=str(resume_id),
            text_length=len(resume_text),
        )

        # Load analysis prompt template
        prompt_template = self.prompt_manager.load_template("resume_analysis")
        prompt = prompt_template.replace("{resume_text}", resume_text)

        # Generate analysis with retry logic
        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(
                    "resume_analysis_attempt",
                    resume_id=str(resume_id),
                    attempt=attempt,
                )

                # Call GPT-4o-mini for analysis
                response = await self.openai_provider.generate_completion(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert resume reviewer. Always return valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=1500,
                    temperature=0.3,  # Lower temperature for consistent analysis
                )

                # Parse JSON response
                analysis_data = self._parse_analysis_response(response)

                # Create and save analysis record
                analysis = ResumeAnalysis(
                    resume_id=resume_id,
                    overall_score=analysis_data["overall_score"],
                    strengths=analysis_data["strengths"],
                    weaknesses=analysis_data["weaknesses"],
                    suggestions=analysis_data["suggestions"],
                    keywords_missing=analysis_data["keywords_missing"],
                    analysis_model=self.openai_provider.model,
                    tokens_used=self._estimate_tokens(prompt + response),
                    analyzed_at=datetime.utcnow(),
                )

                # Save to database
                saved_analysis = await self.analysis_repo.create(analysis)

                logger.info(
                    "resume_analysis_completed",
                    resume_id=str(resume_id),
                    analysis_id=str(saved_analysis.id),
                    overall_score=saved_analysis.overall_score,
                    tokens_used=saved_analysis.tokens_used,
                )

                return saved_analysis

            except json.JSONDecodeError as e:
                logger.warning(
                    "resume_analysis_json_parse_failed",
                    resume_id=str(resume_id),
                    attempt=attempt,
                    error=str(e),
                    response_preview=response[:200] if response else None,
                )
                if attempt == max_retries:
                    raise ValueError(f"Failed to parse analysis JSON after {max_retries} attempts")

            except Exception as e:
                logger.error(
                    "resume_analysis_failed",
                    resume_id=str(resume_id),
                    attempt=attempt,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                if attempt == max_retries:
                    raise

        raise Exception(f"Resume analysis failed after {max_retries} retries")

    def _parse_analysis_response(self, response: str) -> dict:
        """
        Parse and validate AI analysis response.

        Args:
            response: Raw AI response string

        Returns:
            Parsed analysis data dictionary

        Raises:
            ValueError: If response format is invalid
            json.JSONDecodeError: If JSON parsing fails
        """
        # Clean response (remove markdown code blocks if present)
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        # Parse JSON
        data = json.loads(cleaned_response)

        # Validate required fields
        required_fields = ["overall_score", "strengths", "weaknesses", "suggestions", "keywords_missing"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate score range
        score = data["overall_score"]
        if not isinstance(score, int) or score < 0 or score > 100:
            raise ValueError(f"Invalid overall_score: {score} (must be integer 0-100)")

        # Validate arrays
        for field in ["strengths", "weaknesses", "suggestions", "keywords_missing"]:
            if not isinstance(data[field], list):
                raise ValueError(f"Field {field} must be an array")

        logger.debug(
            "analysis_response_parsed",
            score=score,
            strengths_count=len(data["strengths"]),
            weaknesses_count=len(data["weaknesses"]),
        )

        return data

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses simple heuristic: ~4 chars per token.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        return len(text) // 4

    async def get_latest_analysis(self, resume_id: UUID) -> ResumeAnalysis | None:
        """
        Get the most recent analysis for a resume.

        Args:
            resume_id: UUID of the resume

        Returns:
            Latest ResumeAnalysis or None
        """
        return await self.analysis_repo.get_latest_by_resume_id(resume_id)

    async def get_all_analyses(self, resume_id: UUID) -> list[ResumeAnalysis]:
        """
        Get all historical analyses for a resume.

        Args:
            resume_id: UUID of the resume

        Returns:
            List of ResumeAnalysis instances
        """
        return await self.analysis_repo.get_all_by_resume_id(resume_id)
