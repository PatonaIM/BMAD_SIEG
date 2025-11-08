"""Resume upload service for handling PDF uploads and storage."""
from uuid import UUID

import structlog
from fastapi import UploadFile

from app.models.resume import Resume
from app.repositories.resume import ResumeRepository
from app.utils.pdf_extractor import PDFTextExtractor
from app.utils.supabase_storage import SupabaseStorageClient

logger = structlog.get_logger(__name__)


class ResumeUploadService:
    """Service for uploading resumes to storage and managing resume records."""

    # File validation constants
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
    ALLOWED_MIME_TYPES = {"application/pdf"}

    def __init__(
        self,
        storage_client: SupabaseStorageClient,
        resume_repo: ResumeRepository,
        pdf_extractor: PDFTextExtractor,
    ):
        """
        Initialize resume upload service.

        Args:
            storage_client: Supabase storage client for file uploads
            resume_repo: Repository for resume data access
            pdf_extractor: Utility for extracting text from PDFs
        """
        self.storage_client = storage_client
        self.resume_repo = resume_repo
        self.pdf_extractor = pdf_extractor
        self.bucket_name = "candidate-resumes"

    async def upload_resume(
        self, candidate_id: UUID, file: UploadFile
    ) -> tuple[Resume, str]:
        """
        Upload resume PDF and create database record.

        This method:
        1. Validates file (PDF, size < 5MB)
        2. Deactivates previous active resumes
        3. Uploads to Supabase Storage
        4. Extracts text with pdfplumber
        5. Creates Resume record

        Args:
            candidate_id: UUID of the candidate
            file: Uploaded PDF file

        Returns:
            Tuple of (Resume instance, extracted text)

        Raises:
            ValueError: If file validation fails
            Exception: If upload or extraction fails
        """
        logger.info(
            "resume_upload_started",
            candidate_id=str(candidate_id),
            filename=file.filename,
            content_type=file.content_type,
        )

        # Validate file
        self._validate_file(file)

        # Read file content
        file_bytes = await file.read()
        file_size = len(file_bytes)

        logger.debug(
            "resume_file_read",
            candidate_id=str(candidate_id),
            file_size=file_size,
        )

        # Create Resume record first (to get resume_id)
        resume = Resume(
            candidate_id=candidate_id,
            file_name=file.filename or "resume.pdf",
            file_size=file_size,
            file_url="",  # Will update after upload
            is_active=True,
        )

        # Deactivate all other resumes for this candidate
        await self.resume_repo.deactivate_all_for_candidate(candidate_id)

        # Save resume to get ID
        saved_resume = await self.resume_repo.create(resume)

        try:
            # Upload to Supabase Storage: {candidate_id}/{resume_id}.pdf
            storage_path = f"{candidate_id}/{saved_resume.id}.pdf"
            await self._upload_to_storage(storage_path, file_bytes)

            # Update resume with storage path
            saved_resume.file_url = storage_path
            await self.resume_repo.db.commit()
            await self.resume_repo.db.refresh(saved_resume)

            logger.info(
                "resume_uploaded_to_storage",
                candidate_id=str(candidate_id),
                resume_id=str(saved_resume.id),
                storage_path=storage_path,
            )

            # Extract text from PDF
            extracted_text = self.pdf_extractor.extract_text(file_bytes)

            logger.info(
                "resume_upload_completed",
                candidate_id=str(candidate_id),
                resume_id=str(saved_resume.id),
                extracted_text_length=len(extracted_text),
            )

            return saved_resume, extracted_text

        except Exception as e:
            # Cleanup: delete resume record if upload/extraction fails
            logger.error(
                "resume_upload_failed_cleanup",
                candidate_id=str(candidate_id),
                resume_id=str(saved_resume.id),
                error=str(e),
            )
            await self.resume_repo.delete(saved_resume.id)
            raise

    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.

        Args:
            file: Uploaded file

        Raises:
            ValueError: If validation fails
        """
        # Check MIME type
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            logger.warning(
                "invalid_file_type",
                content_type=file.content_type,
                filename=file.filename,
            )
            raise ValueError(
                f"Only PDF files are allowed. Got: {file.content_type}"
            )

        # Note: Size validation happens after reading the file
        # Frontend should validate size before upload

    async def _upload_to_storage(self, file_path: str, file_bytes: bytes) -> None:
        """
        Upload file to Supabase Storage.

        Args:
            file_path: Storage path (e.g., "candidate_id/resume_id.pdf")
            file_bytes: File content bytes

        Raises:
            Exception: If upload fails
        """
        # Validate size
        if len(file_bytes) > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size {len(file_bytes)} exceeds maximum {self.MAX_FILE_SIZE_BYTES} bytes"
            )

        # Upload using adapted Supabase storage client
        # Note: The existing SupabaseStorageClient uses "interview-recordings" bucket
        # We need to use "candidate-resumes" bucket
        try:
            response = self.storage_client.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": "application/pdf"},
            )
            logger.debug("resume_uploaded_to_supabase", file_path=file_path)
        except Exception as e:
            logger.error(
                "supabase_upload_failed",
                file_path=file_path,
                error=str(e),
            )
            raise

    async def delete_resume(self, resume_id: UUID, candidate_id: UUID) -> bool:
        """
        Delete resume from database and storage.

        Args:
            resume_id: UUID of the resume
            candidate_id: UUID of the candidate (for security check)

        Returns:
            True if deletion successful

        Raises:
            ValueError: If resume not found or doesn't belong to candidate
        """
        # Verify resume belongs to candidate
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume or resume.candidate_id != candidate_id:
            raise ValueError(f"Resume {resume_id} not found for candidate {candidate_id}")

        logger.info(
            "resume_deletion_started",
            resume_id=str(resume_id),
            candidate_id=str(candidate_id),
        )

        # Delete from storage
        try:
            self.storage_client.client.storage.from_(self.bucket_name).remove(
                [resume.file_url]
            )
            logger.debug(
                "resume_deleted_from_storage",
                file_url=resume.file_url,
            )
        except Exception as e:
            logger.warning(
                "storage_deletion_failed",
                file_url=resume.file_url,
                error=str(e),
            )
            # Continue with DB deletion even if storage fails

        # Delete from database (cascade deletes analyses)
        await self.resume_repo.delete(resume_id)

        logger.info(
            "resume_deleted",
            resume_id=str(resume_id),
            candidate_id=str(candidate_id),
        )

        return True

    async def generate_signed_url(self, resume_id: UUID, candidate_id: UUID, expires_in: int = 86400) -> str:
        """
        Generate temporary signed URL for resume download.

        Args:
            resume_id: UUID of the resume
            candidate_id: UUID of the candidate (for security check)
            expires_in: URL expiration time in seconds (default: 24 hours)

        Returns:
            Signed URL string

        Raises:
            ValueError: If resume not found or doesn't belong to candidate
        """
        # Verify resume belongs to candidate
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume or resume.candidate_id != candidate_id:
            raise ValueError(f"Resume {resume_id} not found for candidate {candidate_id}")

        try:
            response = self.storage_client.client.storage.from_(self.bucket_name).create_signed_url(
                path=resume.file_url,
                expires_in=expires_in,
            )
            signed_url = response.get("signedURL")
            logger.debug(
                "signed_url_generated",
                resume_id=str(resume_id),
                expires_in=expires_in,
            )
            return signed_url
        except Exception as e:
            logger.error(
                "signed_url_generation_failed",
                resume_id=str(resume_id),
                error=str(e),
            )
            raise
