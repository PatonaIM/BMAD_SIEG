# Intelligent Job Matching System - Brownfield Enhancement PRD

## Document Information

**Status:** Draft  
**Version:** 1.0  
**Created:** November 6, 2025  
**Last Updated:** November 6, 2025  
**Epic:** Epic 04

---

## 1. Intro Project Analysis and Context

### 1.1 Analysis Source

**IDE-based fresh analysis** - Working directly with loaded project in IDE with access to complete documentation from Epic 01-03

### 1.2 Current Project State

**Teamified Candidates Portal** is an AI-powered recruitment platform with progressive AI interview capabilities. Currently implemented:

- **Epic 01**: Foundation with authentication, database schema (candidates, resumes, interviews), and text-based AI interviews
- **Epic 02**: Video interview experience with camera capture, tech checks, and video recording
- **Epic 03**: Job-driven interview flow with database-backed job postings, applications, and job-contextualized interviews

**Current Gaps for Intelligent Matching:**
- Candidate profiles are minimal (email, name, phone only - no skills, preferences, experience tracking)
- Resume `parsed_data` JSONB field exists but is not populated or utilized
- Job recommendations in frontend (`/jobs/matches`) use hard-coded mock data
- No matching algorithm or scoring system
- No candidate skills inventory or preference system

### 1.3 Available Documentation

✅ **Complete Documentation Available:**
- ✅ Tech Stack Documentation (FastAPI, Next.js, PostgreSQL, OpenAI, Supabase)
- ✅ Source Tree/Architecture (monorepo with backend/, frontend/, docs/)
- ✅ Coding Standards (SQLAlchemy patterns, TypeScript standards, naming conventions)
- ✅ API Documentation (Auth, Interviews, Job Postings, Applications)
- ✅ Database Schema (Candidates, Resumes, Interviews, JobPostings, Applications)
- ✅ External API Documentation (OpenAI GPT-4, Whisper, TTS integration)
- ⚠️ UX/UI Guidelines (Partial - shadcn/ui components, Tailwind CSS, no formal design system)
- ✅ Epic/Story Documentation (Epic 01-03 completed with stories)

### 1.4 Enhancement Scope

**Enhancement Type:**
- ✅ **New Feature Addition** - AI-powered job matching and candidate profile system
- ✅ **Integration with Existing Systems** - Extends Epic 03 job postings with intelligent recommendations
- ✅ **Moderate to Significant Impact** - New database columns, OpenAI embedding integration, new APIs, frontend updates

**Enhancement Description:**

Transform the hard-coded job recommendations into an intelligent, AI-powered matching system that uses semantic embeddings to match candidates with job postings. This requires building out candidate profile management (skills, experience, preferences), implementing OpenAI-based resume parsing, and creating a semantic similarity matching engine that considers skills, experience level, preferences, and job descriptions.

**Impact Assessment:**
- ✅ **Moderate Impact** - Extends existing models without breaking changes
- Database: New columns on `candidates` table, utilize existing `resumes.parsed_data`
- Backend: New services for embedding generation, matching algorithm, profile management APIs
- Frontend: Real implementations for existing mocked profile/preference pages
- AI Integration: OpenAI text embeddings for semantic matching

### 1.5 Goals and Background Context

**Goals:**
- Enable candidates to build comprehensive profiles with skills, experience, and job preferences
- Automatically parse uploaded resumes using OpenAI to extract skills and experience
- Generate semantic embeddings for candidate profiles and job postings
- Match candidates to jobs using AI-powered similarity scoring (not just keyword matching)
- Replace hard-coded job matches with real-time personalized recommendations
- Explain match scores with human-readable reasons ("Why this matches you")

**Background Context:**

Epic 03 successfully implemented job posting browsing and applications that trigger customized interviews. However, the candidate discovery experience relies on manual job browsing. Candidates see hard-coded "match scores" and recommendations that don't reflect their actual profile. This enhancement completes the candidate journey by enabling intelligent job discovery through AI-powered matching. By leveraging OpenAI embeddings and semantic similarity, the system can understand that "React expertise" matches "Frontend Developer with Next.js" even when exact keywords differ, providing superior matching compared to traditional keyword-based systems.

### 1.6 Change Log

| Change | Date | Version | Description | Author |
|--------|------|---------|-------------|--------|
| Initial draft | 2025-11-06 | 1.0 | Created brownfield PRD for intelligent job matching | PM Agent (John) |

---

## 2. Requirements

### 2.1 Functional Requirements

**FR1:** The system shall extend the `candidates` table with profile fields: `skills` (JSONB array), `experience_years` (integer), `preferred_job_types` (JSONB array), `preferred_locations` (JSONB array), `preferred_work_setup` (enum: remote|hybrid|onsite|any), `salary_expectation_min` (decimal), `salary_expectation_max` (decimal), `salary_currency` (VARCHAR default 'AUD'), `profile_completeness_score` (integer 0-100).

**FR2:** The system shall automatically parse uploaded resumes using OpenAI GPT-4 to extract: skills array, experience_years, education, previous_roles, and technical_domains into `resumes.parsed_data` JSONB field.

**FR3:** The system shall provide REST API endpoints for candidates to update their profile: skills, experience level, job preferences (type, location, work setup, salary range).

**FR4:** The system shall calculate and update `profile_completeness_score` based on presence of: skills (30%), resume uploaded (20%), preferences set (30%), experience_years (10%), contact info complete (10%).

**FR5:** The system shall generate OpenAI embeddings (text-embedding-3-large, 3072 dimensions) for candidate profiles combining: skills, experience description, and job preferences.

**FR6:** The system shall generate OpenAI embeddings for job postings combining: title, description, required_skills, experience_level, and role_category.

**FR7:** The system shall store embeddings in PostgreSQL using pgvector extension in new columns: `candidates.profile_embedding` (vector(3072)) and `job_postings.job_embedding` (vector(3072)).

**FR8:** The system shall provide a job matching API endpoint that calculates cosine similarity between candidate profile embedding and all active job posting embeddings, returning top N matches sorted by similarity score.

**FR9:** The system shall convert similarity scores (0.0-1.0) to match percentages (0-100%) and classify matches: Excellent (90-100%), Great (80-89%), Good (70-79%), Fair (60-69%).

**FR10:** The system shall generate human-readable match explanations using OpenAI by analyzing: overlapping skills, experience level alignment, salary range fit, location/work setup preferences, and missing requirements.

**FR11:** The frontend `/profile` page shall fetch and display real candidate profile data from the backend API instead of using mock data.

**FR12:** The frontend `/profile/skills`, `/profile/preferences`, and `/profile/resume` pages shall implement actual API calls to update candidate profile data.

**FR13:** The frontend `/jobs/matches` page shall fetch AI-matched jobs from the backend API with real match scores, explanations, and dynamically enable/disable matching based on profile completeness.

**FR14:** The system shall re-generate candidate profile embeddings whenever: skills updated, resume re-uploaded and parsed, or preferences changed significantly.

**FR15:** The system shall re-generate job posting embeddings whenever: job description updated, required_skills modified, or experience_level changed.

**FR16:** The system shall provide an admin/seed endpoint to batch-generate embeddings for existing job postings (Epic 03 seed data already in database).

**FR17:** The system shall block job matching API requests if candidate profile completeness < 40%, returning a message prompting profile completion.

**FR18:** The dashboard page shall display real profile completion progress with actionable links to incomplete profile sections.

### 2.2 Non-Functional Requirements

**NFR1:** Resume parsing using OpenAI shall complete within 30 seconds for documents up to 5MB, with retries on temporary failures.

**NFR2:** Embedding generation shall use batch API calls (up to 100 items) to minimize latency and API costs.

**NFR3:** Job matching queries using pgvector cosine similarity shall return results within 500ms for databases containing up to 10,000 job postings.

**NFR4:** Profile completeness calculation shall be computed synchronously on profile updates and cached in the database field (no runtime calculation).

**NFR5:** The pgvector extension shall use HNSW index on embedding columns for performance optimization with parameters: m=16, ef_construction=64.

**NFR6:** All new API endpoints shall follow existing authentication patterns using the candidate JWT token from Epic 01.

**NFR7:** Profile and preference update APIs shall validate data types and enums matching existing database constraints before persistence.

**NFR8:** The system shall handle resume parsing failures gracefully by storing status="failed" and error messages, allowing manual skill entry as fallback.

**NFR9:** Match explanation generation shall be asynchronous and cached to avoid repeated OpenAI API calls for the same candidate-job pair.

**NFR10:** Database migrations shall add nullable columns with default values to ensure backward compatibility with existing candidate records.

### 2.3 Compatibility Requirements

**CR1: Existing Authentication Flow** - All new profile and matching endpoints shall use the existing JWT authentication middleware from Epic 01 (Story 1.3) without modifications to token structure or validation logic.

**CR2: Resume Upload Compatibility** - The resume parsing enhancement shall work with resumes already uploaded in Epic 01 (existing `resumes` table records), triggering parsing for `parsing_status='completed'` records where `parsed_data` is null or incomplete.

**CR3: Job Posting Schema Stability** - Adding `job_embedding` column to `job_postings` table shall not break existing Epic 03 APIs (`GET /api/v1/job-postings`, application submission), ensuring all existing functionality continues working.

**CR4: Frontend Route Preservation** - Implementing `/profile/*` pages shall maintain existing route structure and shadcn/ui component patterns used in Epic 03 pages.

**CR5: Database Connection Pooling** - New embedding queries shall use the existing `AsyncSessionLocal` database session management without requiring connection pool reconfiguration.

---

## 3. User Interface Enhancement Goals

### 3.1 Integration with Existing UI

The new profile management and job matching UIs will integrate seamlessly with the existing Next.js frontend using established patterns:

**Component Library**: Continue using shadcn/ui components (Card, Button, Badge, Progress, Form, Input, Select, Textarea) as seen in Epic 03 job pages

**Styling**: Maintain Tailwind CSS utility classes with existing color scheme (primary, accent, muted-foreground) and responsive design patterns (max-w-7xl containers, grid layouts)

**State Management**: **Zustand stores** for:
- Candidate profile state (skills, preferences, completeness)
- Job matching preferences (filters, sort order)
- UI state (modals, drawer open/close)

**Data Fetching**: **TanStack Query (React Query)** for:
- Profile data queries with automatic caching and refetching
- Job matches queries with staleTime configuration
- Mutations for profile updates with optimistic updates
- Resume parsing status polling

**Authentication**: Leverage existing JWT token storage and API client patterns from Epic 01 authentication flow

### 3.2 Modified/New Screens and Views

**Pages to Implement (currently mocked):**

1. **`/profile` (Main Profile)** - Display candidate info with real profile completeness score, editable basic info
   - Uses: `useProfileQuery()`, `useUpdateProfileMutation()`
2. **`/profile/skills` (Skills Management)** - Add/remove skills with autocomplete, display parsed resume skills
   - Uses: `useSkillsQuery()`, `useUpdateSkillsMutation()` with optimistic updates
3. **`/profile/preferences` (Job Preferences)** - Set preferred job types, locations, work setup, salary range
   - Uses: `usePreferencesQuery()`, `useUpdatePreferencesMutation()`
4. **`/profile/resume` (Resume Management)** - Upload resume, view parsing status, display extracted data
   - Uses: `useResumeQuery()`, `useUploadResumeMutation()`, `useParsingStatusQuery()` with polling

**Pages to Update (currently use mock data):**

5. **`/jobs/matches` (AI Job Matches)** - Replace hard-coded jobs with real API matches, real match scores and explanations
   - Uses: `useJobMatchesQuery()` with `staleTime: 5 minutes`, Zustand for filter state
6. **`/dashboard` (Dashboard)** - Real profile completion widget, real matched jobs count
   - Uses: `useProfileQuery()`, `useJobMatchesQuery({ limit: 3 })`

**New Zustand Stores:**

7. **`useProfileStore`** - Manages local profile state, completeness calculation, dirty state tracking
8. **`useMatchingStore`** - Manages matching preferences, filter state, sort preferences

**New TanStack Query Hooks:**

9. **`useProfileQuery()`** - Fetches candidate profile with automatic refetch on window focus
10. **`useJobMatchesQuery(options)`** - Fetches AI matches with configurable staleTime and filters
11. **`useUpdateProfileMutation()`** - Updates profile with optimistic updates and automatic query invalidation
12. **`useParsingStatusQuery()`** - Polls resume parsing status every 2 seconds when status="processing"

**New Reusable Components:**

13. **Profile Completeness Widget** - Visual progress bar with actionable items
14. **Skills Input Component** - Tag-based skill entry with validation and autocomplete
15. **Match Score Display** - Percentage with classification badge (Excellent/Great/Good/Fair)
16. **Match Explanation Card** - Collapsible AI-generated match reasons

### 3.3 UI Consistency Requirements

**UCR1:** All profile forms shall use shadcn/ui Form components with React Hook Form integration and TanStack Query mutations for submission.

**UCR2:** Profile completeness progress bars shall use the existing Progress component with consistent color coding (< 40% red/destructive, 40-70% yellow/warning, > 70% green/primary).

**UCR3:** Skills tags shall use Badge variant="outline" consistent with skill displays in job posting pages.

**UCR4:** Match score displays shall use the same card layout patterns as job listings (CardHeader, CardContent structure).

**UCR5:** Empty states (no skills, no preferences set) shall follow existing empty state patterns with icons and call-to-action buttons.

**UCR6:** Loading states during resume parsing or matching shall use TanStack Query's `isLoading` and `isFetching` states with skeleton loaders.

**UCR7:** Error messages for API failures shall use TanStack Query's error handling with toast notifications or inline error displays.

**UCR8:** Mobile responsive breakpoints shall match existing pages: single column < 768px, two columns >= 768px, three columns >= 1024px.

**UCR9:** Optimistic updates for profile changes shall provide immediate UI feedback before server confirmation using TanStack Query's `onMutate` callbacks.

**UCR10:** Zustand stores shall persist relevant state to localStorage (matching preferences, UI preferences) using zustand/middleware.

---

## 4. Technical Constraints and Integration Requirements

### 4.1 Existing Technology Stack

**Languages**: 
- Python 3.11+ (Backend)
- TypeScript 5.x (Frontend)

**Frameworks**: 
- Backend: FastAPI 0.104+, SQLAlchemy 2.x, Alembic (migrations), Pydantic v2
- Frontend: Next.js 14+ (App Router), React 18+, Zustand 4.x, TanStack Query v5

**Database**: 
- PostgreSQL 15+ (Supabase hosted)
- pgvector extension for embedding storage
- Existing extensions: uuid-ossp

**AI/ML**:
- OpenAI API: GPT-4 (resume parsing), text-embedding-3-large (embeddings)
- LangChain (existing interview engine)

**Infrastructure**: 
- Supabase (PostgreSQL, Storage for resumes)
- Vercel (Frontend deployment assumed)
- Environment: .env files for configuration

**External Dependencies**: 
- OpenAI Python SDK, LangChain
- Frontend: shadcn/ui, Tailwind CSS, Lucide icons

### 4.2 Integration Approach

**Database Integration Strategy**: 
- Add nullable columns to existing `candidates` table using Alembic migration with default values
- Enable pgvector extension via Supabase dashboard SQL editor
- Add vector columns: `candidates.profile_embedding vector(3072)`, `job_postings.job_embedding vector(3072)`
- Create HNSW indexes on vector columns for performance
- No breaking changes to existing tables/relationships

**API Integration Strategy**: 
- New FastAPI routes under `/api/v1/profile/*` and `/api/v1/matching/*`
- Use existing dependency injection patterns: `Depends(get_db)`, `Depends(get_current_candidate)`
- New service layer: `ProfileService`, `EmbeddingService`, `MatchingService` following existing patterns
- New repository layer: `ProfileRepository`, `MatchingRepository`
- OpenAI API calls wrapped in async service methods with error handling

**Frontend Integration Strategy**: 
- Create new TanStack Query hooks in `frontend/lib/api/` following existing patterns
- Create Zustand stores in `frontend/lib/stores/` with TypeScript interfaces
- Implement pages in `frontend/app/profile/*` using App Router conventions
- Update existing `frontend/app/jobs/matches/page.tsx` to use real API
- API client base URL from environment variables (existing pattern)

### 4.3 Code Organization and Standards

**File Structure Approach**:
```
backend/app/
  models/
    candidate.py (EXTEND with profile fields)
    job_posting.py (EXTEND with embedding column)
  schemas/
    profile.py (NEW - request/response schemas)
    matching.py (NEW - match result schemas)
  repositories/
    profile_repository.py (NEW)
    matching_repository.py (NEW)
  services/
    profile_service.py (NEW)
    embedding_service.py (NEW)
    matching_service.py (NEW)
  api/v1/endpoints/
    profile.py (NEW - /profile/* routes)
    matching.py (NEW - /matching/* routes)

frontend/
  lib/
    api/
      profile.ts (NEW - API client functions)
      matching.ts (NEW - matching API calls)
    stores/
      profile-store.ts (NEW - Zustand store)
      matching-store.ts (NEW - Zustand store)
    hooks/
      use-profile.ts (NEW - TanStack Query hooks)
      use-matching.ts (NEW - TanStack Query hooks)
  app/
    profile/
      page.tsx (IMPLEMENT)
      skills/page.tsx (IMPLEMENT)
      preferences/page.tsx (IMPLEMENT)
      resume/page.tsx (IMPLEMENT)
    jobs/matches/
      page.tsx (UPDATE to use real API)
```

**Naming Conventions**:
- Backend: snake_case for files, functions, variables
- Frontend: kebab-case for files, camelCase for functions, PascalCase for components
- Zustand stores: `use{Name}Store` pattern
- TanStack Query hooks: `use{Entity}Query`, `use{Action}Mutation` pattern

**Coding Standards**:
- Backend: Follow existing FastAPI + SQLAlchemy patterns in Epic 01-03
- Backend: Pydantic schemas for request/response validation
- Frontend: TypeScript strict mode, explicit return types for functions
- Frontend: Async/await for API calls, error boundaries for error handling

**Documentation Standards**:
- Docstrings for all service methods (Google style)
- TypeScript JSDoc comments for exported functions
- README updates for new API endpoints
- Story completion notes in story markdown files

### 4.4 Deployment and Operations

**Build Process Integration**:
- Backend: No changes to existing FastAPI startup process
- Frontend: Add Zustand and TanStack Query dependencies to package.json
- Database: Migration runs via `alembic upgrade head` (existing process)
- pgvector extension enabled manually via Supabase SQL editor (one-time setup)

**Deployment Strategy**:
- Backend: Deploy to existing environment with new environment variables for OpenAI embedding model
- Frontend: Standard Next.js build process, no deployment changes
- Database migration: Run during deployment maintenance window (nullable columns = zero downtime)
- Seed embeddings: Manual admin endpoint execution post-deployment for existing jobs

**Monitoring and Logging**:
- Log OpenAI API calls (tokens used, latency) using existing logging patterns
- Log matching query performance (pgvector query time, results returned)
- Track profile completeness distribution in application logs
- Monitor resume parsing success/failure rates

**Configuration Management**:
- New environment variables: `OPENAI_EMBEDDING_MODEL=text-embedding-3-large`, `EMBEDDING_BATCH_SIZE=100`
- Existing variables reused: `OPENAI_API_KEY`, `DATABASE_URL`
- Frontend environment: `NEXT_PUBLIC_API_URL` (existing)

### 4.5 Risk Assessment and Mitigation

**Technical Risks**:
- **Risk**: pgvector performance degrades with > 10k jobs
  - **Mitigation**: HNSW index with m=16, ef_construction=64; monitor query times; add pagination if needed
- **Risk**: OpenAI API rate limits during batch embedding generation
  - **Mitigation**: Implement exponential backoff, batch size configuration, optional job queuing
- **Risk**: Resume parsing failures for uncommon formats
  - **Mitigation**: Fallback to manual skill entry, store error details, support re-parsing

**Integration Risks**:
- **Risk**: Adding profile columns breaks existing candidate queries
  - **Mitigation**: All new columns nullable with defaults, manual testing of existing Epic 01-03 APIs post-migration
- **Risk**: Embedding generation cost explosion
  - **Mitigation**: Cache embeddings, only regenerate on content changes, monitor usage via logging

**Deployment Risks**:
- **Risk**: Migration fails on production database
  - **Mitigation**: Test migration on Supabase staging database first, implement rollback plan
- **Risk**: Frontend deploy breaks without backend deploy
  - **Mitigation**: Feature flag for matching UI, graceful degradation to mock data

**Mitigation Strategies**:
- **Phased rollout**: Deploy backend + migration first, then frontend updates
- **Feature flags**: Environment variable to enable/disable AI matching
- **Monitoring**: Alert on OpenAI API errors, slow pgvector queries (> 1s), parsing failure rate > 20%
- **Rollback plan**: Alembic downgrade migration prepared, frontend can revert to mock data

---

## 5. Epic and Story Structure

### 5.1 Epic Approach

**Epic Structure Decision**: **Single comprehensive epic**

This enhancement represents a cohesive feature set (intelligent job matching) that requires coordinated implementation across database, backend services, and frontend. The work flows logically from foundation (profile schema, resume parsing) → matching engine → UI implementation, making a single epic with sequenced stories the optimal approach.

---

## 6. Epic 04: Intelligent Job Matching System

**Epic Goal**: Transform hard-coded job recommendations into an AI-powered matching system that uses semantic embeddings to intelligently match candidates with relevant job postings based on skills, experience, and preferences, while enabling comprehensive candidate profile management.

**Integration Requirements**: 
- Extends Epic 03 job postings with embedding-based matching without breaking existing application flow
- Utilizes existing Epic 01 resume upload infrastructure with new AI parsing capabilities
- Maintains backward compatibility with existing candidates who lack profile data
- Implements mocked frontend pages from Epic 01-03 with real API integrations

---

### Story 4.1: Candidate Profile Schema Extensions and Database Migration

**As a** developer,  
**I want** extended candidate profile schema with skills, experience, preferences, and embedding storage,  
**so that** the system can store comprehensive candidate data for intelligent matching.

**Acceptance Criteria:**

1. Alembic migration created to extend `candidates` table with profile fields: `skills` (JSONB), `experience_years` (INTEGER), `preferred_job_types` (JSONB), `preferred_locations` (JSONB), `preferred_work_setup` (VARCHAR CHECK IN), `salary_expectation_min` (NUMERIC), `salary_expectation_max` (NUMERIC), `salary_currency` (VARCHAR default 'AUD'), `profile_completeness_score` (INTEGER default 0)
2. pgvector extension enabled in Supabase PostgreSQL database (SQL: `CREATE EXTENSION IF NOT EXISTS vector;`)
3. Vector columns added: `candidates.profile_embedding vector(3072)`, `job_postings.job_embedding vector(3072)`
4. HNSW indexes created on both embedding columns with parameters: `m=16, ef_construction=64`
5. All new candidate profile columns are nullable with appropriate defaults for backward compatibility
6. Migration can apply to existing database with Epic 01-03 data and rollback cleanly
7. Updated `Candidate` SQLAlchemy model with new profile fields and type hints
8. Updated `JobPosting` SQLAlchemy model with `job_embedding` column

**Integration Verification:**

**IV1: Existing Candidate Records** - Query existing candidates after migration, verify all fields intact, new profile fields are NULL/defaults, existing relationships (resumes, interviews, applications) still work

**IV2: Existing Job Posting APIs** - Manually test Epic 03 job listing and application endpoints, verify no breaking changes, job_embedding column ignored by existing queries

**IV3: Database Index Performance** - Run EXPLAIN ANALYZE on sample vector similarity query, verify HNSW index used, query completes < 500ms with 1000+ job postings

---

### Story 4.2: OpenAI Resume Parsing Service

**As a** candidate,  
**I want** my uploaded resume automatically parsed to extract skills and experience,  
**so that** I don't have to manually enter all my profile information.

**Acceptance Criteria:**

1. `EmbeddingService` class created in `backend/app/services/embedding_service.py` with OpenAI client initialization
2. Resume parsing method implemented using GPT-4 to extract: `skills` (array), `experience_years` (integer), `education` (string), `previous_roles` (array), `technical_domains` (object)
3. Parsing results stored in `resumes.parsed_data` JSONB field with structured schema
4. Parsing updates `resumes.parsing_status` to "processing" → "completed" or "failed"
5. Parsing completion automatically populates `candidates.skills` and `candidates.experience_years` from parsed data
6. OpenAI API errors handled gracefully with retry logic (3 attempts with exponential backoff)
7. Parsing timeout set to 30 seconds with appropriate error message if exceeded
8. Resume parsing triggered automatically on resume upload completion
9. Admin endpoint created: `POST /api/v1/admin/parse-resume/{resume_id}` for manual re-parsing

**Integration Verification:**

**IV1: Existing Resume Upload Flow** - Upload resume via Epic 01 endpoint, verify parsing triggered automatically, parsed_data populated correctly

**IV2: Profile Population** - After parsing completes, verify candidate.skills array contains extracted skills, experience_years updated

**IV3: Parsing Failure Handling** - Test with corrupted/unsupported file, verify parsing_status="failed", error message stored, candidate can still manually enter skills

---

### Story 4.3: Profile Management API Endpoints

**As a** candidate,  
**I want** API endpoints to view and update my profile, skills, and job preferences,  
**so that** I can manage my job matching preferences.

**Acceptance Criteria:**

1. `ProfileService` created in `backend/app/services/profile_service.py` with CRUD methods
2. `ProfileRepository` created in `backend/app/repositories/profile_repository.py` for database operations
3. Pydantic schemas created in `backend/app/schemas/profile.py`: `ProfileResponse`, `ProfileUpdateRequest`, `SkillsUpdateRequest`, `PreferencesUpdateRequest`
4. API endpoint: `GET /api/v1/profile` returns current candidate profile including completeness score
5. API endpoint: `PUT /api/v1/profile` updates basic profile fields (experience_years)
6. API endpoint: `PUT /api/v1/profile/skills` updates skills array with validation (max 50 skills, min 1)
7. API endpoint: `PUT /api/v1/profile/preferences` updates job preferences (job_types, locations, work_setup, salary_range)
8. Profile completeness score calculated on every update: skills (30%), resume uploaded (20%), preferences set (30%), experience_years (10%), phone (10%)
9. All endpoints require authentication using existing JWT middleware from Epic 01
10. Input validation for enums (work_setup), numeric ranges (salary), array lengths

**Integration Verification:**

**IV1: Authentication Integration** - Test all profile endpoints without token (expect 401), with valid token (expect 200/204), verify candidate_id from JWT used correctly

**IV2: Profile Completeness Accuracy** - Create test candidate with: (a) no data (0%), (b) only resume (20%), (c) skills + resume (50%), (d) all fields (100%), verify scores match

**IV3: Concurrent Updates** - Test simultaneous profile updates from multiple requests, verify no race conditions or data corruption

---

### Story 4.4: Embedding Generation Service

**As a** developer,  
**I want** a service that generates OpenAI embeddings for candidate profiles and job postings,  
**so that** semantic similarity matching can be performed.

**Acceptance Criteria:**

1. `EmbeddingService.generate_embedding()` method created using `text-embedding-3-large` model (3072 dimensions)
2. Candidate profile embedding combines: skills (comma-separated), experience_years description, job preferences into single text string for embedding
3. Job posting embedding combines: title, description, required_skills (comma-separated), experience_level, role_category into single text string
4. Batch embedding generation method created: `generate_embeddings_batch()` processes up to 100 items per OpenAI API call
5. Embedding generation triggered automatically on profile updates (skills, preferences changed)
6. Embedding generation triggered automatically on job posting creation/updates (description, required_skills changed)
7. Generated embeddings stored in `candidates.profile_embedding` and `job_postings.job_embedding` vector columns
8. OpenAI API call logging implemented (tokens used, latency, errors)
9. Admin endpoint: `POST /api/v1/admin/generate-embeddings` for batch generation with query params: `entity_type=candidates|jobs`, `limit=100`

**Integration Verification:**

**IV1: Profile Update Triggers Embedding** - Update candidate skills via API, verify profile_embedding column updated within 3 seconds, embedding has 3072 dimensions

**IV2: Job Update Triggers Embedding** - Update job posting description via Epic 03 endpoint, verify job_embedding column updated

**IV3: Batch Generation Performance** - Run admin endpoint to generate embeddings for 50 existing job postings, verify completes < 10 seconds, all embeddings stored correctly

---

### Story 4.5: Job Matching Algorithm with pgvector

**As a** candidate,  
**I want** the system to calculate match scores between my profile and job postings using AI,  
**so that** I receive personalized job recommendations.

**Acceptance Criteria:**

1. `MatchingService` created in `backend/app/services/matching_service.py` with matching logic
2. `MatchingRepository` created with pgvector cosine similarity query using `<=>` operator
3. Matching query retrieves top N jobs sorted by similarity score (1 - cosine_distance)
4. Similarity scores (0.0-1.0) converted to match percentages (0-100%)
5. Match classification logic: Excellent (90-100%), Great (80-89%), Good (70-79%), Fair (60-69%), filtered if < 60%
6. Matching considers candidate preferences: filter by preferred_locations, preferred_work_setup, salary_range overlap
7. API endpoint: `GET /api/v1/matching/jobs?limit=20` returns matched jobs with scores
8. Matching blocked if `profile_completeness_score < 40`, returns 403 with message prompting profile completion
9. Query uses HNSW index for performance (verified via EXPLAIN ANALYZE)
10. Response includes: job details, match_score (percentage), match_classification (Excellent/Great/Good/Fair)

**Integration Verification:**

**IV1: Known Similarity Test** - Create test candidate and job with identical skills/description, verify match_score > 95%

**IV2: Preference Filtering** - Create test candidate preferring "remote" work, verify only remote/hybrid jobs returned, onsite jobs filtered out

**IV3: Profile Completeness Block** - Test candidate with completeness < 40%, verify matching endpoint returns 403 error with actionable message

---

### Story 4.6: Match Explanation Generation with OpenAI

**As a** candidate,  
**I want** to understand why jobs match my profile,  
**so that** I can make informed application decisions.

**Acceptance Criteria:**

1. `MatchingService.generate_match_explanation()` method created using GPT-4
2. Explanation generation analyzes: overlapping skills, experience level alignment (years), salary range fit, location/work setup preferences, missing requirements
3. Explanation returned as structured JSON: `matching_factors` (array of positive reasons), `missing_requirements` (array), `recommendation` (string)
4. Explanations generated on-demand when candidate requests job details
5. Explanations cached in-memory or database for 24 hours (candidate_id + job_posting_id key)
6. API endpoint: `GET /api/v1/matching/jobs/{job_id}/explanation` returns explanation for specific job match
7. Explanation generation has 10-second timeout with fallback to generic explanation
8. OpenAI prompt engineered to return concise, actionable insights (max 150 words)
9. Explanation includes specific skill matches: "Your React and TypeScript skills align with this role"

**Integration Verification:**

**IV1: Explanation Quality** - Generate explanations for 5 test candidate-job pairs with varying match scores, verify explanations mention specific skills/factors

**IV2: Cache Functionality** - Request explanation for same job twice within 1 minute, verify second request served from cache (no duplicate OpenAI API call logged)

**IV3: Timeout Handling** - Mock slow OpenAI API response (> 10s), verify fallback explanation returned, no request failure

---

### Story 4.7: Frontend Profile Management Implementation

**As a** candidate,  
**I want** to manage my profile, skills, and preferences through an intuitive UI,  
**so that** I can optimize my job matching results.

**Acceptance Criteria:**

1. TanStack Query hooks created in `frontend/lib/hooks/use-profile.ts`: `useProfileQuery()`, `useUpdateProfileMutation()`, `useUpdateSkillsMutation()`, `useUpdatePreferencesMutation()`
2. Zustand store created in `frontend/lib/stores/profile-store.ts` for local profile state and dirty tracking
3. API client functions created in `frontend/lib/api/profile.ts` with TypeScript interfaces
4. `/profile` page implemented: displays real profile data, profile completeness widget, edit basic info inline
5. `/profile/skills` page implemented: skills tag input component, display parsed resume skills (read-only), add/remove custom skills, autocomplete suggestions
6. `/profile/preferences` page implemented: form for job types (multi-select), locations (multi-select), work setup (radio), salary range (number inputs)
7. `/profile/resume` page implemented: resume upload, parsing status polling (using TanStack Query with `refetchInterval`), display parsed_data in structured format
8. Profile completeness widget shows progress bar, lists incomplete sections with action buttons
9. Optimistic updates implemented for skills and preferences mutations
10. Loading states, error states, and success toasts for all mutations
11. Mobile responsive design following existing page patterns

**Integration Verification:**

**IV1: Profile Data Sync** - Update skills via frontend, verify backend API called correctly, profile_completeness_score updates, UI reflects new completeness

**IV2: Resume Upload Flow** - Upload resume, verify parsing status polling starts, status updates from "processing" to "completed", parsed skills appear in skills page

**IV3: Optimistic Updates** - Add skill via frontend, verify skill appears immediately in UI, verify API call succeeds in background, no UI flicker

---

### Story 4.8: Frontend Job Matching Implementation

**As a** candidate,  
**I want** to see AI-powered job recommendations based on my profile,  
**so that** I can discover relevant opportunities.

**Acceptance Criteria:**

1. TanStack Query hooks created in `frontend/lib/hooks/use-matching.ts`: `useJobMatchesQuery()`, `useMatchExplanationQuery(jobId)`
2. Zustand store created in `frontend/lib/stores/matching-store.ts` for matching preferences and filters
3. API client functions created in `frontend/lib/api/matching.ts`
4. `/jobs/matches` page updated: replace mock data with `useJobMatchesQuery()` hook
5. Match score component displays percentage with classification badge (Excellent/Great/Good/Fair) using color coding
6. Match reasons displayed in collapsible card for each job (fetched on expand)
7. "Why this matches you" section loads match explanation on demand
8. Profile completeness gate: if < 40%, show banner prompting profile completion instead of job list
9. Empty state: if no matches found, show message with suggestions to improve profile
10. Loading skeleton for initial matches load
11. Match preference controls: sort by (match score, posted date), filter by (location, work setup)
12. "Matched Jobs" count displayed in dashboard widget using `useJobMatchesQuery({ limit: 0 })`

**Integration Verification:**

**IV1: Real Match Data** - Complete profile to 100%, verify `/jobs/matches` displays real jobs from database with match scores, verify scores sorted descending

**IV2: Match Explanation Load** - Click "Why this matches you", verify API call to `/api/v1/matching/jobs/{id}/explanation`, explanation displayed with specific skills mentioned

**IV3: Profile Completeness Block** - Set test candidate completeness to 30%, verify `/jobs/matches` shows completion prompt, no job list displayed

---

### Story 4.9: Batch Embedding Generation for Existing Data

**As a** system administrator,  
**I want** to generate embeddings for all existing job postings and candidate profiles,  
**so that** the matching system works with existing data.

**Acceptance Criteria:**

1. Admin CLI script created: `backend/scripts/generate_embeddings.py` with argument parsing for entity type and batch size
2. Script queries candidates with `profile_completeness_score >= 40` and `profile_embedding IS NULL`
3. Script queries job_postings with `status='active'` and `job_embedding IS NULL`
4. Batch processing: processes records in groups of 100, calls `EmbeddingService.generate_embeddings_batch()`
5. Progress logging: prints "Processed X/Y records" every 100 records
6. Error handling: logs failed records, continues processing, outputs summary at end
7. Dry-run mode: `--dry-run` flag to preview records that would be processed
8. Script can be run multiple times safely (idempotent, only processes NULL embeddings)
9. Script respects OpenAI rate limits with exponential backoff on 429 errors
10. Documentation added to README with usage instructions

**Integration Verification:**

**IV1: Existing Job Postings** - Run script on database with Epic 03 seed job postings (20+ jobs), verify all active jobs have job_embedding populated

**IV2: Existing Candidate Profiles** - Create 5 test candidates with complete profiles, run script, verify all have profile_embedding populated

**IV3: Idempotency** - Run script twice on same data, verify second run processes 0 records (all embeddings already exist)

---

## Appendix

### A. Story Sequencing Rationale

**Dependency Chain:**
1. **4.1 (Schema)** - Foundation layer, must be first
2. **4.2 (Resume Parsing)** - Populates profile data, needed before embeddings
3. **4.3 (Profile APIs)** - Enables manual profile management, independent of matching
4. **4.4 (Embeddings)** - Core matching infrastructure, depends on schema
5. **4.5 (Matching Algorithm)** - Depends on embeddings being available
6. **4.6 (Explanations)** - Enhancement to matching, can be parallel with frontend
7. **4.7 (Profile UI)** - Frontend implementation, depends on backend APIs (4.2, 4.3)
8. **4.8 (Matching UI)** - Final integration, depends on all backend stories
9. **4.9 (Batch Generation)** - Operations story, can run after 4.4 deployed

### B. Environment Variables

**New Backend Variables:**
```bash
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_BATCH_SIZE=100
```

**Existing Variables (reused):**
```bash
OPENAI_API_KEY=<your-key>
DATABASE_URL=<supabase-connection-string>
```

### C. pgvector Setup Commands

**Enable Extension (run once in Supabase SQL editor):**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Verify Installation:**
```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### D. Embedding Cost Estimation

**text-embedding-3-large pricing:** ~$0.13 per 1M tokens

**Estimated Usage:**
- Candidate profile: ~200 tokens → $0.000026 per profile
- Job posting: ~400 tokens → $0.000052 per job
- Batch 1000 jobs: ~$0.052
- Batch 10,000 candidates: ~$0.26

**Monthly estimates (assuming 1000 new candidates, 100 new jobs):**
- Profile embeddings: $0.026
- Job embeddings: $0.0052
- Match explanations (500/month @ 500 tokens): ~$0.033
- **Total: ~$0.065/month** (negligible cost)
