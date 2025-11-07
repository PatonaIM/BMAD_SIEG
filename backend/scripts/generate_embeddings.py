#!/usr/bin/env python3
"""
Embedding Generation Script

Purpose: Generate semantic embeddings for existing candidates and job postings.
         Designed for initial deployment seeding and large-scale backfills (unlimited records).

Usage:
    From backend directory:
        uv run python scripts/generate_embeddings.py [options]

    Options:
        --dry-run           Show what would be processed without API calls
        --force             Regenerate embeddings for records that already have them
        --candidates-only   Process only candidates
        --jobs-only         Process only job postings
        --limit N           Records per batch (default: 100, max: 1000)
        --help              Show this help message

Output:
    Progress logs for each batch and final summary with counts.

Behavior:
    - Idempotent: Skips records with existing embeddings (unless --force)
    - Automatic pagination: Processes ALL records in database
    - Batch processing: Configurable limit per API call (default 100)
    - Error resilient: Continues on individual failures, logs errors
    - Rate limit handling: Built into EmbeddingService (exponential backoff)
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path
from typing import Any

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings  # noqa: E402
from app.core.database import AsyncSessionLocal  # noqa: E402
from app.repositories.candidate import CandidateRepository  # noqa: E402
from app.repositories.job_posting_repository import JobPostingRepository  # noqa: E402
from app.services.embedding_service import EmbeddingService  # noqa: E402

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_CONFIG_ERROR = 2
EXIT_AUTH_ERROR = 3


async def process_all_candidates(
    embedding_service: EmbeddingService,
    dry_run: bool,
    force: bool,
    limit_per_batch: int
) -> dict[str, Any]:
    """
    Process all candidate embeddings with pagination.

    Args:
        embedding_service: Service for generating embeddings
        dry_run: If true, only show counts without processing
        force: If true, regenerate existing embeddings
        limit_per_batch: Number of records to process per batch

    Returns:
        Summary statistics dict
    """
    print("[INFO] Querying candidates with completeness >= 40%...")

    total_processed = 0
    total_successful = 0
    total_failed = 0
    all_errors: list[str] = []
    batch_num = 0

    while True:
        batch_num += 1

        if dry_run:
            # Query count for dry run
            candidates = await embedding_service.candidate_repo.get_candidates_for_embedding(
                skip_with_embedding=not force,
                limit=limit_per_batch
            )
            if candidates:
                print(f"[INFO] Would process {len(candidates)} candidates in batch {batch_num}")
                total_processed += len(candidates)
            break

        # Process batch
        print(f"\n[INFO] Processing candidates batch {batch_num} ({limit_per_batch} max)...")

        stats = await embedding_service.batch_generate_candidate_embeddings(
            force=force,
            limit=limit_per_batch
        )

        # Check if any records were processed
        if stats["total_processed"] == 0:
            print("[INFO] No more candidates to process")
            break

        # Accumulate stats
        total_processed += stats["total_processed"]
        total_successful += stats["successful"]
        total_failed += stats["failed"]
        all_errors.extend(stats["errors"])

        # Log batch results
        print(f"[INFO] ✓ Batch {batch_num} completed: {stats['successful']} successful, {stats['failed']} failed")

        if stats["errors"]:
            print(f"[WARNING] Batch {batch_num} had errors:")
            for error in stats["errors"][:3]:  # Show first 3 errors
                print(f"  - {error}")
            if len(stats["errors"]) > 3:
                print(f"  ... and {len(stats['errors']) - 3} more errors")

        # If we processed fewer than the limit, we're done
        if stats["total_processed"] < limit_per_batch:
            print("[INFO] All candidates processed")
            break

    if dry_run and total_processed == 0:
        print("[INFO] No candidates found matching criteria")

    return {
        "total_processed": total_processed,
        "successful": total_successful,
        "failed": total_failed,
        "errors": all_errors
    }


async def process_all_jobs(
    embedding_service: EmbeddingService,
    dry_run: bool,
    force: bool,
    limit_per_batch: int
) -> dict[str, Any]:
    """
    Process all job posting embeddings with pagination.

    Args:
        embedding_service: Service for generating embeddings
        dry_run: If true, only show counts without processing
        force: If true, regenerate existing embeddings
        limit_per_batch: Number of records to process per batch

    Returns:
        Summary statistics dict
    """
    print("[INFO] Querying active job postings...")

    total_processed = 0
    total_successful = 0
    total_failed = 0
    all_errors: list[str] = []
    batch_num = 0

    while True:
        batch_num += 1

        if dry_run:
            # Query count for dry run
            jobs = await embedding_service.job_repo.get_jobs_for_embedding(
                skip_with_embedding=not force,
                limit=limit_per_batch
            )
            if jobs:
                print(f"[INFO] Would process {len(jobs)} jobs in batch {batch_num}")
                total_processed += len(jobs)
            break

        # Process batch
        print(f"\n[INFO] Processing jobs batch {batch_num} ({limit_per_batch} max)...")

        stats = await embedding_service.batch_generate_job_embeddings(
            force=force,
            limit=limit_per_batch
        )

        # Check if any records were processed
        if stats["total_processed"] == 0:
            print("[INFO] No more jobs to process")
            break

        # Accumulate stats
        total_processed += stats["total_processed"]
        total_successful += stats["successful"]
        total_failed += stats["failed"]
        all_errors.extend(stats["errors"])

        # Log batch results
        print(f"[INFO] ✓ Batch {batch_num} completed: {stats['successful']} successful, {stats['failed']} failed")

        if stats["errors"]:
            print(f"[WARNING] Batch {batch_num} had errors:")
            for error in stats["errors"][:3]:  # Show first 3 errors
                print(f"  - {error}")
            if len(stats["errors"]) > 3:
                print(f"  ... and {len(stats['errors']) - 3} more errors")

        # If we processed fewer than the limit, we're done
        if stats["total_processed"] < limit_per_batch:
            print("[INFO] All jobs processed")
            break

    if dry_run and total_processed == 0:
        print("[INFO] No jobs found matching criteria")

    return {
        "total_processed": total_processed,
        "successful": total_successful,
        "failed": total_failed,
        "errors": all_errors
    }


async def main() -> None:
    """Main script execution."""
    parser = argparse.ArgumentParser(
        description="Generate semantic embeddings for candidates and job postings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run to see what would be processed
  uv run python scripts/generate_embeddings.py --dry-run

  # Process only candidates
  uv run python scripts/generate_embeddings.py --candidates-only

  # Process only jobs
  uv run python scripts/generate_embeddings.py --jobs-only

  # Force regeneration of existing embeddings
  uv run python scripts/generate_embeddings.py --force

  # Process with custom batch size
  uv run python scripts/generate_embeddings.py --limit 50
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without making API calls'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate embeddings for records that already have them'
    )
    parser.add_argument(
        '--candidates-only',
        action='store_true',
        help='Process only candidates'
    )
    parser.add_argument(
        '--jobs-only',
        action='store_true',
        help='Process only job postings'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Records per batch (default: 100, max: 1000)'
    )

    args = parser.parse_args()

    # Validate limit
    if args.limit > 1000:
        print("[ERROR] Limit cannot exceed 1000")
        sys.exit(EXIT_CONFIG_ERROR)

    if args.limit < 1:
        print("[ERROR] Limit must be at least 1")
        sys.exit(EXIT_CONFIG_ERROR)

    # Print header
    print("=" * 50)
    print("=== Embedding Generation Script ===")
    print("=" * 50)
    print(f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else settings.database_url}")
    print("OpenAI Model: text-embedding-3-large")
    print(f"Dry Run: {args.dry_run}")
    print(f"Force: {args.force}")
    print(f"Limit per batch: {args.limit}")
    print("=" * 50)
    print()

    start_time = time.time()

    candidate_stats: dict[str, Any] = {
        "total_processed": 0,
        "successful": 0,
        "failed": 0,
        "errors": []
    }
    job_stats: dict[str, Any] = {
        "total_processed": 0,
        "successful": 0,
        "failed": 0,
        "errors": []
    }

    try:
        # Initialize service
        async with AsyncSessionLocal() as session:
            candidate_repo = CandidateRepository(session)
            job_repo = JobPostingRepository(session)
            embedding_service = EmbeddingService(candidate_repo, job_repo)

            # Process candidates
            if not args.jobs_only:
                print("\n[INFO] === Processing Candidates ===")
                candidate_stats = await process_all_candidates(
                    embedding_service, args.dry_run, args.force, args.limit
                )

            # Process jobs
            if not args.candidates_only:
                print("\n[INFO] === Processing Job Postings ===")
                job_stats = await process_all_jobs(
                    embedding_service, args.dry_run, args.force, args.limit
                )

    except Exception as e:
        print(f"\n[ERROR] Unexpected error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(EXIT_ERROR)

    # Calculate duration
    duration = time.time() - start_time

    # Print summary
    print("\n" + "=" * 50)
    print("=== Summary ===")
    print("=" * 50)

    if not args.jobs_only:
        print(f"Candidates: {candidate_stats['successful']}/{candidate_stats['total_processed']} successful ({candidate_stats['failed']} failed)")

    if not args.candidates_only:
        print(f"Jobs: {job_stats['successful']}/{job_stats['total_processed']} successful ({job_stats['failed']} failed)")

    total_processed = candidate_stats['total_processed'] + job_stats['total_processed']
    total_successful = candidate_stats['successful'] + job_stats['successful']
    total_failed = candidate_stats['failed'] + job_stats['failed']

    print(f"\nTotal: {total_successful}/{total_processed} successful ({total_failed} failed)")
    print(f"Duration: {duration:.1f} seconds")

    # Show error summary if any
    all_errors = candidate_stats['errors'] + job_stats['errors']
    if all_errors:
        print(f"\n[WARNING] {len(all_errors)} total errors occurred")
        print("First 5 errors:")
        for error in all_errors[:5]:
            print(f"  - {error}")

    print("=" * 50)

    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Script interrupted by user")
        sys.exit(EXIT_SUCCESS)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(EXIT_ERROR)
