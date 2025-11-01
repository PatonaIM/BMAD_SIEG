#!/usr/bin/env python3
"""
Script to run video cleanup job manually or via cron.

Usage:
    python scripts/cleanup_videos.py

This script:
1. Soft-deletes videos older than VIDEO_RETENTION_DAYS
2. Hard-deletes videos soft-deleted more than HARD_DELETE_AFTER_DAYS ago
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.video_cleanup_service import VideoCleanupService
from app.utils.supabase_storage import SupabaseStorageClient


async def main():
    """Run video cleanup jobs."""
    print("=" * 70)
    print("Video Cleanup Script")
    print("=" * 70)
    print(f"Retention period: {settings.video_retention_days} days")
    print(f"Hard delete after: {settings.hard_delete_after_days} days")
    print(f"Storage threshold: {settings.video_storage_threshold_gb} GB")
    print("-" * 70)
    
    # Initialize dependencies
    storage_client = SupabaseStorageClient()
    
    async with AsyncSessionLocal() as db:
        cleanup_service = VideoCleanupService(db, storage_client)
        
        # Step 1: Soft delete expired videos
        print("\n[1/3] Soft-deleting expired videos...")
        soft_delete_result = await cleanup_service.cleanup_expired_videos(
            retention_days=settings.video_retention_days
        )
        print(f"✓ Soft deleted: {soft_delete_result['soft_deleted']}")
        print(f"✗ Errors: {soft_delete_result['errors']}")
        
        # Step 2: Hard delete old soft-deleted videos
        print("\n[2/3] Hard-deleting old soft-deleted videos...")
        hard_delete_result = await cleanup_service.hard_delete_old_soft_deleted_videos(
            days_after_soft_delete=settings.hard_delete_after_days
        )
        print(f"✓ Hard deleted: {hard_delete_result['hard_deleted']}")
        print(f"✗ Errors: {hard_delete_result['errors']}")
        
        # Step 3: Check storage usage
        print("\n[3/3] Checking storage usage...")
        usage = await storage_client.get_bucket_usage()
        print(f"Storage used: {usage['total_size_gb']:.3f} GB")
        print(f"File count: {usage['file_count']}")
        
        # Check threshold
        if usage['total_size_gb'] > settings.video_storage_threshold_gb:
            print(f"\n⚠️  WARNING: Storage usage exceeds threshold of {settings.video_storage_threshold_gb} GB!")
        else:
            print(f"\n✓ Storage usage within threshold")
    
    print("-" * 70)
    print("Cleanup completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
