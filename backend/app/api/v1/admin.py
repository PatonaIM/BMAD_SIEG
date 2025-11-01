"""Admin API endpoints for system management."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.config import settings
from app.models import Candidate
from app.utils.supabase_storage import SupabaseStorageClient

router = APIRouter(prefix="/admin", tags=["admin"])
logger = structlog.get_logger(__name__)


@router.get("/storage/usage")
async def get_storage_usage(
    current_user: Candidate = Depends(get_current_user)
):
    """
    Get current video storage usage (authenticated users only).
    
    Returns storage metrics including total size, file count, and threshold warning.
    
    Note: In production, this should be restricted to admin users only.
    For MVP, any authenticated user can view storage usage.
    
    Args:
        current_user: Authenticated candidate
        
    Returns:
        dict with:
            - total_size_bytes: Total storage used in bytes
            - total_size_gb: Total storage used in GB
            - file_count: Number of files in bucket
            - threshold_gb: Configured storage threshold
            - warning: Boolean indicating if threshold exceeded
            
    Raises:
        500: If storage API request fails
    """
    try:
        storage_client = SupabaseStorageClient()
        usage = await storage_client.get_bucket_usage()
        
        # Check against threshold
        threshold_exceeded = usage["total_size_gb"] > settings.video_storage_threshold_gb
        
        if threshold_exceeded:
            logger.warning(
                "storage_threshold_exceeded",
                total_gb=usage["total_size_gb"],
                threshold_gb=settings.video_storage_threshold_gb,
                file_count=usage["file_count"]
            )
        
        response = {
            **usage,
            "threshold_gb": settings.video_storage_threshold_gb,
            "warning": threshold_exceeded
        }
        
        logger.info(
            "storage_usage_retrieved",
            user_id=str(current_user.id),
            usage_gb=usage["total_size_gb"]
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "storage_usage_retrieval_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage usage"
        )
