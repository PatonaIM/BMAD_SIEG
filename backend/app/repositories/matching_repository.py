"""Repository for job matching with pgvector semantic similarity."""
from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_posting import JobPosting


class MatchingRepository:
    """
    Repository for job matching operations using pgvector.
    
    Handles vector similarity queries with cosine distance and preference filtering.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db
        self.logger = structlog.get_logger().bind(repository="matching_repository")

    async def get_vector_matches(
        self,
        candidate_embedding: list[float],
        filters: dict[str, Any],
        limit: int,
        offset: int
    ) -> list[dict[str, Any]]:
        """
        Get job matches ranked by vector similarity with preference filtering.
        
        Uses pgvector cosine distance operator (<=>) with HNSW index for fast
        approximate nearest neighbor search. Applies optional preference filters
        for location, work_setup, employment_type, and salary range.
        
        Args:
            candidate_embedding: 3072-dimensional embedding vector
            filters: Dict with optional keys: preferred_locations, preferred_work_setups,
                    preferred_employment_types, candidate_salary_min, candidate_salary_max
            limit: Maximum number of results to return
            offset: Number of results to skip (pagination)
        
        Returns:
            List of dicts with keys: job (JobPosting), similarity_score (float 0-1)
        """
        self.logger.bind(
            candidate_embedding_size=len(candidate_embedding),
            filters=filters,
            limit=limit,
            offset=offset
        )

        # Convert numpy array to list if needed
        if hasattr(candidate_embedding, 'tolist'):
            candidate_embedding = candidate_embedding.tolist()
        
        # Convert list to PostgreSQL vector string format: '[val1,val2,...]'
        embedding_str = '[' + ','.join(str(x) for x in candidate_embedding) + ']'

        # Build base query
        query_parts = [
            "SELECT jp.*, 1 - (jp.job_embedding <=> :candidate_embedding) AS similarity_score",
            "FROM job_postings jp",
            "WHERE jp.status = 'active'",
            "AND jp.job_embedding IS NOT NULL"
        ]

        # Build preference filters
        params: dict[str, Any] = {"candidate_embedding": embedding_str}

        # Location filter
        if filters.get("preferred_locations"):
            locations = filters["preferred_locations"]
            query_parts.append(
                "(jp.location = ANY(:preferred_locations) OR jp.work_setup = 'remote')"
            )
            params["preferred_locations"] = locations

        # Work setup filter
        if filters.get("preferred_work_setups"):
            work_setups = filters["preferred_work_setups"]
            query_parts.append("jp.work_setup = ANY(:preferred_work_setups)")
            params["preferred_work_setups"] = work_setups

        # Employment type filter
        if filters.get("preferred_employment_types"):
            employment_types = filters["preferred_employment_types"]
            query_parts.append("jp.employment_type = ANY(:preferred_employment_types)")
            params["preferred_employment_types"] = employment_types

        # Salary range overlap filter
        if filters.get("candidate_salary_min") and filters.get("candidate_salary_max"):
            query_parts.append(
                "(jp.salary_max >= :candidate_salary_min AND jp.salary_min <= :candidate_salary_max)"
            )
            params["candidate_salary_min"] = filters["candidate_salary_min"]
            params["candidate_salary_max"] = filters["candidate_salary_max"]

        # Add ordering and pagination
        query_parts.extend([
            "ORDER BY jp.job_embedding <=> :candidate_embedding",
            "LIMIT :limit OFFSET :offset"
        ])
        params["limit"] = limit
        params["offset"] = offset

        # Combine query
        query = " ".join(query_parts)

        self.logger.info("executing_vector_match_query", query_preview=query[:200])

        # Execute query
        result = await self.db.execute(text(query), params)
        rows = result.fetchall()

        self.logger.info(
            "vector_match_query_completed",
            result_count=len(rows)
        )

        # Convert rows to job objects with similarity scores
        matches = []
        for row in rows:
            # Extract job fields (all columns except similarity_score)
            job_data = {
                "id": row.id,
                "title": row.title,
                "company": row.company,
                "description": row.description,
                "role_category": row.role_category,
                "tech_stack": row.tech_stack,
                "employment_type": row.employment_type,
                "work_setup": row.work_setup,
                "location": row.location,
                "salary_min": row.salary_min,
                "salary_max": row.salary_max,
                "salary_currency": row.salary_currency,
                "required_skills": row.required_skills,
                "experience_level": row.experience_level,
                "status": row.status,
                "is_cancelled": row.is_cancelled,
                "cancellation_reason": row.cancellation_reason,
                "job_embedding": row.job_embedding,
                "created_at": row.created_at,
                "updated_at": row.updated_at
            }

            # Create JobPosting instance
            job = JobPosting(**job_data)

            matches.append({
                "job": job,
                "similarity_score": float(row.similarity_score)
            })

        return matches

    async def count_matching_jobs(
        self,
        candidate_embedding: list[float],
        filters: dict[str, Any]
    ) -> int:
        """
        Count total matching jobs for pagination metadata.
        
        Applies same filters as get_vector_matches but only returns count.
        
        Args:
            candidate_embedding: 3072-dimensional embedding vector
            filters: Dict with optional preference filters (same as get_vector_matches)
        
        Returns:
            Total count of matching jobs
        """
        # Convert numpy array to list if needed
        if hasattr(candidate_embedding, 'tolist'):
            candidate_embedding = candidate_embedding.tolist()
        
        # Convert list to PostgreSQL vector string format: '[val1,val2,...]'
        embedding_str = '[' + ','.join(str(x) for x in candidate_embedding) + ']'

        # Build count query with same filters
        query_parts = [
            "SELECT COUNT(*)",
            "FROM job_postings jp",
            "WHERE jp.status = 'active'",
            "AND jp.job_embedding IS NOT NULL"
        ]

        params: dict[str, Any] = {"candidate_embedding": embedding_str}

        # Apply same filters
        if filters.get("preferred_locations"):
            locations = filters["preferred_locations"]
            query_parts.append(
                "(jp.location = ANY(:preferred_locations) OR jp.work_setup = 'remote')"
            )
            params["preferred_locations"] = locations

        if filters.get("preferred_work_setups"):
            work_setups = filters["preferred_work_setups"]
            query_parts.append("jp.work_setup = ANY(:preferred_work_setups)")
            params["preferred_work_setups"] = work_setups

        if filters.get("preferred_employment_types"):
            employment_types = filters["preferred_employment_types"]
            query_parts.append("jp.employment_type = ANY(:preferred_employment_types)")
            params["preferred_employment_types"] = employment_types

        if filters.get("candidate_salary_min") and filters.get("candidate_salary_max"):
            query_parts.append(
                "(jp.salary_max >= :candidate_salary_min AND jp.salary_min <= :candidate_salary_max)"
            )
            params["candidate_salary_min"] = filters["candidate_salary_min"]
            params["candidate_salary_max"] = filters["candidate_salary_max"]

        query = " ".join(query_parts)

        result = await self.db.execute(text(query), params)
        count = result.scalar()

        self.logger.info("count_matching_jobs_completed", total_count=count)

        return int(count) if count else 0
