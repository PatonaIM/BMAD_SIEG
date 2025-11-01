"""VideoRecording model for video interview metadata."""
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VideoRecording(Base):
    """
    Video recording metadata model.

    Tracks video recordings for interviews with upload status, file metadata,
    and soft delete capability.

    Attributes:
        id: Unique identifier (UUID)
        interview_id: Foreign key to Interview (one-to-one)
        storage_path: Supabase Storage path to video file
        file_size_bytes: File size in bytes
        duration_seconds: Video duration in seconds
        resolution: Video resolution (e.g., "1280x720")
        bitrate_kbps: Video bitrate in kbps
        codec: Video codec (e.g., "H.264")
        upload_started_at: Timestamp when upload started
        upload_completed_at: Timestamp when upload completed (NULL if in progress)
        deleted_at: Soft delete timestamp (NULL if not deleted)
        recording_metadata: JSONB field for flexible metadata storage
        created_at: Timestamp of record creation
        updated_at: Timestamp of last update
        interview: Related Interview record (one-to-one)
    """

    __tablename__ = "video_recordings"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key (unique constraint for one-to-one relationship)
    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Storage metadata
    storage_path = Column(Text, nullable=False)

    # File metadata
    file_size_bytes = Column(BigInteger, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    resolution = Column(String(20), nullable=True)
    bitrate_kbps = Column(Integer, nullable=True)
    codec = Column(String(50), nullable=True)

    # Upload tracking
    upload_started_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    upload_completed_at = Column(DateTime, nullable=True, index=True)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True, index=True)

    # Flexible metadata storage (quality metrics, chunk info, etc.)
    recording_metadata = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    interview = relationship("Interview", back_populates="video_recording")

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "deleted" if self.deleted_at else (
            "completed" if self.upload_completed_at else "uploading"
        )
        return f"<VideoRecording {self.id} - Interview {self.interview_id} - {status}>"
