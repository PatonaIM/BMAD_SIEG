# Job-Driven AI Interview Flow - Brownfield Enhancement PRD

## Document Information

**Status:** Draft  
**Version:** 1.0  
**Created:** November 4, 2025  
**Last Updated:** November 4, 2025  
**Epic:** Epic 03

---

## 1. Intro Project Analysis and Context

### 1.1 Analysis Source

**IDE-based fresh analysis** - Working directly with loaded project in IDE

### 1.2 Current Project State

**Teamified Candidates Portal** is an AI-powered recruitment platform that enables candidates to undergo technical assessments through conversational AI interviews. Currently supports:

- **Core Functionality:**
  - Candidate registration and authentication
  - Resume upload and parsing (backend models exist)
  - AI-powered technical interviews with speech-to-speech capability
  - Progressive assessment engine (warmup → standard → advanced questions)
  - Support for multiple technical roles: React, Python, JavaScript, Fullstack
  - Real-time conversation flow with OpenAI GPT-4
  - Interview completion with basic results

- **Current Limitations:**
  - Job postings are **hard-coded** in frontend components
  - No database-driven job posting system
  - Applications are **mocked data** only
  - AI interviews default to "React" role type
  - No connection between job applications and interview customization

### 1.3 Available Documentation

✅ **Complete Documentation Available:**
- ✅ Tech Stack Documentation (FastAPI backend, Next.js frontend, PostgreSQL)
- ✅ Source Tree/Architecture (monorepo structure documented)
- ✅ Coding Standards (Python, TypeScript, SQLAlchemy patterns)
- ✅ API Documentation (Interview APIs, Authentication)
- ✅ Database Schema (Candidates, Interviews, InterviewMessages, etc.)
- ✅ External API Documentation (OpenAI integration)
- ⚠️ UX/UI Guidelines (Partial - shadcn/ui components, no formal design system)
- ✅ Technical Debt Documentation (Epic stories include QA results)

### 1.4 Enhancement Scope

**Enhancement Type:**
- ✅ **New Feature Addition** - Job posting browsing and application system
- ✅ **Integration with New Systems** - Linking applications to AI interviews
- ⚠️ **Moderate to Significant Impact** - New database tables, API endpoints, frontend pages updated

**Enhancement Description:**

Transform the platform from a standalone AI interview demo into a complete candidate-driven job application system where candidates can browse real job postings from the database, apply to positions, and immediately begin customized AI interviews tailored to the specific job requirements and role type.

**Impact Assessment:**
- ✅ **Moderate Impact** - New tables/models, but existing interview system largely intact
- Database: New tables for `job_postings` and `applications`
- Backend: New repositories, services, and API endpoints
- Frontend: Update existing pages to fetch from APIs instead of using mock data
- Interview Engine: Enhance to accept job context for customization

### 1.5 Goals and Background Context

**Goals:**
- Enable candidates to browse and search real job postings stored in the database
- Allow candidates to apply to job postings with a streamlined application flow
- Automatically trigger AI interviews customized to the job's role type and requirements
- Create a cohesive candidate journey: Browse → Apply → Interview → Results
- Generate comprehensive seed data with realistic job postings for development and demo

**Background Context:**

The current system demonstrates powerful AI interview capabilities but operates in isolation without a job context. Candidates currently see hard-coded job listings that don't connect to the interview experience. This enhancement bridges that gap by implementing a database-driven job posting system that serves as the entry point for the candidate journey. When a candidate applies to a job, the system will immediately launch an AI interview customized to that specific role (React, Python, JavaScript, or Fullstack), creating a seamless and contextually relevant assessment experience.

### 1.6 Change Log

| Change | Date | Version | Description | Author |
|--------|------|---------|-------------|--------|
| Initial draft | 2025-11-04 | 1.0 | Created brownfield PRD for job-driven interview flow | PM Agent |

---

## 2. Requirements

### 2.1 Functional Requirements

**FR1:** The system shall store job postings in the database with fields including title, company, description, role_type (react|python|javascript|fullstack), location, job_type, salary_range, required_skills (JSONB), experience_level, and status.

**FR2:** The system shall provide a REST API endpoint for candidates to retrieve a paginated list of active job postings with filtering by role_type, location, job_type, and experience_level.

**FR3:** The system shall provide a REST API endpoint for candidates to retrieve detailed information about a specific job posting by ID.

**FR4:** The system shall allow authenticated candidates to submit applications to job postings, creating an `applications` record linking candidate_id to job_posting_id.

**FR5:** Upon successful application submission, the system shall automatically create and start an AI interview with the role_type matching the job posting's role_type.

**FR6:** The system shall link the created interview to the application record via interview_id foreign key.

**FR7:** The system shall update the application status to "interview_scheduled" when the AI interview is created.

**FR8:** The system shall prevent duplicate applications by checking if a candidate has already applied to the same job posting.

**FR9:** The system shall provide a REST API endpoint for candidates to retrieve their own application history with status tracking.

**FR10:** The frontend job browsing page (`/jobs`) shall fetch job postings from the backend API instead of using hard-coded data.

**FR11:** The frontend dashboard (`/dashboard`) shall fetch matched jobs and recent applications from the backend API.

**FR12:** The frontend applications page (`/applications`) shall display real application data with current status and linked interview information.

**FR13:** The system shall generate comprehensive seed data including at least 20 diverse job postings across all role types for development and demonstration purposes.

**FR14:** The interview start endpoint shall accept an optional `application_id` parameter to customize interview questions based on job requirements.

**FR15:** The system shall maintain backward compatibility allowing interviews to be started without an application_id for practice/standalone assessments.

**FR16:** The frontend shall display "View Interview Results" link from applications page when interview is completed.

### 2.2 Non-Functional Requirements

**NFR1:** API endpoints shall return responses within 200ms for list operations and 100ms for single-record retrievals under normal load.

**NFR2:** The database schema shall use proper indexes on foreign keys (candidate_id, job_posting_id, interview_id) and frequently queried fields (role_type, status, posted_at).

**NFR3:** Job posting search and filter operations shall remain performant with up to 10,000 job postings in the database.

**NFR4:** The enhancement shall maintain the existing authentication and authorization patterns without introducing new security vulnerabilities.

**NFR5:** All new API endpoints shall follow RESTful conventions and the existing FastAPI patterns (Pydantic schemas, dependency injection, error handling).

**NFR6:** Frontend components shall maintain the existing UI/UX patterns using shadcn/ui components and Tailwind CSS.

**NFR7:** The system shall handle concurrent application submissions gracefully with proper transaction isolation to prevent race conditions.

**NFR8:** Database migrations shall be reversible (up/down) and tested for both fresh installations and existing databases.

**NFR9:** Frontend pages shall implement skeleton loaders for initial page load to improve perceived performance.

**NFR10:** The seed data generation script shall be idempotent, allowing safe re-execution without creating duplicate records.

### 2.3 Compatibility Requirements

**CR1: Existing Interview API Compatibility** - The interview creation endpoint (`POST /api/v1/interviews/start`) shall maintain its current interface while accepting an optional `application_id` parameter, ensuring existing interview functionality remains unaffected.

**CR2: Database Schema Compatibility** - New tables (`job_postings`, `applications`) shall integrate seamlessly with existing schema without modifying existing tables (candidates, interviews, interview_messages, interview_sessions, resumes, assessment_results).

**CR3: UI/UX Consistency** - All updated frontend pages shall maintain visual consistency with existing components, color schemes, typography, and interaction patterns established in the current application.

**CR4: Integration Compatibility** - The OpenAI interview engine integration shall remain unchanged; job context will be passed as additional metadata without altering the core conversation flow or progressive assessment logic.

---

## 3. User Interface Enhancement Goals

### 3.1 Integration with Existing UI

The enhancement will integrate seamlessly with the existing Next.js frontend architecture and shadcn/ui component library:

**Component Reuse:**
- Leverage existing `Card`, `Button`, `Badge`, `Input`, `Select` components from shadcn/ui
- Maintain current layout patterns using `AuthenticatedLayout` wrapper
- Preserve existing color scheme (primary, accent, muted-foreground)
- Continue using Lucide React icons for consistency

**State Management:**
- Follow existing patterns using React hooks (`useState`, `useEffect`)
- Use existing `useAuthStore` for candidate authentication
- Implement new custom hooks following established patterns: `useJobPostings`, `useApplications`, `useApplyToJob`
- Maintain error handling patterns with inline error displays

**Routing Integration:**
- Update existing routes: `/jobs`, `/dashboard`, `/applications`
- Maintain existing navigation structure in `AuthenticatedLayout`
- No new top-level routes required (all updates to existing pages)

**API Integration:**
- Follow existing API service patterns
- Use consistent error handling and loading states
- Maintain existing authentication header injection patterns

### 3.2 Modified/New Screens and Views

**Modified Screens:**

1. **`/jobs` (Browse Jobs Page)** - Currently displays hard-coded jobs
   - **Changes:** Replace mock data with API call to `GET /api/v1/job-postings`
   - **New functionality:** Real-time filtering, search, pagination, skeleton loaders
   - **Preserved:** Existing card layout, filter UI, job detail display

2. **`/jobs/{id}` (Job Detail Page)** - Currently uses hard-coded data
   - **Changes:** Fetch from `GET /api/v1/job-postings/{id}`
   - **New functionality:** "Apply Now" button triggers application flow
   - **Preserved:** Existing layout and information architecture

3. **`/dashboard` (Dashboard Page)** - Currently shows mock applications and matched jobs
   - **Changes:** Replace "Recent Applications" section with `GET /api/v1/applications/me`
   - **Changes:** Replace "Matched Jobs" section with `GET /api/v1/job-postings?matched=true`
   - **Preserved:** Stats cards, layout structure, quick action cards

4. **`/applications` (Applications Page)** - Currently entirely mock data
   - **Changes:** Complete replacement with real data from API
   - **New functionality:** Status tracking, linked interview access, application history filtering, "View Interview Results" link, skeleton loaders
   - **Preserved:** Tab-based filtering UI, status badges, card layout

5. **`/interview/start` (Interview Start Page)** - Currently hard-codes role_type="react"
   - **Changes:** Accept `application_id` from query params
   - **Changes:** Display job context when starting from application
   - **Preserved:** Interview preparation UI, feature highlights, begin button

**No New Pages Required** - All functionality fits within existing page structure.

### 3.3 UI Consistency Requirements

**Visual Consistency:**
- **UC1:** All new API-driven components shall use the same Card, Button, Badge, and typography styles as existing hard-coded components
- **UC2:** Job posting cards shall maintain identical visual structure whether populated from mock data or API data
- **UC3:** Skeleton loaders shall match the shape and layout of the content they represent
- **UC4:** Error states shall follow existing error message styling and placement

**Interaction Consistency:**
- **UC5:** Application submission flow shall follow existing form submission patterns (loading states, success feedback, error handling)
- **UC6:** Navigation between job browsing, application, and interview shall maintain existing routing behavior
- **UC7:** Filter and search interactions shall match existing input component behavior

**Data Display Consistency:**
- **UC8:** Date formatting shall use consistent format across all pages (e.g., "2 days ago" vs "Jan 15, 2024")
- **UC9:** Salary ranges, locations, and job types shall display in identical format to current mock data
- **UC10:** Status badges (applied, interview_scheduled, under_review, etc.) shall use the same color coding as existing components

---

## 4. Technical Constraints and Integration Requirements

### 4.1 Existing Technology Stack

**Languages:**
- Python 3.11+ (Backend)
- TypeScript 5.x (Frontend)

**Frameworks:**
- **Backend:** FastAPI 0.104+, SQLAlchemy 2.x ORM, Alembic (migrations), Pydantic v2 (schemas)
- **Frontend:** Next.js 14+ (App Router), React 18+, shadcn/ui components, Tailwind CSS

**Database:**
- PostgreSQL 15+ (via Supabase)
- JSONB columns for flexible data (skills, metadata)
- UUID primary keys with proper indexing

**Infrastructure:**
- Development: Local PostgreSQL (port 5432)
- API: FastAPI uvicorn server
- Frontend: Next.js dev server

**External Dependencies:**
- OpenAI API (GPT-4, Whisper STT, TTS)
- LangChain for conversation management
- Authentication: JWT tokens (existing implementation)

### 4.2 Integration Approach

**Database Integration Strategy:**
```
# New tables integrate with existing schema via foreign keys
# No modifications to existing tables

job_postings (new table)
  ├─ Independent table, no FK to existing schema
  └─ Referenced by: applications.job_posting_id

applications (new table)
  ├─ FK: candidate_id → candidates.id
  ├─ FK: job_posting_id → job_postings.id
  └─ FK: interview_id → interviews.id (nullable, set after interview creation)

interviews (existing table - no modifications needed)
  └─ Referenced by: applications.interview_id
```

**Migration Strategy:**
- Create new Alembic migration: `add_job_postings_and_applications`
- Use proper CASCADE/SET NULL for foreign key constraints
- Include rollback for testing
- Seed data as separate script (not in migration)

**API Integration Strategy:**
```
New Endpoints (RESTful):
  GET    /api/v1/job-postings              (list with filters)
  GET    /api/v1/job-postings/{id}         (single job detail)
  POST   /api/v1/applications               (apply to job)
  GET    /api/v1/applications/me            (candidate's applications)
  GET    /api/v1/applications/{id}          (single application detail)

Enhanced Endpoint:
  POST   /api/v1/interviews/start           (add optional application_id)

Existing Endpoints (unchanged):
  All interview endpoints remain compatible
```

**Repository Pattern:**
```python
# Follow existing patterns
backend/app/repositories/
  ├─ job_posting_repository.py    (new)
  ├─ application_repository.py    (new)
  └─ interview_repository.py      (existing - minor updates)

backend/app/services/
  ├─ job_posting_service.py       (new)
  ├─ application_service.py       (new)
  └─ interview_service.py         (existing - enhanced)
```

**Frontend Integration Strategy:**
```typescript
// API client pattern (following existing)
frontend/lib/api/
  ├─ jobPostings.ts               (new)
  ├─ applications.ts              (new)
  └─ interviews.ts                (existing)

// Custom hooks
frontend/hooks/
  ├─ useJobPostings.ts            (new)
  ├─ useApplyToJob.ts             (new)
  ├─ useApplications.ts           (new)
  └─ useStartInterview.ts         (existing - may enhance)

// Updated pages consume new hooks
frontend/app/
  ├─ jobs/page.tsx                (update to use API)
  ├─ dashboard/page.tsx           (update to use API)
  ├─ applications/page.tsx        (update to use API)
  └─ interview/start/page.tsx     (enhance for job context)
```

**Testing Integration Strategy:**
- Manual testing focus for this enhancement
- Follow existing patterns if automated tests are added later

### 4.3 Code Organization and Standards

**File Structure Approach:**
```
backend/app/
  models/
    ├─ job_posting.py              # New model
    ├─ application.py              # New model
    └─ interview.py                # Existing (no modifications)
  
  schemas/
    ├─ job_posting.py              # New Pydantic schemas
    ├─ application.py              # New Pydantic schemas
    └─ interview.py                # Existing (add optional fields)
  
  repositories/
    ├─ job_posting_repository.py   # New CRUD operations
    └─ application_repository.py   # New CRUD operations
  
  services/
    ├─ job_posting_service.py      # New business logic
    └─ application_service.py      # New business logic + interview trigger
  
  api/v1/
    ├─ job_postings.py             # New router
    └─ applications.py             # New router

backend/alembic/versions/
  └─ YYYYMMDD_add_job_postings_and_applications.py

backend/scripts/
  └─ seed_job_postings.py          # New seed data script
```

**Naming Conventions:**
- Models: PascalCase (`JobPosting`, `Application`)
- Tables: snake_case (`job_postings`, `applications`)
- Endpoints: kebab-case (`/job-postings`, `/applications`)
- Functions: snake_case (`get_job_posting`, `create_application`)

**Coding Standards:**
- SQLAlchemy models: Type hints, proper relationships, `__repr__`
- Pydantic schemas: Request/Response separation, examples in docstrings
- FastAPI routes: Dependency injection, proper HTTP status codes
- TypeScript: Strict mode, explicit return types, proper error handling

**Documentation Standards:**
- Docstrings for all public functions (Google style)
- API endpoint descriptions in Pydantic schema examples
- README updates for new seed script usage
- Inline comments for complex business logic (application → interview flow)

### 4.4 Deployment and Operations

**Build Process Integration:**
- No changes to existing build process
- Backend: `pip install` includes no new dependencies
- Frontend: Next.js build remains unchanged
- Migration runs before server start (existing pattern)

**Deployment Strategy:**
- Run Alembic migration: `alembic upgrade head`
- Run seed script: `uv run python backend/scripts/seed_job_postings.py`
- Restart backend server
- Frontend: Standard Next.js build and deploy

**Monitoring and Logging:**
- Use existing FastAPI logging patterns
- Log application submissions and interview creations
- Monitor new endpoint performance (response times)
- Track application → interview conversion rate

**Configuration Management:**
- No new environment variables required
- Use existing DATABASE_URL, API_KEY patterns
- Seed script uses same database connection

### 4.5 Risk Assessment and Mitigation

**Technical Risks:**
- **Risk:** Foreign key constraints may cause issues if interview creation fails after application is created
  - **Mitigation:** Use database transactions, set interview_id only after successful interview creation
  
- **Risk:** Migration may fail on existing production data
  - **Mitigation:** Test migration on copy of production database, implement proper rollback

- **Risk:** Concurrent applications to same job may cause race conditions
  - **Mitigation:** Use database-level unique constraint on (candidate_id, job_posting_id), handle duplicate key errors gracefully

**Integration Risks:**
- **Risk:** Interview engine may not handle optional job context gracefully
  - **Mitigation:** Make application_id truly optional, maintain backward compatibility, test both paths

- **Risk:** Frontend API calls may timeout with large job posting lists
  - **Mitigation:** Implement pagination (limit 20-50 per page), add proper loading states

- **Risk:** Seed data may conflict with existing test data
  - **Mitigation:** Make seed script idempotent with upsert logic or clear warnings

**Deployment Risks:**
- **Risk:** Migration downtime during deployment
  - **Mitigation:** Migrations are additive (no breaking changes), can run with zero downtime

- **Risk:** Frontend may fail if backend not updated first
  - **Mitigation:** Deploy backend first, then frontend; maintain API compatibility

**Mitigation Strategies:**
1. **Phased Rollout:** Backend APIs → Frontend updates per page → Seed data
2. **Feature Flags:** (Optional) Environment variable to toggle new job system vs. mock data
3. **Comprehensive Testing:** Manual testing for entire application flow before production
4. **Rollback Plan:** Alembic downgrade script tested, frontend can revert to mock data if needed

---

## 5. Epic and Story Structure

### 5.1 Epic Approach

**Epic Structure Decision:** **Single Comprehensive Epic (Epic 03)**

**Rationale:**
This enhancement represents one cohesive user journey (Browse Jobs → Apply → AI Interview) with tightly coupled components that must work together to deliver value. Breaking it into multiple epics would create artificial boundaries and deployment dependencies. The work naturally sequences as:

1. Database foundation (models, migrations)
2. Backend services and APIs
3. Frontend integration
4. Seed data for realistic demo

All stories are interdependent and share a common goal: enabling candidates to apply to real jobs and receive customized AI interviews. A single epic ensures clear ownership, coordinated delivery, and atomic feature completion.

---

## 6. Epic 03: Job-Driven AI Interview Flow

**Epic Goal:** Enable candidates to browse database-driven job postings, apply with one click, and immediately begin AI interviews customized to the specific job's role type and requirements.

**Integration Requirements:**
- New `job_postings` and `applications` tables integrate via foreign keys with existing `candidates` and `interviews` tables
- Backend APIs follow existing FastAPI + SQLAlchemy patterns
- Frontend pages updated to consume APIs while maintaining UI/UX consistency
- Interview engine enhanced to accept job context without breaking existing functionality
- Seed data script provides realistic job postings for development and demo

---

### Story 3.1: Job Posting Data Models and Database Schema

**As a** developer,  
**I want** database tables for job postings and applications with proper relationships to candidates and interviews,  
**so that** the system can store and retrieve job data for the candidate application flow.

**Acceptance Criteria:**

1. `job_postings` table created with fields: id (UUID), title, company, description, role_type (enum: react|python|javascript|fullstack), location, job_type, salary_range, required_skills (JSONB), experience_level, status (default 'active'), posted_at, created_at, updated_at
2. `applications` table created with fields: id (UUID), candidate_id (FK), job_posting_id (FK), status (enum: applied|interview_scheduled|interview_completed|under_review|rejected|offered), applied_at, interview_id (FK, nullable), created_at, updated_at
3. SQLAlchemy models created: `JobPosting` and `Application` following existing coding standards
4. Alembic migration created with proper up/down functions
5. Foreign key indexes created on candidate_id, job_posting_id, interview_id
6. Unique constraint on (candidate_id, job_posting_id) to prevent duplicate applications
7. Migration tested: can apply to fresh database and existing database, can rollback cleanly

**Integration Verification:**

**IV1: Existing Schema Integrity** - Run migration on copy of existing database, verify all existing tables and relationships remain intact, no data loss occurs

**IV2: Foreign Key Constraints** - Verify CASCADE and SET NULL behaviors work correctly when deleting candidates or interviews

**IV3: Enum Compatibility** - Confirm role_type enum matches existing interview role_type enum values exactly

---

### Story 3.2: Job Posting Repository and Service Layer

**As a** developer,  
**I want** repository and service classes for job posting operations,  
**so that** the API layer has clean business logic for managing job postings.

**Acceptance Criteria:**

1. `JobPostingRepository` created with methods: get_by_id, get_all, get_active, filter_by_role_type, filter_by_location
2. `JobPostingService` created with business logic for retrieving and filtering job postings
3. Pagination support implemented (default limit 20, max 100)
4. Filter support for: role_type, location, job_type, experience_level
5. Search support for title and company (case-insensitive)
6. Service follows existing dependency injection patterns
7. Code follows existing repository/service patterns from interview system

**Integration Verification:**

**IV1: Database Connection Pooling** - Verify new repository uses existing database session management without creating additional connections

**IV2: Error Handling Consistency** - Confirm service layer error handling matches existing patterns (HTTPException, proper status codes)

**IV3: Query Performance** - Verify queries execute within 200ms for lists of 100+ job postings

---

### Story 3.3: Application Repository and Service Layer

**As a** developer,  
**I want** repository and service classes for application operations including interview triggering,  
**so that** candidates can apply to jobs and automatically start customized interviews.

**Acceptance Criteria:**

1. `ApplicationRepository` created with methods: create, get_by_id, get_by_candidate_id, get_by_job_posting_id, update_status
2. `ApplicationService` created with business logic including duplicate detection and interview triggering
3. `create_application` method checks for existing application and returns appropriate error
4. Upon successful application creation, service automatically calls interview service to create interview
5. Interview created with role_type matching job_posting.role_type
6. Application.interview_id updated after interview creation
7. Application status updated to 'interview_scheduled' after interview link
8. Transaction handling ensures atomicity (rollback if interview creation fails)

**Integration Verification:**

**IV1: Interview Service Integration** - Verify new application service can call existing interview service without modifications to interview service core logic

**IV2: Transaction Rollback** - Simulate interview creation failure, verify application is rolled back and database remains consistent

**IV3: Existing Interview Functionality** - Confirm interviews can still be created independently (without applications) for practice mode

---

### Story 3.4: Job Posting REST API Endpoints

**As a** frontend developer,  
**I want** REST API endpoints for browsing and retrieving job postings,  
**so that** the frontend can display real job data instead of mock data.

**Acceptance Criteria:**

1. `GET /api/v1/job-postings` endpoint created with query params: role_type, location, job_type, experience_level, search, skip, limit
2. `GET /api/v1/job-postings/{id}` endpoint created for single job retrieval
3. Pydantic request/response schemas created: `JobPostingListResponse`, `JobPostingDetailResponse`, `JobPostingFilters`
4. Endpoints return proper HTTP status codes (200, 404, 422)
5. Response includes pagination metadata (total, skip, limit)
6. OpenAPI/Swagger documentation auto-generated with examples
7. Endpoints do not require authentication (public job browsing)

**Integration Verification:**

**IV1: FastAPI Router Integration** - Verify new router integrates with existing app router structure without conflicts

**IV2: CORS Configuration** - Confirm frontend can call new endpoints without CORS issues

**IV3: Response Schema Consistency** - Verify response format matches existing API patterns (camelCase/snake_case consistency)

---

### Story 3.5: Application REST API Endpoints

**As a** authenticated candidate,  
**I want** REST API endpoints to submit applications and view my application history,  
**so that** I can apply to jobs and track my application status.

**Acceptance Criteria:**

1. `POST /api/v1/applications` endpoint created (authenticated) with body: job_posting_id
2. `GET /api/v1/applications/me` endpoint created (authenticated) returning candidate's applications
3. `GET /api/v1/applications/{id}` endpoint created (authenticated) for single application detail
4. Pydantic schemas created: `ApplicationCreateRequest`, `ApplicationResponse`, `ApplicationDetailResponse`
5. POST endpoint validates job_posting exists and is active
6. POST endpoint returns 409 Conflict if duplicate application
7. Endpoints require authentication (JWT token validation using existing auth)
8. GET /me endpoint includes job_posting details and interview status

**Integration Verification:**

**IV1: Authentication Middleware** - Verify new endpoints use existing JWT auth dependency without modifications

**IV2: Authorization** - Confirm candidates can only access their own applications (not other candidates')

**IV3: Interview Data Inclusion** - Verify response includes interview status when interview_id is set

---

### Story 3.13: Dynamic Tech-Stack Interview System

**As a** candidate applying to a job with a specific tech stack (e.g., Go, TypeScript, Rust),  
**I want** the AI interview to ask relevant questions for that technology,  
**So that** I can demonstrate my actual skills rather than being assessed on unrelated technologies.

**Acceptance Criteria:**

1. `interviews.role_type` column migrated from enum to VARCHAR(100) to accept any tech stack
2. Dynamic prompt system loads appropriate interview questions based on tech_stack value
3. Interview prompts created for at least 10 common tech stacks: React, Python, JavaScript, TypeScript, Go, Rust, Java, PHP, Node.js, Playwright
4. Fallback "general_technical" prompt used when tech_stack is unknown or NULL
5. Application service passes job_posting.tech_stack to interview creation
6. Interview service maps tech_stack to appropriate prompt template
7. Existing interviews with old role_type enum values ('react', 'python', 'javascript', 'fullstack') continue to work unchanged
8. New interview creation accepts any tech_stack string value
9. Interview API endpoints remain unchanged (backward compatible)
10. Progressive assessment engine continues to work with new prompt system

**Integration Verification:**

**IV1: Existing Interview Compatibility** - Query existing interviews with old role_type values, start sessions, verify prompts load correctly and interviews complete without errors

**IV2: Dynamic Prompt Loading** - Create interviews with 5+ different tech_stacks, verify correct prompt file is loaded for each, test with unknown tech_stack to verify fallback prompt loads

**IV3: Application → Interview Integration** - Create job posting with specific tech_stack, submit application, verify interview created with matching role_type, start interview and verify correct tech-specific questions appear

---

### Story 3.6: Enhanced Interview Start Endpoint

**As a** candidate applying to a job,  
**I want** the interview system to know which job I'm applying for,  
**so that** the AI interview is customized to the job's requirements and tech stack.

**Acceptance Criteria:**

1. `POST /api/v1/interviews/start` endpoint enhanced to accept optional `application_id` field
2. Pydantic schema `InterviewStartRequest` updated with optional application_id (UUID)
3. When application_id provided, interview fetches job_posting via application relationship
4. Interview.role_type set to match job_posting.tech_stack (using dynamic interview system from Story 3.13)
5. Interview metadata includes job_posting_id for future customization
6. Endpoint maintains backward compatibility (works without application_id)
7. Service validates application belongs to authenticated candidate

**Integration Verification:**

**IV1: Existing Interview Flow** - Verify interviews started without application_id work exactly as before

**IV2: Dynamic Interview System** - Confirm tech_stack from job posting correctly loads appropriate interview prompt (Story 3.13 dependency)

**IV3: Interview Message Logging** - Verify interview messages are logged correctly for both job-linked and standalone interviews

---

### Story 3.7: Frontend Job Browsing Page Update

**As a** candidate,  
**I want** to browse real job postings from the database,  
**so that** I can find positions that match my skills and interests.

**Acceptance Criteria:**

1. `/jobs/page.tsx` updated to fetch data from `GET /api/v1/job-postings` API
2. Custom hook `useJobPostings` created for data fetching with loading/error states
3. Skeleton loaders implemented for initial page load
4. Filters (role_type, location, job_type, experience_level) connected to API query params
5. Search functionality connected to API search param
6. Pagination implemented (if more than 20 results)
7. Existing UI/UX preserved (card layout, badges, icons)
8. Error handling displays user-friendly messages

**Integration Verification:**

**IV1: Existing Navigation** - Verify navigation to/from jobs page works unchanged

**IV2: Filter State Management** - Confirm filter changes don't break other page functionality

**IV3: Visual Consistency** - Verify API-driven job cards look identical to previous mock data cards

---

### Story 3.8: Frontend Dashboard and Applications Page Update

**As a** authenticated candidate,  
**I want** to see my real application history and status on the dashboard and applications page,  
**so that** I can track my job search progress.

**Acceptance Criteria:**

1. `/dashboard/page.tsx` updated: "Recent Applications" section fetches from `GET /api/v1/applications/me`
2. `/applications/page.tsx` completely updated to use `GET /api/v1/applications/me`
3. Custom hook `useApplications` created for data fetching
4. Skeleton loaders implemented for initial load on both pages
5. Application status badges use existing color scheme
6. "View Interview Results" link added when interview_id exists and interview is completed
7. Link navigates to interview results page with interview_id
8. Empty state displayed when no applications exist
9. Error handling with user-friendly messages

**Integration Verification:**

**IV1: Dashboard Stats** - Verify dashboard stats cards still display correctly (may show 0 until applications made)

**IV2: Authentication Flow** - Confirm pages redirect to login if not authenticated

**IV3: Interview Results Link** - Verify link correctly navigates to existing interview results page

---

### Story 3.9: Frontend Application Submission Flow

**As a** authenticated candidate,  
**I want** to apply to a job posting with one click,  
**so that** I can quickly submit my application.

**Acceptance Criteria:**

1. `/jobs/[id]/page.tsx` (job detail page) displays "Apply Now" button for authenticated users
2. Custom hook `useApplyToJob` created for application submission
3. Button click calls `POST /api/v1/applications` with job_posting_id
4. Loading state displays during application submission
5. Success state shows confirmation message and updates button to "Applied"
6. Error handling for duplicate applications shows appropriate message ("Already applied")
7. Disabled state shown if already applied
8. Success state includes link/button to "Start Interview Now"

**Integration Verification:**

**IV1: Authentication Check** - Verify unauthenticated users see "Sign in to apply" instead of Apply button

**IV2: Application Submission** - Confirm application is created and linked to candidate correctly

**IV3: Navigation Consistency** - Verify browser back button works correctly after application submission

---

### Story 3.10: Frontend Interview Start with Job Context

**As a** candidate who has applied to a job,  
**I want** to start the AI interview directly from my application,  
**so that** I can seamlessly progress from application to assessment.

**Acceptance Criteria:**

1. `/interview/start/page.tsx` accepts `application_id` query parameter
2. When application_id present, page displays job context (title, company, role) 
3. Interview start page calls `POST /api/v1/interviews/start` with application_id
4. Success redirects to active interview session
5. Job context card shows role-specific preparation tips
6. Error handling for invalid/unauthorized application_id
7. Existing interview start flow (without application_id) remains functional

**Integration Verification:**

**IV1: Interview Start Flow** - Confirm interview starts with correct role_type from job

**IV2: Interview Session Creation** - Verify interview session and messages are created correctly

**IV3: Backward Compatibility** - Verify standalone interview start (without job) still works

---

### Story 3.11: Documentation Updates

**As a** developer,  
**I want** comprehensive documentation for the new job-driven interview flow,  
**so that** team members can understand and maintain the system.

**Acceptance Criteria:**

1. README.md updated with seed script usage: `uv run python backend/scripts/seed_job_postings.py`
2. Architecture documentation updated with new tables (job_postings, applications) and relationships
3. API documentation includes new endpoints with examples
4. Database schema diagram updated to show new tables and foreign keys
5. Developer setup guide includes steps for running seed script
6. Epic 03 added to epic index (docs/epics/00-index.md)
7. PRD added to PRD index (docs/prds/00-index.md)

**Integration Verification:**

**IV1: Documentation Accuracy** - Verify all documented commands and examples work as described

**IV2: Schema Diagrams** - Confirm updated diagrams accurately reflect database relationships

**IV3: API Documentation** - Verify OpenAPI/Swagger docs are accessible and accurate

---

### Story 3.12: Seed Data Generation Script

**As a** developer,  
**I want** a script to generate realistic job posting seed data,  
**so that** I can develop and demo the system with diverse job examples.

**Acceptance Criteria:**

1. Script created at `backend/scripts/seed_job_postings.py`
2. Script generates at least 20 diverse job postings across all role categories and multiple tech stacks
3. Job postings include realistic: titles, companies, descriptions, locations, salary ranges, required skills, tech_stack values
4. Script covers at least 10 different tech_stacks: React, Python, TypeScript, Go, Rust, Java, PHP, Node.js, Playwright, and others
5. Script is idempotent (can run multiple times safely with clear warnings or upsert logic)
6. Script uses existing database connection patterns
7. Script executed with: `uv run python backend/scripts/seed_job_postings.py`
8. Script outputs summary (e.g., "Created 20 job postings across 10 tech stacks")
8. Script includes variety in experience levels, locations, and salary ranges

**Integration Verification:**

**IV1: Database Connection** - Verify script uses same DATABASE_URL and connection patterns as main application

**IV2: Data Integrity** - Confirm seeded job postings don't conflict with any existing data or constraints

**IV3: Realistic Variety** - Verify job postings span different experience levels, locations, and salary ranges for good demo coverage

---

## 7. Success Metrics

**Development Success:**
- All 12 stories completed and manually tested
- Database migration runs successfully on fresh and existing databases
- Seed script generates 20+ diverse job postings
- Zero breaking changes to existing interview functionality

**User Experience Success:**
- Candidates can browse job postings with <2 second initial load
- Application submission to interview start takes <5 seconds
- UI remains visually consistent with existing design
- Zero authentication/authorization issues

**Technical Success:**
- API response times meet NFR1 requirements (<200ms list, <100ms single)
- Database queries remain performant with 100+ job postings
- Transaction handling prevents partial state (application without interview)
- Backward compatibility maintained for standalone interviews

---

## 8. Dependencies and Assumptions

**Dependencies:**
- Existing authentication system (JWT) is functional
- Existing interview service can accept role_type parameter
- Database connection pooling is properly configured
- Frontend build pipeline supports new API integrations

**Assumptions:**
- Job postings will be seeded manually via script (no recruiter portal yet)
- Resume/cover letter attachments are deferred to future enhancement
- Application flow is linear (apply → immediate interview, no scheduling)
- Candidates can only apply once per job posting
- Job postings remain active indefinitely (no expiration logic yet)

---

## 9. Future Enhancements (Out of Scope)

**Deferred for Future Epics:**
- Resume upload and attachment to applications
- Cover letter submission
- Custom application questions per job posting
- Job posting expiration and archiving
- Recruiter portal for job posting management
- Application scheduling (delay interview start)
- Multiple interview rounds per application
- Application withdrawal/cancellation
- Job posting analytics (views, applications per posting)
- Advanced job matching algorithms
- Email notifications for application status changes
- Real-time job posting updates (polling/websockets)
- Soft-delete for job postings

---

## Appendix

### A. Database Schema

```sql
-- New Tables

CREATE TABLE job_postings (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Basic Info
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,  -- The hiring company/client
    description TEXT,
    
    -- Job Classification
    role_category VARCHAR(50) NOT NULL 
        CHECK (role_category IN (
            'engineering',
            'quality_assurance',
            'data',
            'devops',
            'design',
            'product',
            'sales',
            'support',
            'operations',
            'management',
            'other'
        )),
    tech_stack VARCHAR(100),  -- Flexible field: 'React', 'Python', 'TypeScript', 'Playwright', etc.
    
    -- Employment Details
    employment_type VARCHAR(50) NOT NULL 
        CHECK (employment_type IN ('permanent', 'contract', 'part_time')),
    work_setup VARCHAR(50) 
        CHECK (work_setup IN ('remote', 'hybrid', 'onsite')),
    location VARCHAR(255),
    
    -- Compensation
    salary_min NUMERIC(10, 2),
    salary_max NUMERIC(10, 2),
    salary_currency VARCHAR(10) DEFAULT 'AUD',
    
    -- Requirements & Skills
    experience_level VARCHAR(50),
    required_skills JSONB,
    
    -- Status Management
    status VARCHAR(20) DEFAULT 'active' 
        CHECK (status IN ('active', 'paused', 'closed')),
    is_cancelled BOOLEAN DEFAULT false,
    cancellation_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_job_postings_role_category ON job_postings(role_category);
CREATE INDEX idx_job_postings_tech_stack ON job_postings(tech_stack) WHERE tech_stack IS NOT NULL;
CREATE INDEX idx_job_postings_status ON job_postings(status) WHERE status = 'active';
CREATE INDEX idx_job_postings_employment_type ON job_postings(employment_type);
CREATE INDEX idx_job_postings_created_at ON job_postings(created_at DESC);

CREATE TABLE applications (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Keys
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    interview_id UUID REFERENCES interviews(id) ON DELETE SET NULL,
    
    -- Application Status
    status VARCHAR(50) DEFAULT 'applied' 
        CHECK (status IN (
            'applied',
            'interview_scheduled',
            'interview_completed',
            'under_review',
            'rejected',
            'offered',
            'accepted',
            'withdrawn'
        )),
    
    -- Timestamps
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate applications
    CONSTRAINT uq_applications_candidate_job UNIQUE(candidate_id, job_posting_id)
);

-- Indexes for performance
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_applications_job_posting_id ON applications(job_posting_id);
CREATE INDEX idx_applications_interview_id ON applications(interview_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_applied_at ON applications(applied_at DESC);
```

### B. API Endpoint Reference

**Job Postings:**
- `GET /api/v1/job-postings` - List job postings with filters and pagination
- `GET /api/v1/job-postings/{id}` - Get single job posting detail

**Applications:**
- `POST /api/v1/applications` - Submit application (authenticated)
- `GET /api/v1/applications/me` - Get candidate's applications (authenticated)
- `GET /api/v1/applications/{id}` - Get single application detail (authenticated)

**Interviews (Enhanced):**
- `POST /api/v1/interviews/start` - Start interview with optional application_id (authenticated)

### C. Frontend Routes Updated

- `/jobs` - Browse jobs page (API integration)
- `/jobs/[id]` - Job detail page (API integration)
- `/dashboard` - Dashboard (API integration)
- `/applications` - Applications page (API integration)
- `/interview/start` - Interview start page (enhanced for job context)

---

**End of Document**
