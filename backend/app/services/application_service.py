"""Business logic for application operations."""

from uuid import UUID

import structlog
from fastapi import HTTPException, status

from app.models.application import Application
from app.models.interview import Interview
from app.models.interview_session import InterviewSession
from app.repositories.application_repository import ApplicationRepository
from app.repositories.interview import InterviewRepository
from app.repositories.job_posting_repository import JobPostingRepository
from app.services.interview_engine import InterviewEngine


class ApplicationService:
    """Service for application business logic."""

    def __init__(
        self,
        app_repo: ApplicationRepository,
        job_repo: JobPostingRepository,
        interview_repo: InterviewRepository,
        interview_engine: InterviewEngine,
    ):
        """
        Initialize application service with repositories and services.

        Args:
            app_repo: ApplicationRepository instance
            job_repo: JobPostingRepository instance
            interview_repo: InterviewRepository instance for creating Interview records
            interview_engine: InterviewEngine instance for creating interview sessions
        """
        self.app_repo = app_repo
        self.job_repo = job_repo
        self.interview_repo = interview_repo
        self.interview_engine = interview_engine
        self.logger = structlog.get_logger().bind(service="application_service")

    async def create_application(
        self, candidate_id: UUID, job_posting_id: UUID
    ) -> tuple[Application, InterviewSession]:
        """
        Create a new application and automatically start interview.

        Creates application record, validates job posting is active,
        checks for duplicates, then automatically creates and links
        interview session. All operations are atomic within a transaction.

        Args:
            candidate_id: UUID of the candidate applying
            job_posting_id: UUID of the job posting to apply to

        Returns:
            Tuple of (Application, InterviewSession) both fully populated

        Raises:
            HTTPException 404: If job posting not found
            HTTPException 400: If job posting is not active
            HTTPException 409: If candidate already applied to this job
            HTTPException 500: If interview creation fails
        """
        self.logger.info(
            "creating_application",
            candidate_id=str(candidate_id),
            job_posting_id=str(job_posting_id),
        )

        try:
            # Step 1: Validate job posting exists and is active
            job_posting = await self.job_repo.get_by_id(job_posting_id)
            if not job_posting:
                self.logger.warning(
                    "job_posting_not_found", job_posting_id=str(job_posting_id)
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job posting {job_posting_id} not found",
                )

            if job_posting.status != "active":
                self.logger.warning(
                    "job_posting_not_active",
                    job_posting_id=str(job_posting_id),
                    status=job_posting.status,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job posting is not accepting applications",
                )

            # Step 2: Check for duplicate application
            existing = await self.app_repo.check_existing_application(
                candidate_id, job_posting_id
            )
            if existing:
                self.logger.warning(
                    "duplicate_application",
                    candidate_id=str(candidate_id),
                    job_posting_id=str(job_posting_id),
                    existing_id=str(existing.id),
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Already applied to this job",
                )

            # Step 3: Create application record
            application = Application(
                candidate_id=candidate_id,
                job_posting_id=job_posting_id,
                status="applied",
            )
            application = await self.app_repo.create(application)
            self.logger.info("application_created", application_id=str(application.id))

            # Step 4: Create interview record first
            try:
                # Map tech_stack/role_category to interview role_type enum
                # Priority: tech_stack first, then role_category, then default to 'fullstack'
                role_type_raw = job_posting.tech_stack or str(job_posting.role_category)
                
                # Expanded role mapping for technical AND non-technical roles
                # Maps to valid enum values: react, python, javascript, fullstack
                role_type_mapping = {
                    # Existing technical mappings
                    "react": "react",
                    "python": "python",
                    "javascript": "javascript",
                    
                    # New technical mappings
                    "typescript": "javascript",  # TypeScript uses JS base
                    "go": "python",              # Backend/systems
                    "rust": "python",            # Systems programming
                    "java": "python",            # OOP/backend
                    "csharp": "python",          # .NET/backend
                    "c#": "python",
                    "dotnet": "python",
                    ".net": "python",
                    "php": "python",             # Backend scripting
                    "node": "javascript",
                    "nodejs": "javascript",
                    "node.js": "javascript",
                    "data": "python",            # Data engineering
                    "data_engineering": "python",
                    "data engineering": "python",
                    "devops": "python",          # Ops/scripting
                    "qa": "javascript",          # Testing/automation
                    "qa_automation": "javascript",
                    "quality_assurance": "javascript",
                    "playwright": "javascript",
                    "cypress": "javascript",
                    
                    # Non-technical role mappings (by role_category)
                    # These use 'fullstack' as base, but job context makes them specific
                    "sales": "fullstack",
                    "account_manager": "fullstack",
                    "account manager": "fullstack",
                    "business_development": "fullstack",
                    "business development": "fullstack",
                    "support": "fullstack",
                    "customer_service": "fullstack",
                    "customer service": "fullstack",
                    "customer_success": "fullstack",
                    "customer success": "fullstack",
                    "product": "fullstack",
                    "product_manager": "fullstack",
                    "product manager": "fullstack",
                    "design": "fullstack",
                    "ux": "fullstack",
                    "ui": "fullstack",
                    "ux/ui": "fullstack",
                    "marketing": "fullstack",
                    "operations": "fullstack",
                    "management": "fullstack",
                    
                    # Default
                    "fullstack": "fullstack",
                    "full-stack": "fullstack",
                    "full stack": "fullstack",
                }
                role_type = role_type_mapping.get(role_type_raw.lower(), "fullstack")
                
                self.logger.info(
                    "role_type_mapping",
                    tech_stack=job_posting.tech_stack,
                    role_category=str(job_posting.role_category),
                    mapped_role_type=role_type,
                )

                # Create Interview record with job_posting_id for context
                interview = Interview(
                    candidate_id=candidate_id,
                    role_type=role_type,
                    job_posting_id=job_posting_id,  # NEW: Store for job context
                    status="in_progress",
                )
                interview = await self.interview_repo.create(interview)
                self.logger.info(
                    "interview_record_created",
                    interview_id=str(interview.id),
                    role_type=role_type,
                )

                # Create InterviewSession manually with correct interview_id
                from datetime import datetime
                interview_session = InterviewSession(
                    interview_id=interview.id,  # Use actual interview ID
                    current_difficulty_level="warmup",
                    questions_asked_count=0,
                    skill_boundaries_identified={},
                    progression_state={
                        "use_realtime": True,
                        "phase_history": [
                            {
                                "phase": "warmup",
                                "started_at": datetime.utcnow().isoformat(),
                                "questions_count": 0
                            }
                        ],
                        "response_quality_history": [],
                        "skills_explored": [],
                        "skills_pending": [],
                        "boundary_detections": []
                    },
                    conversation_memory={
                        "messages": [],
                        "memory_metadata": {
                            "created_at": datetime.utcnow().isoformat(),
                            "last_updated": datetime.utcnow().isoformat(),
                            "message_count": 0,
                            "truncation_count": 0
                        }
                    },
                    last_activity_at=datetime.utcnow()
                )
                interview_session = await self.interview_engine.session_repo.create(interview_session)

                self.logger.info(
                    "interview_session_created",
                    interview_id=str(interview.id),
                    session_id=str(interview_session.id),
                    role_type=role_type,
                )
            except Exception as e:
                self.logger.error(
                    "interview_creation_failed",
                    application_id=str(application.id),
                    error=str(e),
                )
                # Let transaction rollback - application will not be saved
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create interview session",
                ) from e

            # Step 5: Link interview to application
            application = await self.app_repo.link_interview(
                application.id, interview.id
            )
            self.logger.info(
                "interview_linked",
                application_id=str(application.id),
                interview_id=str(interview.id),
            )

            # Step 6: Transaction will commit when endpoint returns
            self.logger.info(
                "application_completed",
                application_id=str(application.id),
                interview_id=str(interview.id),
                status=application.status,
            )

            return application, interview_session

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            self.logger.error(
                "application_creation_failed",
                candidate_id=str(candidate_id),
                job_posting_id=str(job_posting_id),
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create application",
            ) from e

    async def get_candidate_applications(
        self, candidate_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Application]:
        """
        Get all applications for a candidate with pagination.

        Returns applications with eager-loaded relationships
        (job_posting, interview).

        Args:
            candidate_id: UUID of the candidate
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)

        Returns:
            List of Application instances with relationships loaded
        """
        self.logger.info(
            "fetching_candidate_applications",
            candidate_id=str(candidate_id),
            skip=skip,
            limit=limit,
        )

        applications = await self.app_repo.get_by_candidate_id(
            candidate_id, skip=skip, limit=limit
        )

        self.logger.info(
            "candidate_applications_fetched",
            candidate_id=str(candidate_id),
            count=len(applications),
        )

        return applications

    async def get_application_by_id(
        self, application_id: UUID, candidate_id: UUID
    ) -> Application:
        """
        Get application by ID with authorization check.

        Verifies that the application belongs to the specified candidate.

        Args:
            application_id: UUID of the application
            candidate_id: UUID of the candidate (for authorization)

        Returns:
            Application instance

        Raises:
            HTTPException 404: If application not found
            HTTPException 403: If application doesn't belong to candidate
        """
        self.logger.info(
            "fetching_application",
            application_id=str(application_id),
            candidate_id=str(candidate_id),
        )

        application = await self.app_repo.get_by_id(application_id)

        if not application:
            self.logger.warning(
                "application_not_found", application_id=str(application_id)
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        # Authorization check
        if application.candidate_id != candidate_id:
            self.logger.warning(
                "unauthorized_application_access",
                application_id=str(application_id),
                candidate_id=str(candidate_id),
                application_candidate_id=str(application.candidate_id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this application",
            )

        return application
