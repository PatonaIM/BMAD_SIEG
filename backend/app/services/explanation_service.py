"""Service for generating AI explanations for job matches."""
import json
from decimal import Decimal
from uuid import UUID

import structlog
from fastapi import HTTPException

from app.models.candidate import Candidate
from app.models.job_posting import JobPosting
from app.providers.openai_provider import OpenAIProvider
from app.repositories.candidate import CandidateRepository
from app.repositories.job_posting_repository import JobPostingRepository
from app.services.explanation_cache import ExplanationCache

# Prompt template for explanation generation
EXPLANATION_PROMPT_TEMPLATE = """You are a career advisor analyzing why a job matches a candidate's profile.

**Candidate Profile:**
Skills: {candidate_skills}
Experience: {candidate_experience} years
Preferences:
- Locations: {preferred_locations}
- Employment Types: {preferred_employment_types}
- Work Setups: {preferred_work_setups}
- Salary Range: {salary_min}-{salary_max} {currency}
- Role Categories: {role_categories}

**Job Posting:**
Title: {job_title}
Company: {job_company}
Description: {job_description}
Required Skills: {job_skills}
Experience Level: {job_experience_level}
Employment Type: {job_employment_type}
Work Setup: {job_work_setup}
Location: {job_location}
Salary Range: {job_salary_min}-{job_salary_max} {job_currency}

**Match Score:** {match_score}% ({match_classification})

**Preference Matches:**
- Location: {location_match}
- Work Setup: {work_setup_match}
- Employment Type: {employment_type_match}
- Salary: {salary_match}

**Task:**
Analyze why this job is a {match_classification} match for the candidate. Provide specific, actionable insights.

**Response Format (JSON):**
{{
  "matching_factors": [
    "Specific reason 1 (e.g., '5+ years Python experience matches Senior requirement')",
    "Specific reason 2 (e.g., 'Remote preference aligns with job location')",
    "Specific reason 3 (e.g., 'React and TypeScript skills match 80% of required skills')"
  ],
  "missing_requirements": [
    "Specific gap 1 (e.g., 'Job requires GraphQL experience, not listed in profile')",
    "Specific gap 2 (e.g., 'Salary expectation $120-150K exceeds job range $100-130K')"
  ],
  "overall_reasoning": "2-3 sentence summary explaining the match quality and key decision factors",
  "confidence_score": 0.85
}}

**Guidelines:**
- Be specific and evidence-based (reference actual skills, experience, preferences)
- Focus on 3-5 key matching factors (most important first)
- Identify 0-3 missing requirements (only significant gaps)
- Confidence score: 0.7-1.0 (based on data completeness and alignment strength)
- Keep overall_reasoning concise but insightful (2-3 sentences)
"""


class ExplanationService:
    """
    Generate AI explanations for job-candidate matches.
    
    Uses OpenAI GPT-4o-mini to analyze match quality and provide detailed
    reasoning about why a job matches (or doesn't match) a candidate's profile.
    Caches explanations to reduce API costs.
    """

    def __init__(
        self,
        openai_provider: OpenAIProvider,
        candidate_repo: CandidateRepository,
        job_repo: JobPostingRepository,
        cache: ExplanationCache
    ):
        """
        Initialize explanation service with dependencies.
        
        Args:
            openai_provider: OpenAI provider for GPT completions
            candidate_repo: Repository for candidate data
            job_repo: Repository for job posting data
            cache: Explanation cache service
        """
        self.openai_provider = openai_provider
        self.candidate_repo = candidate_repo
        self.job_repo = job_repo
        self.cache = cache
        self.logger = structlog.get_logger().bind(service="explanation_service")

    def build_explanation_prompt(
        self,
        candidate: Candidate,
        job: JobPosting,
        match_score: Decimal,
        match_classification: str,
        preference_matches: dict[str, bool]
    ) -> str:
        """
        Build explanation prompt with candidate and job context.
        
        Args:
            candidate: Candidate model instance
            job: JobPosting model instance
            match_score: Match score 0-100
            match_classification: Excellent, Great, Good, Fair, or Poor
            preference_matches: Dict of preference match flags
        
        Returns:
            Formatted prompt string for GPT
        """
        # Format candidate data
        candidate_skills = ", ".join(candidate.skills) if candidate.skills else "None listed"
        candidate_experience = candidate.experience_years if candidate.experience_years is not None else "Not specified"

        prefs = candidate.job_preferences or {}
        preferred_locations = ", ".join(prefs.get("locations", [])) if prefs.get("locations") else "Not specified"
        preferred_employment_types = ", ".join(prefs.get("employment_types", [])) if prefs.get("employment_types") else "Not specified"
        preferred_work_setups = ", ".join(prefs.get("work_setups", [])) if prefs.get("work_setups") else "Not specified"
        salary_min = prefs.get("salary_min", "Not specified")
        salary_max = prefs.get("salary_max", "Not specified")
        currency = "AUD"
        role_categories = ", ".join(prefs.get("role_categories", [])) if prefs.get("role_categories") else "Not specified"

        # Format job data
        job_skills = ", ".join(job.required_skills) if job.required_skills else "None listed"
        job_description = job.description[:500]  # Truncate to avoid token bloat
        if len(job.description) > 500:
            job_description += "..."

        # Format preference matches
        location_match = "✅ Yes" if preference_matches.get("location") else "❌ No"
        work_setup_match = "✅ Yes" if preference_matches.get("work_setup") else "❌ No"
        employment_type_match = "✅ Yes" if preference_matches.get("employment_type") else "❌ No"
        salary_match = "✅ Yes" if preference_matches.get("salary") else "❌ No"

        # Build prompt
        prompt = EXPLANATION_PROMPT_TEMPLATE.format(
            candidate_skills=candidate_skills,
            candidate_experience=candidate_experience,
            preferred_locations=preferred_locations,
            preferred_employment_types=preferred_employment_types,
            preferred_work_setups=preferred_work_setups,
            salary_min=salary_min,
            salary_max=salary_max,
            currency=currency,
            role_categories=role_categories,
            job_title=job.title,
            job_company=job.company,
            job_description=job_description,
            job_skills=job_skills,
            job_experience_level=job.experience_level,
            job_employment_type=job.employment_type,
            job_work_setup=job.work_setup,
            job_location=job.location,
            job_salary_min=job.salary_min if job.salary_min is not None else "Not specified",
            job_salary_max=job.salary_max if job.salary_max is not None else "Not specified",
            job_currency=job.salary_currency,
            match_score=match_score,
            match_classification=match_classification,
            location_match=location_match,
            work_setup_match=work_setup_match,
            employment_type_match=employment_type_match,
            salary_match=salary_match
        )

        return prompt

    async def generate_explanation(
        self,
        candidate_id: UUID,
        job_id: UUID,
        match_score: Decimal,
        match_classification: str,
        preference_matches: dict[str, bool]
    ) -> dict[str, any]:
        """
        Generate explanation for job-candidate match.
        
        Checks cache first, then generates using OpenAI GPT-4o-mini if needed.
        Explanations are only generated for matches with score ≥40% (Fair or better).
        
        Args:
            candidate_id: UUID of candidate
            job_id: UUID of job posting
            match_score: Match score 0-100
            match_classification: Excellent, Great, Good, Fair, or Poor
            preference_matches: Dict of preference match flags
        
        Returns:
            Dict with matching_factors, missing_requirements, overall_reasoning, confidence_score
        
        Raises:
            HTTPException: 404 if candidate/job not found, 400 if match score too low, 500 if generation fails
        """
        # Check cache first
        cache_key = f"explanation:{candidate_id}:{job_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            self.logger.info(
                "explanation_cache_hit",
                candidate_id=str(candidate_id),
                job_id=str(job_id)
            )
            return cached

        # Validate match score (only generate for Fair or better)
        if match_score < 40:
            self.logger.warning(
                "explanation_match_too_low",
                candidate_id=str(candidate_id),
                job_id=str(job_id),
                match_score=float(match_score)
            )
            raise HTTPException(
                status_code=400,
                detail="Explanations only available for matches with score ≥40% (Fair or better)"
            )

        # Fetch candidate and job data
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            self.logger.error(
                "explanation_candidate_not_found",
                candidate_id=str(candidate_id)
            )
            raise HTTPException(status_code=404, detail="Candidate not found")

        job = await self.job_repo.get_by_id(job_id)
        if not job:
            self.logger.error(
                "explanation_job_not_found",
                job_id=str(job_id)
            )
            raise HTTPException(status_code=404, detail="Job posting not found")

        # Build explanation prompt
        prompt = self.build_explanation_prompt(
            candidate=candidate,
            job=job,
            match_score=match_score,
            match_classification=match_classification,
            preference_matches=preference_matches
        )

        # Call OpenAI GPT-4o-mini for explanation
        try:
            self.logger.info(
                "generating_explanation",
                candidate_id=str(candidate_id),
                job_id=str(job_id),
                match_score=float(match_score)
            )

            # Generate completion with GPT-4o-mini
            response_text = await self.openai_provider.generate_completion(
                messages=[
                    {"role": "system", "content": "You are a career advisor providing job match analysis. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )

            # Parse JSON response
            explanation = json.loads(response_text)

            # Validate response structure
            required_keys = ["matching_factors", "missing_requirements", "overall_reasoning", "confidence_score"]
            if not all(key in explanation for key in required_keys):
                self.logger.error(
                    "explanation_invalid_structure",
                    candidate_id=str(candidate_id),
                    job_id=str(job_id),
                    missing_keys=[k for k in required_keys if k not in explanation]
                )
                raise ValueError("Invalid explanation format from GPT - missing required fields")

            # Cache explanation (24 hour TTL)
            await self.cache.set(cache_key, explanation, ttl_seconds=86400)

            self.logger.info(
                "explanation_generated",
                candidate_id=str(candidate_id),
                job_id=str(job_id),
                confidence=explanation["confidence_score"],
                factors_count=len(explanation["matching_factors"]),
                gaps_count=len(explanation["missing_requirements"])
            )

            return explanation

        except json.JSONDecodeError as e:
            self.logger.error(
                "explanation_json_parse_failed",
                candidate_id=str(candidate_id),
                job_id=str(job_id),
                error=str(e),
                response=response_text[:200]  # Log first 200 chars
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to parse explanation from AI response"
            ) from e

        except HTTPException:
            # Re-raise HTTP exceptions (404, 400)
            raise

        except Exception as e:
            self.logger.error(
                "explanation_generation_failed",
                candidate_id=str(candidate_id),
                job_id=str(job_id),
                error=str(e),
                error_type=type(e).__name__
            )
            raise HTTPException(
                status_code=500,
                detail=f"Explanation generation failed: {str(e)}"
            ) from e
