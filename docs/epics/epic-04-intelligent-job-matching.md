# Epic 04: Intelligent Job Matching System

**Status:** Ready for Development  
**Epic Goal:** Transform hard-coded job recommendations into an AI-powered matching system that uses semantic embeddings to intelligently match candidates with relevant job postings based on skills, experience, and preferences, while enabling comprehensive candidate profile management.

**Dependencies:** Epic 01 (Foundation), Epic 02 (Video Interviews), Epic 03 (Job-Driven Interviews)

---

## Overview

This epic implements AI-powered job matching using OpenAI embeddings and semantic similarity. Candidates build comprehensive profiles (skills, experience, preferences), resumes are automatically parsed, and pgvector-based matching recommends relevant jobs with explainable match scores.

### Key Features

- **Candidate Profile Management**: Skills inventory, experience tracking, job preferences
- **AI Resume Parsing**: Automatic skill extraction using GPT-4
- **Semantic Embeddings**: text-embedding-3-large (3072 dimensions) for profiles and jobs
- **pgvector Matching**: HNSW-indexed cosine similarity for fast, accurate recommendations
- **Match Explanations**: GPT-4 generated reasons for job-candidate matches
- **Profile Completeness**: Calculated score with UI prompts to improve matching

### Integration Points

- Extends `candidates` and `job_postings` tables (Epic 01 & 03 schemas)
- Utilizes `resumes.parsed_data` JSONB field from Epic 01
- Implements mocked profile/preference pages from Epic 01-03 frontend
- Uses existing JWT authentication from Epic 01

---

## Technical Architecture

### Backend

**New Services:**
- `ProfileService`: CRUD operations for candidate profiles
- `EmbeddingService`: OpenAI embedding generation (batch + individual)
- `MatchingService`: pgvector similarity queries and match scoring

**New API Endpoints:**
- `GET /api/v1/profile` - Fetch candidate profile
- `PUT /api/v1/profile/skills` - Update skills
- `PUT /api/v1/profile/preferences` - Update job preferences
- `GET /api/v1/matching/jobs` - Get matched jobs with scores
- `GET /api/v1/matching/jobs/{id}/explanation` - Get match reasoning
- `POST /api/v1/admin/generate-embeddings` - Batch embedding generation

**Database Changes:**
- Extend `candidates` table: skills, experience_years, preferences, profile_completeness_score, profile_embedding
- Extend `job_postings` table: job_embedding
- Enable pgvector extension, create HNSW indexes

### Frontend

**State Management:**
- **Zustand**: Profile state, matching preferences, UI state
- **TanStack Query**: API data fetching, caching, mutations, optimistic updates

**New/Updated Pages:**
- `/profile` - Profile overview with completeness widget
- `/profile/skills` - Skills management with autocomplete
- `/profile/preferences` - Job preferences form
- `/profile/resume` - Resume upload with parsing status
- `/jobs/matches` - AI-matched jobs (replace mock data)
- `/dashboard` - Real profile completion widget

---

## Stories

### Story 4.1: Candidate Profile Schema Extensions and Database Migration
**Prerequisite** - Database foundation for all matching features

- Extend `candidates` table with profile fields (skills, experience, preferences)
- Enable pgvector extension in Supabase
- Add vector(3072) columns for embeddings
- Create HNSW indexes (m=16, ef_construction=64)
- Update SQLAlchemy models

**Story File:** `docs/stories/4.1.candidate-profile-schema.md`

---

### Story 4.2: OpenAI Resume Parsing Service
Automatic skill extraction from uploaded resumes

- GPT-4 parsing: skills, experience_years, education, roles
- Store in `resumes.parsed_data` JSONB
- Auto-populate `candidates.skills` and `experience_years`
- Retry logic, timeout handling, error states
- Admin endpoint for manual re-parsing

**Story File:** `docs/stories/4.2.resume-parsing-service.md`

---

### Story 4.3: Profile Management API Endpoints
REST APIs for candidate profile CRUD operations

- `ProfileService` and `ProfileRepository` layers
- Pydantic schemas for request/response validation
- Endpoints: GET/PUT profile, skills, preferences
- Profile completeness calculation (0-100%)
- JWT authentication integration

**Story File:** `docs/stories/4.3.profile-management-apis.md`

---

### Story 4.4: Embedding Generation Service
OpenAI embedding generation for semantic matching

- `text-embedding-3-large` integration (3072 dimensions)
- Batch processing (100 items per API call)
- Auto-trigger on profile/job updates
- Store in vector columns
- Admin batch generation endpoint
- OpenAI usage logging

**Story File:** `docs/stories/4.4.embedding-generation.md`

---

### Story 4.5: Job Matching Algorithm with pgvector
Core matching engine using cosine similarity

- `MatchingService` and `MatchingRepository`
- pgvector cosine similarity queries (`<=>` operator)
- Match score calculation and classification (Excellent/Great/Good/Fair)
- Preference filtering (location, work_setup, salary)
- Profile completeness gate (< 40% blocked)
- Match API endpoint

**Story File:** `docs/stories/4.5.job-matching-algorithm.md`

---

### Story 4.6: Match Explanation Generation with OpenAI
Explainable AI for match reasoning

- GPT-4 explanation generation
- Analyze: skill overlap, experience fit, preferences, gaps
- Structured JSON response (matching_factors, missing_requirements)
- 24-hour caching (in-memory or database)
- Timeout handling with fallback
- Explanation API endpoint

**Story File:** `docs/stories/4.6.match-explanations.md`

---

### Story 4.7: Frontend Profile Management Implementation
UI for candidate profile management

- TanStack Query hooks: profile, skills, preferences queries/mutations
- Zustand store for local state
- Profile pages: main, skills, preferences, resume
- Profile completeness widget (progress bar + actions)
- Optimistic updates for mutations
- Resume parsing status polling

**Story File:** `docs/stories/4.7.frontend-profile-ui.md`

---

### Story 4.8: Frontend Job Matching Implementation
AI-powered job recommendations UI

- TanStack Query hooks: job matches, explanations
- Zustand store for matching preferences
- Replace mock data in `/jobs/matches` with real API
- Match score badges (color-coded classifications)
- Collapsible match explanations
- Profile completeness gate UI
- Dashboard matched jobs widget

**Story File:** `docs/stories/4.8.frontend-matching-ui.md`

---

### Story 4.9: Batch Embedding Generation for Existing Data
Admin tooling for seeding embeddings

- CLI script: `backend/scripts/generate_embeddings.py`
- Query candidates (completeness >= 40%) and active jobs
- Batch processing (100 per API call)
- Progress logging, error handling
- Dry-run mode, idempotent execution
- OpenAI rate limit handling

**Story File:** `docs/stories/4.9.batch-embedding-generation.md`

---

### Story 4.10: Resume Upload & AI Evaluation
Full-featured resume upload with instant AI feedback

- PDF file upload with validation (5MB max, Supabase Storage)
- `pdfplumber` text extraction from uploaded PDFs
- AI-powered resume analysis (GPT-4o-mini): score, strengths, weaknesses, suggestions, missing keywords
- FastAPI BackgroundTasks for async analysis (non-blocking)
- Frontend drag-drop upload UI with progress indicators
- Analysis results modal with color-coded scores and actionable feedback
- Resume management: multiple versions, active/inactive, delete with cascade
- Security: JWT authentication, candidate isolation, private storage bucket

**Story File:** `docs/stories/4.10.resume-upload-ai-evaluation.md`

---

## Acceptance Criteria (Epic Level)

1. ✅ Candidates can create comprehensive profiles with skills, experience, and job preferences
2. ✅ Uploaded resumes are automatically parsed, extracting skills and experience into candidate profiles
3. ✅ Profile completeness score accurately reflects data availability and prompts candidates to complete missing sections
4. ✅ Semantic embeddings generated for all candidates (>= 40% completeness) and active job postings
5. ✅ Job matching API returns ranked matches using pgvector cosine similarity with <500ms latency
6. ✅ Match scores classified (Excellent/Great/Good/Fair) and filtered by candidate preferences
7. ✅ Match explanations provide specific, actionable reasoning for job-candidate pairs
8. ✅ Frontend profile pages display real data and update backend via API calls
9. ✅ `/jobs/matches` page shows AI-matched jobs with real scores and explanations
10. ✅ Dashboard displays accurate profile completion progress and matched job count
11. ✅ Existing Epic 01-03 functionality remains intact (backward compatibility verified)
12. ✅ Admin tooling available to seed embeddings for existing database records

---

## Technical Specifications

### Technology Stack

**Backend:**
- FastAPI (REST APIs)
- SQLAlchemy 2.x (ORM)
- Alembic (migrations)
- OpenAI Python SDK (GPT-4, text-embedding-3-large)
- pgvector (PostgreSQL extension)

**Frontend:**
- Next.js 14+ (App Router)
- React 18+
- Zustand 4.x (state management)
- TanStack Query v5 (data fetching)
- shadcn/ui + Tailwind CSS

**Database:**
- PostgreSQL 15+ (Supabase)
- pgvector extension with HNSW indexes

### Environment Variables

```bash
# New Variables
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_BATCH_SIZE=100

# Existing (reused)
OPENAI_API_KEY=<your-key>
DATABASE_URL=<supabase-connection-string>
```

### Performance Targets

- Resume parsing: < 30 seconds (5MB files)
- Embedding generation: < 3 seconds (single profile/job)
- Job matching query: < 500ms (10,000 jobs)
- Match explanation: < 5 seconds (with caching)

---

## Risk Assessment

### Technical Risks

1. **pgvector Performance**: May degrade with > 10k jobs
   - **Mitigation**: HNSW indexes, query monitoring, pagination if needed

2. **OpenAI Rate Limits**: Batch operations may hit limits
   - **Mitigation**: Exponential backoff, configurable batch size, job queuing

3. **Resume Parsing Failures**: Uncommon file formats
   - **Mitigation**: Graceful failure handling, manual skill entry fallback

### Integration Risks

1. **Schema Changes Break Existing APIs**: Profile columns affect queries
   - **Mitigation**: All columns nullable with defaults, manual regression testing

2. **Embedding Cost Explosion**: Frequent regeneration
   - **Mitigation**: Cache embeddings, only regenerate on meaningful changes

### Mitigation Strategies

- **Phased Deployment**: Backend + migration → frontend updates
- **Feature Flags**: Environment variable to enable/disable matching
- **Monitoring**: OpenAI usage, pgvector query performance, parsing success rate
- **Rollback Plan**: Alembic downgrade ready, frontend can revert to mock data

---

## Success Metrics

### User Engagement
- Profile completion rate: Target > 60% of registered candidates
- Resume upload rate: Target > 50% of registered candidates
- Job match interactions: Clicks on match explanations, applications from matches

### System Performance
- Average job matching query time: < 300ms
- Resume parsing success rate: > 90%
- Profile completeness score accuracy: ±5% manual validation

### Business Impact
- Increase in applications per candidate (matched jobs vs manual browsing)
- Reduction in time-to-apply (profile setup → first application)
- Candidate satisfaction with match quality (future survey metric)

---

## Deployment Plan

### Phase 1: Backend + Database (Stories 4.1-4.6)
1. Deploy Story 4.1 migration (enable pgvector, extend schema)
2. Verify backward compatibility with Epic 01-03 APIs
3. Deploy Stories 4.2-4.6 (services, APIs)
4. Run Story 4.9 batch script to seed embeddings for existing data
5. Manual testing of all backend endpoints

### Phase 2: Frontend (Stories 4.7-4.8)
1. Deploy Story 4.7 (profile UI)
2. Manual testing of profile workflows
3. Deploy Story 4.8 (matching UI)
4. End-to-end testing of complete matching flow
5. Monitor OpenAI usage and pgvector performance

### Rollback Procedures
- **Database**: Alembic downgrade to pre-Epic-04 schema
- **Backend**: Revert to previous deployment, disable matching endpoints
- **Frontend**: Environment flag to revert to mock data for `/jobs/matches`

---

## Dependencies

### Prerequisites
- ✅ Epic 01 completed (authentication, candidates, resumes, interviews)
- ✅ Epic 02 completed (video interviews - optional, no direct dependency)
- ✅ Epic 03 completed (job postings, applications)

### External Dependencies
- OpenAI API access (GPT-4, text-embedding-3-large)
- Supabase PostgreSQL with pgvector extension support

### Team Dependencies
- None (single epic, sequential story execution)

---

## Cost Estimation

### OpenAI API Costs (Monthly, Estimated)

**Assumptions:**
- 1,000 new candidates/month
- 100 new job postings/month
- 500 match explanations/month

**Breakdown:**
- Profile embeddings: 1,000 × $0.000026 = **$0.026**
- Job embeddings: 100 × $0.000052 = **$0.0052**
- Resume parsing: 500 × $0.002 (GPT-4) = **$1.00**
- Match explanations: 500 × $0.0001 (GPT-4 mini) = **$0.05**

**Total Monthly Cost: ~$1.08** (negligible)

### Infrastructure Costs
- No additional infrastructure required (existing Supabase, Vercel)
- pgvector extension: Free in Supabase

---

## Future Enhancements (Post-Epic)

1. **Cron Job for Automatic Embedding Updates**: Replace manual admin endpoint with scheduled job
2. **Advanced Filtering**: Industry, company size, tech stack preferences
3. **Candidate Alerts**: Email/push notifications for new matched jobs
4. **Recruiter Dashboard**: View candidate-job matches from recruiter perspective
5. **Match History**: Track match quality over time, A/B test matching algorithms
6. **Skills Taxonomy**: Normalize skills (React = React.js), suggest synonyms
7. **Experience Parsing**: Extract detailed work history from resumes, not just years

---

## Related Documentation

- **PRD**: `docs/prds/09-intelligent-job-matching.md`
- **Stories**: `docs/stories/4.*.md`
- **Architecture**: `docs/architecture/backend/`, `docs/architecture/frontend/`
- **Database Schema**: `docs/architecture/backend/08-database-schema.md`

---

**Epic Created:** November 6, 2025  
**PM:** John (PM Agent)  
**Status:** Ready for Story 4.1 Development
