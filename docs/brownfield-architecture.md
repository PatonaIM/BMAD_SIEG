# Teamified AI Interview Platform - Brownfield Architecture Document

> **Document Type:** Current State Analysis for AI Agents  
> **Last Updated:** November 1, 2025  
> **Purpose:** Enable AI agents to understand the ACTUAL implemented system for Story 1.8 completion  
> **Status:** POC Implementation - Epic 01 & 01.5 (Speech) Near Complete

---

## Document Scope

**Current Focus:** Implementing Story 1.8 (Interview Completion & Basic Results) to complete the AI Interview POC.

This document captures the **real implementation state** including:
- What's actually built and working (Stories 1.1-1.7, 1.5.1-1.5.4)
- What needs to be implemented (Story 1.8)
- Current architecture patterns and conventions
- Known gaps and technical considerations

**For AI Agents:** Use this document to understand what exists before implementing Story 1.8.

---

## Change Log

| Date       | Version | Description                                    | Author  |
|------------|---------|------------------------------------------------|---------|
| 2025-11-01 | 1.0     | Initial brownfield analysis for Story 1.8 work | Winston |

---

## Table of Contents

1. [Quick Reference - What's Built](#quick-reference---whats-built)
2. [Project Structure Reality](#project-structure-reality)
3. [Current Implementation Status](#current-implementation-status)
4. [Tech Stack - Actual Versions](#tech-stack---actual-versions)
5. [Database Schema - Current State](#database-schema---current-state)
6. [Backend Architecture - As Implemented](#backend-architecture---as-implemented)
7. [Frontend Architecture - As Implemented](#frontend-architecture---as-implemented)
8. [API Endpoints - What Exists](#api-endpoints---what-exists)
9. [Story 1.8 - What Needs Implementation](#story-18---what-needs-implementation)
10. [Development Environment](#development-environment)
11. [Known Issues and Gotchas](#known-issues-and-gotchas)

---

## Quick Reference - What's Built

### Critical Files for Story 1.8

**Backend (Python/FastAPI):**
- `backend/main.py` - Application entrypoint
- `backend/app/services/interview_engine.py` - Core interview logic (HAS `_should_complete_interview()` method)
- `backend/app/api/v1/interviews.py` - Interview API endpoints (NEEDS completion endpoint)
- `backend/app/repositories/interview.py` - Interview database operations
- `backend/app/schemas/interview.py` - API request/response models (NEEDS completion schemas)
- `backend/app/models/interview.py` - SQLAlchemy Interview model (has status field)

**Frontend (Next.js 16/React/TypeScript):**
- `frontend/app/interview/[sessionId]/page.tsx` - Interview UI (NEEDS completion detection)
- `frontend/app/interview/[sessionId]/results/page.tsx` - NEEDS CREATION (completion screen)

**Key Models Already Built:**
- `Interview` - Main interview record with status tracking
- `InterviewSession` - Session state with progression tracking
- `InterviewMessage` - Question/response history
- `Candidate` - User authentication

---

## Project Structure Reality

```
/Users/teamified_ph/Codes/BMAD_Sieg/
├── backend/                        # FastAPI Python backend
│   ├── main.py                     # App entrypoint with CORS, lifespan
│   ├── alembic.ini                 # Database migrations config
│   ├── pyproject.toml              # Python dependencies (uv)
│   ├── requirements.txt            # Pip fallback
│   └── app/
│       ├── api/
│       │   └── v1/
│       │       ├── auth.py         # ✅ Login/Register endpoints
│       │       ├── interviews.py   # ✅ Start, SendMessage | ⚠️ NEEDS Complete endpoint
│       │       └── audio.py        # ✅ STT/TTS endpoints
│       ├── core/
│       │   ├── config.py           # ✅ Settings with OpenAI config
│       │   ├── database.py         # ✅ AsyncPG connection
│       │   └── exceptions.py       # ✅ Custom exception hierarchy
│       ├── models/                 # ✅ SQLAlchemy models complete
│       │   ├── candidate.py
│       │   ├── interview.py        # Has status field: scheduled, in_progress, completed, abandoned
│       │   ├── interview_session.py
│       │   ├── interview_message.py
│       │   └── resume.py
│       ├── providers/              # ✅ AI/Speech provider abstractions
│       │   ├── base_ai_provider.py
│       │   ├── openai_provider.py
│       │   ├── speech_provider.py
│       │   └── openai_speech_provider.py
│       ├── repositories/           # ✅ Database access layer
│       │   ├── interview.py
│       │   ├── interview_session.py
│       │   └── interview_message.py
│       ├── schemas/                # ⚠️ NEEDS completion schemas
│       │   ├── auth.py
│       │   ├── interview.py        # Has InterviewStartRequest, SendMessageRequest
│       │   └── speech.py
│       ├── services/               # ⚠️ NEEDS complete_interview() method
│       │   ├── interview_engine.py # Has _should_complete_interview()
│       │   ├── progressive_assessment_engine.py
│       │   ├── conversation_memory.py
│       │   ├── speech_service.py
│       │   └── auth_service.py
│       └── prompts/                # ✅ AI prompt templates
│           ├── response_analysis.txt
│           └── adaptive_question.txt
│
├── frontend/                       # Next.js 16 React TypeScript
│   ├── next.config.mjs
│   ├── package.json                # npm/pnpm dependencies
│   ├── tsconfig.json
│   └── app/
│       ├── layout.tsx              # ✅ Root layout with providers
│       ├── page.tsx                # ✅ Landing page
│       ├── login/                  # ✅ Login flow
│       ├── register/               # ✅ Registration
│       ├── dashboard/              # ✅ Candidate dashboard
│       └── interview/
│           ├── start/              # ✅ Interview setup
│           ├── practice/           # ✅ Practice mode
│           └── [sessionId]/
│               ├── page.tsx        # ✅ Active interview UI
│               └── results/        # ⚠️ NEEDS CREATION
│                   └── page.tsx
│
└── docs/
    ├── prd.md                      # PRD index (sharded)
    ├── prds/                       # ✅ Complete PRD sections
    ├── epics/                      # ✅ Epic 01 & 01.5 defined
    ├── stories/                    # ✅ Stories 1.1-1.7, 1.5.1-1.5.4 complete
    │   └── 1.8.interview-completion-basic-results.md  # ⚠️ IN PROGRESS
    └── architecture/
        ├── backend/                # ✅ Complete backend architecture
        └── frontend/               # ✅ Complete frontend architecture
```

---

## Current Implementation Status

### ✅ Completed Stories (Working)

| Story | Description | Status | Files |
|-------|-------------|--------|-------|
| 1.1 | Project Initialization | ✅ Complete | `pyproject.toml`, `package.json` |
| 1.2 | Database Schema & Models | ✅ Complete | `app/models/*`, `alembic/versions/*` |
| 1.3 | Authentication & Sessions | ✅ Complete | `app/api/v1/auth.py`, `app/services/auth_service.py` |
| 1.4 | OpenAI & LangChain Setup | ✅ Complete | `app/providers/openai_provider.py` |
| 1.5 | Progressive Assessment Engine | ✅ Complete | `app/services/progressive_assessment_engine.py` |
| 1.6 | Interview UI - Text Chat | ✅ Complete | `frontend/app/interview/[sessionId]/page.tsx` |
| 1.7 | Real-Time Conversation Flow | ✅ Complete | `app/api/v1/interviews.py`, `app/services/interview_engine.py` |
| 1.5.1 | OpenAI Speech Integration | ✅ Complete | `app/providers/openai_speech_provider.py` |
| 1.5.3 | Speech-to-Text Pipeline | ✅ Complete | `app/api/v1/audio.py`, `app/services/speech_service.py` |
| 1.5.4 | Text-to-Speech Generation | ✅ Complete | `app/api/v1/audio.py` (TTS endpoint) |

### ⚠️ Current Work (Story 1.8)

**Story 1.8: Interview Completion & Basic Results** - **IN PROGRESS**

**What's Already There:**
- ✅ `_should_complete_interview()` method exists in `interview_engine.py` (line 442)
- ✅ Interview model has `status` field with enum: `scheduled`, `in_progress`, `completed`, `abandoned`
- ✅ Database schema supports completion tracking (`completed_at`, `duration_seconds`)
- ✅ `SendMessageResponse` returns completion flag in interview flow

**What Needs Implementation:**
- ❌ `POST /api/v1/interviews/{id}/complete` endpoint
- ❌ `complete_interview()` method in `InterviewEngine`
- ❌ `GET /api/v1/interviews/{id}/transcript` endpoint
- ❌ Completion response schemas in `app/schemas/interview.py`
- ❌ Frontend completion page: `frontend/app/interview/[sessionId]/results/page.tsx`
- ❌ Frontend completion detection and navigation

### 🚧 Not Started (Future)

- Story 1.5.5-1.5.9: Voice UI enhancements, WebRTC, hybrid mode
- Story 1.9: CI/CD Pipeline
- Epic 02+: Recruiter portal, scoring, advanced features

---

## Tech Stack - Actual Versions

### Backend (Python)

```toml
# From backend/pyproject.toml
requires-python = ">=3.11.9"

[dependencies]
fastapi = "0.104.1"              # Web framework
uvicorn[standard] = ">=0.24"     # ASGI server
sqlalchemy = ">=2.0"             # ORM with AsyncPG
asyncpg = ">=0.29"               # PostgreSQL async driver
alembic = ">=1.12"               # Database migrations
pydantic = ">=2.5"               # Data validation
pydantic-settings = ">=2.1"      # Config management
python-jose[cryptography]        # JWT tokens
passlib[bcrypt]                  # Password hashing
langchain = ">=0.1.0"            # LLM framework
langchain-openai = ">=0.0.5"     # OpenAI integration
openai = ">=1.0.0"               # OpenAI API client
tiktoken = ">=0.5.0"             # Token counting
httpx = ">=0.25"                 # HTTP client for APIs
structlog = ">=23.2"             # Structured logging
aiohttp = ">=3.13.2"             # Async HTTP
aiofiles = ">=25.1.0"            # Async file I/O
```

**Development Tools:**
- `pytest` + `pytest-asyncio` - Testing
- `ruff` - Linting (replaces flake8, isort)
- `black` - Code formatting
- `mypy` - Type checking

### Frontend (TypeScript/React)

```json
// From frontend/package.json
"dependencies": {
  "next": "16.0.1",                      // Next.js App Router
  "react": "^19.1.1",                    // React 19
  "react-dom": "^19.1.1",
  "@tanstack/react-query": "latest",     // Data fetching
  "zustand": "latest",                   // State management
  "@radix-ui/*": "latest",               // UI primitives (20+ packages)
  "@mui/material": "latest",             // Material-UI components
  "framer-motion": "latest",             // Animations
  "react-hook-form": "latest",           // Form handling
  "zod": "^4.1.12",                      // Schema validation
  "lucide-react": "^0.454.0",            // Icons
  "tailwindcss": "^4.1.9"                // Styling
}
```

**Development Tools:**
- `vitest` - Unit testing
- `eslint` + `prettier` - Code quality
- `typescript` - Type safety

### Database

- **PostgreSQL 15+** (Supabase hosted for MVP)
- **Alembic** for migrations
- **AsyncPG** driver for async operations

### AI Services

- **OpenAI GPT-4o-mini** - Interview conversations (`gpt-4o-mini`)
- **OpenAI Whisper** - Speech-to-text (`whisper-1`)
- **OpenAI TTS** - Text-to-speech (`tts-1`, voice: `alloy`)

---

## Database Schema - Current State

### Core Tables (Implemented)

**candidates**
```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, deleted
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**interviews**
```sql
CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE SET NULL,
    role_type VARCHAR(50) NOT NULL,  -- react, python, javascript, fullstack
    status VARCHAR(20) DEFAULT 'scheduled',  -- scheduled, in_progress, completed, abandoned
    started_at TIMESTAMP,
    completed_at TIMESTAMP,           -- ⚠️ Set by Story 1.8
    duration_seconds INTEGER,          -- ⚠️ Set by Story 1.8
    ai_model_used VARCHAR(50),
    total_tokens_used INTEGER DEFAULT 0,
    cost_usd NUMERIC(10,4) DEFAULT 0.0,
    speech_tokens_used INTEGER DEFAULT 0,
    speech_cost_usd NUMERIC(10,4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX idx_interviews_status ON interviews(status);
```

**interview_sessions**
```sql
CREATE TABLE interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    current_difficulty_level VARCHAR(20) DEFAULT 'warmup',  -- warmup, standard, advanced
    questions_asked_count INTEGER DEFAULT 0,
    skill_boundaries_identified JSONB DEFAULT '{}',
    progression_state JSONB DEFAULT '{}',  -- Phase history, quality tracking
    conversation_memory JSONB DEFAULT '{}',  -- LangChain memory
    last_activity_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_sessions_interview_id ON interview_sessions(interview_id);
```

**interview_messages**
```sql
CREATE TABLE interview_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,
    message_type VARCHAR(20) NOT NULL,  -- ai_question, candidate_response
    content_text TEXT NOT NULL,
    audio_url VARCHAR(500),
    audio_metadata JSONB,  -- STT confidence, duration, etc.
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_messages_interview_id ON interview_messages(interview_id);
CREATE INDEX idx_messages_sequence ON interview_messages(interview_id, sequence_number);
```

**Key Relationships:**
- `candidate` → many `interviews`
- `interview` → one `interview_session` (1:1)
- `interview` → many `interview_messages`
- `interview_session` tracks progression state and conversation memory

---

## Backend Architecture - As Implemented

### Service Layer Pattern (Clean Architecture)

```
API Layer (FastAPI Routes)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Database Access)
    ↓
Database (PostgreSQL)
```

### Key Services

**1. InterviewEngine** (`app/services/interview_engine.py`)
- **Current State:** Handles interview orchestration, integrates Progressive Assessment
- **Key Methods:**
  - ✅ `start_interview()` - Creates session with warmup difficulty
  - ✅ `process_candidate_response()` - Analyzes response, generates next question
  - ✅ `_should_complete_interview()` - **EXISTS** - Checks completion criteria
  - ❌ `complete_interview()` - **NEEDS IMPLEMENTATION** (Story 1.8 Task 3)

**Completion Logic Already Built:**
```python
async def _should_complete_interview(self, session: InterviewSession) -> bool:
    """Check if interview should complete based on criteria."""
    # Line 442 in interview_engine.py
    # Checks: min questions (12), max questions (20), all phases complete
```

**2. ProgressiveAssessmentEngine** (`app/services/progressive_assessment_engine.py`)
- ✅ Three-phase difficulty progression: warmup → standard → advanced
- ✅ AI-powered response analysis
- ✅ Automatic difficulty advancement based on performance
- ✅ Skill boundary detection to avoid re-testing

**3. SpeechService** (`app/services/speech_service.py`)
- ✅ STT/TTS orchestration with OpenAI
- ✅ Cost tracking for speech services
- ✅ Audio validation and quality checks

**4. ConversationMemoryManager** (`app/services/conversation_memory.py`)
- ✅ LangChain conversation memory management
- ✅ Token optimization with memory pruning

### Provider Abstraction

**Pattern:** Abstract base classes for easy provider swapping

```python
# app/providers/base_ai_provider.py
class AIProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list, **kwargs) -> str: ...

# app/providers/speech_provider.py
class SpeechProvider(ABC):
    @abstractmethod
    async def transcribe_audio(self, audio_data: bytes) -> TranscriptionResult: ...
    @abstractmethod
    async def synthesize_speech(self, text: str) -> bytes: ...
```

**Current Implementations:**
- ✅ `OpenAIProvider` - GPT-4o-mini completions
- ✅ `OpenAISpeechProvider` - Whisper STT + TTS

---

## Frontend Architecture - As Implemented

### Next.js 16 App Router

**Migration Complete:** Migrated from Vite SPA to Next.js 16 with App Router (October 2025)

**Route Structure:**
```
app/
├── layout.tsx                    # Root layout with auth providers
├── page.tsx                      # Landing page
├── login/page.tsx               # ✅ Login flow
├── register/page.tsx            # ✅ Registration
├── dashboard/page.tsx           # ✅ Candidate dashboard
└── interview/
    ├── start/page.tsx           # ✅ Interview setup
    └── [sessionId]/
        ├── page.tsx             # ✅ Active interview UI
        └── results/
            └── page.tsx         # ⚠️ NEEDS CREATION (Story 1.8 Task 5)
```

### State Management

**Pattern:** Zustand stores for client state, React Query for server state

**Current Stores:**
- ✅ `useAuthStore` - Authentication state
- ✅ `useInterviewStore` - Interview session state
- ⚠️ May need completion state management

### API Integration

**Pattern:** React Query hooks with TypeScript fetch wrappers

```typescript
// Example pattern from existing code
const { mutate: sendMessage } = useMutation({
  mutationFn: async (data: SendMessageRequest) => {
    const res = await fetch(`/api/v1/interviews/${sessionId}/messages`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(data)
    });
    return res.json();
  }
});
```

### UI Component Library

- **Radix UI** - Accessible primitives (Dialog, Popover, etc.)
- **MUI Material** - Complex components (DataGrid, Autocomplete)
- **Tailwind CSS** - Styling utility classes
- **Framer Motion** - Animations

---

## API Endpoints - What Exists

### ✅ Implemented Endpoints

**Authentication** (`/api/v1/auth`)
```
POST   /api/v1/auth/register       # Register new candidate
POST   /api/v1/auth/login          # Login and get JWT token
GET    /api/v1/auth/me             # Get current user profile
```

**Interviews** (`/api/v1/interviews`)
```
POST   /api/v1/interviews/start    # Start interview, get first question
POST   /api/v1/interviews/{id}/messages  # Send candidate response, get next AI question
GET    /api/v1/interviews/{id}     # Get interview details
```

**Audio** (`/api/v1/audio`)
```
POST   /api/v1/interviews/{id}/audio          # Upload audio, get transcription
GET    /api/v1/interviews/{id}/audio/{msg_id} # Get TTS audio for AI message
```

### ⚠️ Needs Implementation (Story 1.8)

**Interview Completion** (Task 2)
```
POST   /api/v1/interviews/{id}/complete   # Mark interview complete
```

**Request:** None (just interview_id in path)

**Response:**
```typescript
{
  interview_id: string;          // UUID
  completed_at: string;          // ISO timestamp
  duration_seconds: number;
  questions_answered: number;
  skill_boundaries_identified: number;
  message: string;               // "Interview completed successfully"
}
```

**Interview Transcript** (Task 4)
```
GET    /api/v1/interviews/{id}/transcript   # Get full conversation history
```

**Response:**
```typescript
{
  interview_id: string;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  messages: Array<{
    sequence_number: number;
    message_type: "ai_question" | "candidate_response";
    content_text: string;
    created_at: string;
    audio_url?: string;
  }>;
}
```

---

## Story 1.8 - What Needs Implementation

### Task Breakdown (From Story Document)

**Task 1: Completion Detection Logic** ✅ ALREADY EXISTS
- `_should_complete_interview()` method exists at line 442 in `interview_engine.py`
- Checks: min 12 questions, max 20 questions, all phases complete
- Returns boolean completion flag
- **Action:** Verify it's called correctly in `process_candidate_response()`

**Task 2: Create Completion API Endpoint** ❌ NEEDS IMPLEMENTATION
- **File:** `backend/app/api/v1/interviews.py`
- **Endpoint:** `POST /api/v1/interviews/{id}/complete`
- **Auth:** JWT required via `get_current_user`
- **Validation:** Check candidate owns interview, interview is `in_progress`
- **Action:** Call `InterviewEngine.complete_interview()` service method
- **Response:** `InterviewCompleteResponse` schema

**Task 3: Implement `complete_interview()` Method** ❌ NEEDS IMPLEMENTATION
- **File:** `backend/app/services/interview_engine.py`
- **Method:** `async def complete_interview(interview_id: UUID) -> InterviewCompleteResponse`
- **Logic:**
  1. Load interview and session from repositories
  2. Calculate metrics: duration, questions answered, skill boundaries
  3. Update interview: `status='completed'`, `completed_at`, `duration_seconds`
  4. Commit to database
  5. Return structured response
- **Error Handling:** 404 if not found, 400 if already completed

**Task 4: Create Transcript API Endpoint** ❌ NEEDS IMPLEMENTATION
- **File:** `backend/app/api/v1/interviews.py`
- **Endpoint:** `GET /api/v1/interviews/{id}/transcript`
- **Auth:** JWT required
- **Data:** Fetch all `interview_messages` ordered by `sequence_number`
- **Response:** `InterviewTranscriptResponse` schema with message list
- **Optimization:** Add pagination if > 100 messages (query params: skip, limit)

**Task 5: Create Completion Frontend Page** ❌ NEEDS IMPLEMENTATION
- **File:** `frontend/app/interview/[sessionId]/results/page.tsx`
- **Design:**
  - Success checkmark icon (use `lucide-react` icons)
  - "Thank You!" heading
  - Completion summary card:
    - Duration (formatted: "30 minutes 45 seconds")
    - Questions answered count
    - Completion timestamp
  - Next steps message ("You'll receive results within 24 hours")
  - "Return to Dashboard" button
- **Data Fetching:** Call completion endpoint, then display results
- **Routing:** Navigate here after `should_complete=true` in SendMessageResponse

**Task 6: Update Interview UI for Completion Detection** ❌ NEEDS IMPLEMENTATION
- **File:** `frontend/app/interview/[sessionId]/page.tsx`
- **Logic:** Check `should_complete` flag in `SendMessageResponse`
- **Action:** If true, navigate to `/interview/{sessionId}/results`
- **Implementation:** Use Next.js `useRouter()` for navigation

---

## Development Environment

### Local Setup (Already Done)

**Backend:**
```bash
cd backend
source .venv/bin/activate  # Virtual environment active
uv run uvicorn main:app --reload  # Running on http://localhost:8000
```

> **⚠️ Important:** Always use `uv run` prefix for Python commands to ensure proper dependency management.

**Frontend:**
```bash
cd frontend
npm run dev  # Running on http://localhost:3000
```

**Database:**
- PostgreSQL hosted on Supabase
- Connection via environment variables in `backend/.env`
- Migrations via Alembic: `alembic upgrade head`

### Environment Variables

**Backend** (`backend/.env`):
```bash
# Database
DB_USER=postgres
DB_PASSWORD=[redacted]
DB_HOST=db.supabase.co
DB_PORT=5432
DB_NAME=postgres

# OpenAI
OPENAI_API_KEY=[redacted]
OPENAI_MODEL=gpt-4o-mini
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy
OPENAI_STT_MODEL=whisper-1

# Auth
JWT_SECRET=[redacted]
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend** (`frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Testing

**Backend Tests:**
```bash
cd backend
pytest                          # Run all tests
pytest tests/unit              # Unit tests only
pytest tests/integration       # Integration tests
pytest --cov=app              # With coverage
```

**Frontend Tests:**
```bash
cd frontend
npm test                       # Run Vitest
npm run test:coverage         # With coverage
npm run test:ui               # Interactive UI
```

---

## Known Issues and Gotchas

### 1. Interview Status Transitions

**Current Behavior:**
- Interview starts with `status='in_progress'` (not 'scheduled')
- File: `backend/app/api/v1/interviews.py` line 66

```python
interview = Interview(
    status="in_progress",  # Changed from "scheduled" in Story 1.7
    # ...
)
```

**Story 1.8 Impact:**
- Completion endpoint should check `status == 'in_progress'` before completing
- Reject if already `'completed'` or `'abandoned'`

### 2. Completion Detection Called but Not Used

**Current State:** `_should_complete_interview()` is called at line 419 in `interview_engine.py`:

```python
should_complete = await self._should_complete_interview(session)
return {
    "ai_question": next_question["question"],
    "should_complete": should_complete,  # Returned but frontend doesn't act on it
    # ...
}
```

**Story 1.8 Fix:**
- Frontend needs to check `should_complete` flag in response
- Navigate to completion page when `true`

### 3. No Explicit Completion Endpoint Yet

**Current Workaround:** Interview completes when candidate stops responding

**Story 1.8 Change:**
- Add explicit `POST /api/v1/interviews/{id}/complete` endpoint
- Frontend calls this after detecting `should_complete=true`
- Backend updates status and persists completion data

### 4. Transcript Endpoint Missing

**Current State:** No way to retrieve full conversation history via API

**Story 1.8 Addition:**
- Create `GET /api/v1/interviews/{id}/transcript` endpoint
- Useful for completion screen and future recruiter portal
- Consider pagination for long interviews (20+ messages)

### 5. Frontend Route Doesn't Exist

**Current State:** No `/interview/[sessionId]/results` page

**Story 1.8 Creation:**
- Must create `frontend/app/interview/[sessionId]/results/page.tsx`
- Use Next.js App Router conventions
- Server-side fetch completion data or client-side with React Query

### 6. Duration Calculation

**Implementation Detail:**
- Interview model has `started_at` field (set on interview start)
- Need to calculate `duration_seconds = (completed_at - started_at).total_seconds()`
- Round to nearest second for display

**Formatting for Frontend:**
```typescript
// Helper function needed in frontend
function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins} minutes ${secs} seconds`;
}
```

### 7. Skill Boundaries Count

**Data Location:** `interview_session.skill_boundaries_identified` (JSONB)

**Current Structure:**
```json
{
  "react_hooks": {
    "proficiency": "advanced",
    "boundary_type": "knowledge_gap",
    "detected_at_question": 8
  },
  "async_patterns": {
    "proficiency": "proficient",
    "boundary_type": "confidence_limit",
    "detected_at_question": 12
  }
}
```

**Calculation:** `len(session.skill_boundaries_identified.keys())`

### 8. JWT Token Handling

**Current Pattern:** Frontend stores JWT in localStorage/Zustand

**Story 1.8 Endpoints:** Both completion and transcript endpoints require JWT

**Auth Pattern:**
```typescript
const token = localStorage.getItem('auth_token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

### 9. Error Handling Patterns

**Backend Pattern:**
```python
# Custom exceptions in app/core/exceptions.py
raise InterviewNotFoundException(interview_id=interview_id)
raise InterviewCompletedException(interview_id=interview_id)

# Exception handlers in main.py return appropriate HTTP status
```

**Frontend Pattern:**
```typescript
try {
  const response = await fetch(...);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }
  return await response.json();
} catch (error) {
  console.error('API error:', error);
  // Show toast notification or error UI
}
```

### 10. Alembic Migrations

**Current State:** No migration needed for Story 1.8 (fields already exist)

**If Schema Changes Needed:**
```bash
cd backend
alembic revision --autogenerate -m "Add completion fields"
alembic upgrade head
```

---

## Next Steps for Story 1.8 Implementation

### Implementation Order (Recommended)

1. **Backend - Schemas** (Easiest first)
   - Add `InterviewCompleteResponse` to `app/schemas/interview.py`
   - Add `InterviewTranscriptResponse` and `TranscriptMessage` schemas

2. **Backend - Service Method**
   - Implement `InterviewEngine.complete_interview()` in `interview_engine.py`
   - Write unit tests for completion logic

3. **Backend - API Endpoints**
   - Add `POST /api/v1/interviews/{id}/complete` in `interviews.py`
   - Add `GET /api/v1/interviews/{id}/transcript` in `interviews.py`
   - Test with curl or Postman

4. **Frontend - Completion Page**
   - Create `app/interview/[sessionId]/results/page.tsx`
   - Design completion UI with success message and summary
   - Add "Return to Dashboard" button

5. **Frontend - Navigation Logic**
   - Update `app/interview/[sessionId]/page.tsx`
   - Check `should_complete` flag after sending message
   - Navigate to results page when true

6. **Testing**
   - Backend integration tests for completion flow
   - Frontend E2E test for full interview → completion
   - Manual testing of complete user journey

### Success Criteria Checklist

- [ ] Interview completion detected after 12+ questions and phase completion
- [ ] `POST /api/v1/interviews/{id}/complete` endpoint returns completion data
- [ ] Interview status updated to "completed" in database
- [ ] Completion page displays duration, question count, and next steps
- [ ] Transcript endpoint returns full conversation history
- [ ] Frontend navigation to completion page works automatically
- [ ] Cannot submit new messages after interview completed
- [ ] All tests pass

---

## Appendix - Useful Commands

### Backend Development

```bash
# Start development server (⚠️ ALWAYS use 'uv run' prefix)
cd backend
source .venv/bin/activate
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest
pytest tests/unit/test_interview_engine.py -v
pytest --cov=app --cov-report=html

# Database migrations
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "description"

# Linting and formatting
ruff check app/
black app/
mypy app/
```

### Frontend Development

```bash
# Start development server
cd frontend
npm run dev

# Run tests
npm test
npm run test:coverage
npm run test:ui

# Linting and formatting
npm run lint
npm run lint:fix
npm run format
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Start interview (requires JWT token)
curl -X POST http://localhost:8000/api/v1/interviews/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"role_type":"react"}'
```

---

## Document Metadata

**Author:** Winston (Architect Agent)  
**Created:** November 1, 2025  
**Purpose:** Enable AI agents to implement Story 1.8 with full understanding of current system state  
**Maintenance:** Update after significant implementation changes or architectural decisions  

**Related Documents:**
- `docs/prd.md` - Product Requirements (sharded)
- `docs/epics/epic-01-foundation.md` - Epic 01 definition
- `docs/stories/1.8.interview-completion-basic-results.md` - Story 1.8 detailed requirements
- `docs/architecture/backend/` - Backend architecture (sharded)
- `docs/architecture/frontend/` - Frontend architecture
- `README.md` - Project setup and installation

---

**End of Brownfield Architecture Document**
