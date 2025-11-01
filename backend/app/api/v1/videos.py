"""Video management API endpoints."""
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import Candidate, Interview, VideoRecording

router = APIRouter(prefix="/videos", tags=["videos"])
logger = structlog.get_logger(__name__)


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_video(
    interview_id: UUID,
    current_user: Candidate = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete video for an interview (GDPR compliance).
    
    Only the candidate who owns the interview can delete the video.
    This sets the deleted_at timestamp without removing the file from storage.
    Actual storage deletion happens via the cleanup job after retention period.
    
    Args:
        interview_id: UUID of the interview
        current_user: Authenticated candidate
        db: Database session
        
    Returns:
        204 No Content on success
        
    Raises:
        404: Video not found
        403: User not authorized to delete this video
    """
    # Get interview to verify ownership
    stmt = select(Interview).where(Interview.id == interview_id)
    result = await db.execute(stmt)
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Verify candidate owns this interview
    if interview.candidate_id != current_user.id:
        logger.warning(
            "unauthorized_video_deletion_attempt",
            candidate_id=str(current_user.id),
            interview_id=str(interview_id),
            owner_id=str(interview.candidate_id)
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this video"
        )
    
    # Get video recording
    stmt = select(VideoRecording).where(
        VideoRecording.interview_id == interview_id
    )
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video recording not found"
        )
    
    # Check if already deleted
    if video.deleted_at is not None:
        logger.info(
            "video_already_deleted",
            video_id=str(video.id),
            interview_id=str(interview_id)
        )
        return  # Already deleted, return success
    
    # Soft delete: set deleted_at timestamp
    from datetime import datetime
    video.deleted_at = datetime.utcnow()
    db.add(video)
    await db.commit()
    
    logger.info(
        "video_soft_deleted_by_candidate",
        video_id=str(video.id),
        interview_id=str(interview_id),
        candidate_id=str(current_user.id),
        storage_path=video.storage_path
    )
    
    return
