# Teamified Candidates Portal Backend Architecture Document

## Introduction

This document outlines the backend architecture for **Teamified Candidates Portal**, including server-side systems, AI services integration, database design, API specifications, and infrastructure. Its primary goal is to serve as the guiding architectural blueprint for AI-driven backend development, ensuring consistency and adherence to chosen patterns and technologies.

**Relationship to Frontend Architecture:**

This backend architecture works in conjunction with the existing [Frontend Architecture Document](ui-architecture.md). The frontend handles user interactions, real-time audio capture, and visual components, while this backend architecture manages:
- AI interview orchestration (OpenAI GPT-4 via LangChain)
- Speech processing (OpenAI Whisper STT + OpenAI TTS)
- Assessment scoring and integrity analysis
- Resume parsing and candidate data management
- RESTful APIs and external integrations
- Database persistence and state management

Core technology stack choices documented in the "Tech Stack" section are definitive for the entire project.

### Starter Template or Existing Project

**Backend Framework: FastAPI with Python 3.11.9**

- **Rationale:** Modern async Python framework with automatic OpenAPI documentation, excellent for AI service integration
- **Starting Point:** Clean FastAPI project structure (no boilerplate starter)
- **Key Benefits:** 
  - Native async/await for concurrent interview sessions
  - Type hints align with Python 3.11+ features
  - Auto-generated API documentation reduces manual specification work
  - Excellent integration with LangChain for AI orchestration

**Project Structure Approach:** Monorepo with `/frontend` and `/backend` directories as specified in PRD Epic 1, Story 1.1.

**Package Management:** UV for fast, deterministic dependency management and virtual environment handling.

**AI Services Strategy:** OpenAI for MVP (Whisper STT, TTS API, GPT-4) with provider-agnostic abstraction layer enabling future migration to Azure/GCP alternatives without frontend changes.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-28 | 1.0 | Initial backend architecture document creation | Winston (Architect) |

---


## High Level Architecture

### Technical Summary

Teamified Candidates Portal backend follows a **monolithic architecture with microservices-ready design**, leveraging Python 3.11.9 and FastAPI for high-performance async operations. The system orchestrates AI-driven technical interviews through OpenAI GPT-4 (via LangChain), processes speech using OpenAI Whisper/TTS, and persists data in PostgreSQL (Supabase). Key architectural patterns include Repository Pattern for data access, Service Layer for business logic, and provider-agnostic abstractions for AI services enabling future cloud migration. This design supports the PRD's goal of 50+ concurrent interview sessions with <2 second AI response times while maintaining clear boundaries for eventual microservices extraction.

### High Level Overview

**1. Architectural Style: Modular Monolith**

The backend implements a **modular monolithic architecture** with clear internal boundaries designed for future microservices extraction. This approach:

- Simplifies MVP development and deployment (single service to manage)
- Reduces operational complexity during bootstrap/self-funded phase
- Maintains clean separation of concerns through internal modules
- Enables linear scaling characteristics for 500+ interviews/month (NFR12)
- Provides clear migration path when scale demands distributed architecture

**2. Repository Structure: Monorepo**

Single repository containing `/frontend` and `/backend` as specified in PRD, enabling:
- Atomic commits across full-stack features
- Simplified dependency management
- Reduced context switching for small team (2-4 developers)

**3. Service Architecture Decision**

**Identified Architectural Boundaries (Future Microservices):**
- **AI Interview Engine** - Conversational AI, adaptive questioning, real-time scoring
- **Resume Parser Service** - Batch processing for resume analysis and skill extraction
- **Assessment Scoring Service** - Integrity analysis, skill boundary mapping, report generation
- **Integration API Gateway** - External ATS/HRIS connectivity and webhook management
- **Speech Processing Service** - OpenAI Whisper/TTS integration with provider abstraction

**Current MVP Approach:** These exist as internal modules with well-defined interfaces, deployed as a single FastAPI application.

**4. Primary Data Flow**

```
Candidate → Frontend (React) → Backend API (FastAPI)
                                      ↓
                        ┌─────────────┴──────────────┐
                        ↓                            ↓
                 AI Interview Engine          Speech Processing
                 (LangChain + GPT-4)         (Whisper + TTS)
                        ↓                            ↓
                 Assessment Scoring            Audio Metadata
                        ↓                            ↓
                        └─────────────┬──────────────┘
                                      ↓
                              PostgreSQL (Supabase)
                                      ↓
                        Recruiter Portal / ATS APIs
```

**5. Key Architectural Decisions**

- **OpenAI as Primary AI Provider** - Single vendor for LLM + Speech simplifies MVP
- **LangChain for AI Orchestration** - Manages conversation memory, prompt templates, token optimization
- **Provider Abstraction Layer** - Clean interfaces enable Azure/GCP migration without breaking changes
- **PostgreSQL with JSONB** - Flexible schema for AI-generated data (scores, reasoning, red flags)
- **Async FastAPI** - Native async/await critical for concurrent sessions and external API calls
- **UV Package Management** - 10-100x faster than pip, deterministic builds
- **No Redis/Celery for MVP** - FastAPI async sufficient for pilot scale; defer infrastructure complexity

### High Level Project Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        FE[Frontend - React + TypeScript]
    end
    
    subgraph "Backend - FastAPI Monolith"
        API[API Gateway Layer]
        
        subgraph "Core Services"
            AUTH[Auth Service]
            INTERVIEW[AI Interview Engine]
            SPEECH[Speech Processing Service]
            RESUME[Resume Parser Service]
            SCORING[Assessment Scoring Service]
        end
        
        subgraph "Data Layer"
            REPO[Repository Layer]
        end
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API<br/>GPT-4 + Whisper + TTS]
        SUPABASE[(Supabase PostgreSQL)]
        ATS[External ATS/HRIS<br/>via REST APIs]
    end
    
    FE -->|HTTPS/WebSocket| API
    
    API --> AUTH
    API --> INTERVIEW
    API --> SPEECH
    API --> RESUME
    API --> SCORING
    
    INTERVIEW -->|LangChain| OPENAI
    SPEECH -->|Audio Processing| OPENAI
    RESUME -->|Skill Extraction| OPENAI
    
    AUTH --> REPO
    INTERVIEW --> REPO
    SPEECH --> REPO
    RESUME --> REPO
    SCORING --> REPO
    
    REPO --> SUPABASE
    
    API -->|Webhooks/REST| ATS
    ATS -->|Candidate Data| API
```

### Architectural and Design Patterns

**1. Service Layer Pattern**
- **Purpose:** Encapsulate business logic separate from API and data layers
- **Implementation:** Each core service (Interview, Resume, Scoring) has dedicated service class
- **Rationale:** Enables unit testing of business logic without HTTP overhead, clear separation of concerns

**2. Repository Pattern**
- **Purpose:** Abstract database access behind interfaces
- **Implementation:** `CandidateRepository`, `InterviewRepository`, `SessionRepository` classes
- **Rationale:** Database-agnostic code, easy mocking for tests, supports future database migration

**3. Dependency Injection**
- **Purpose:** Manage service dependencies and enable testability
- **Implementation:** FastAPI's built-in dependency injection system
- **Rationale:** Clean service instantiation, automatic request scoping, simplified testing

**4. Provider Abstraction Pattern**
- **Purpose:** Isolate external AI service implementations
- **Implementation:** `AIProvider` interface with `OpenAIProvider` implementation
- **Rationale:** Switch OpenAI → Azure/GCP by swapping provider without changing business logic

**5. API Gateway Pattern**
- **Purpose:** Single entry point for all client requests
- **Implementation:** FastAPI router structure with middleware pipeline
- **Rationale:** Centralized auth, rate limiting, CORS, logging

**6. Async Background Tasks (MVP)**
- **Purpose:** Non-blocking operations for resume parsing and email notifications
- **Implementation:** FastAPI BackgroundTasks for MVP
- **Future:** Redis Streams or RabbitMQ when extracting microservices or queue depth grows
- **Rationale:** Sufficient for 24-hour resume processing SLA at pilot scale; defer infrastructure complexity

---


## Tech Stack

### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Language** | Python | 3.11.9 | Primary backend language | Production-stable LTS (until Oct 2027), excellent async support, strong AI/ML ecosystem, type hints for safety |
| **Runtime** | Python | 3.11.9 | Application runtime | Native async/await, 10-60% faster than 3.10, mature ecosystem support |
| **Framework** | FastAPI | 0.104.1 | Web framework | Auto OpenAPI docs, native async, excellent performance, type-safe, minimal boilerplate |
| **Package Manager** | uv | 0.1.0+ | Dependency management | 10-100x faster than pip, deterministic lockfiles, drop-in pip replacement |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM | Industry standard, async support, type-safe queries, migration-friendly |
| **Database** | PostgreSQL | 15+ | Primary database | JSONB for flexible AI data, proven reliability, Supabase-hosted for MVP |
| **Database Client** | asyncpg | 0.29+ | PostgreSQL driver | Fastest async PostgreSQL driver for Python |
| **Database Platform** | Supabase | Cloud | Hosted PostgreSQL | Rapid prototyping, real-time capabilities, migration path to self-hosted PG |
| **Migrations** | Alembic | 1.12+ | Database migrations | SQLAlchemy integration, version control for schema changes |
| **AI Orchestration** | LangChain | 0.1.0+ | LLM framework | Conversation memory, prompt templates, token optimization, provider abstraction |
| **LLM Provider (Dev)** | OpenAI API | GPT-4o-mini | Development AI | Cost-effective development ($0.15/M tokens vs $30/M), 200x cheaper for iteration |
| **LLM Provider (Prod)** | OpenAI API | GPT-4 | Production interviews | Superior reasoning quality for candidate assessment, upgrade when revenue-proven |
| **Speech-to-Text** | OpenAI Whisper | API | Audio transcription | Excellent accuracy, same vendor as LLM (unified billing), $0.006/minute |
| **Text-to-Speech** | OpenAI TTS | API | Voice synthesis | Natural neural voices, same vendor integration, $0.015/1K characters |
| **Authentication** | JWT | via PyJWT 2.8+ | Token-based auth | Stateless, scalable, industry standard for API authentication |
| **Password Hashing** | bcrypt | via passlib 1.7+ | Secure password storage | Industry standard, resistant to rainbow tables and brute force |
| **Validation** | Pydantic | 2.5+ | Request/response validation | FastAPI native, type-safe, auto JSON schema generation |
| **HTTP Client** | httpx | 0.25+ | Async HTTP client | Modern async requests, HTTP/2 support, excellent for external APIs |
| **Background Tasks** | FastAPI BackgroundTasks | Built-in | Async task execution | Sufficient for MVP resume parsing, no external dependencies |
| **Logging** | structlog | 23.2+ | Structured logging | JSON logs, context preservation, debugging-friendly, production-ready |
| **Testing Framework** | pytest | 7.4+ | Unit & integration tests | Industry standard, excellent fixtures, async support |
| **Test Coverage** | pytest-cov | 4.1+ | Coverage reporting | Integration with pytest, detailed coverage metrics |
| **Async Testing** | pytest-asyncio | 0.21+ | Async test support | Test async FastAPI endpoints and services |
| **HTTP Testing** | httpx | 0.25+ | API testing | Test client for FastAPI, async support |
| **Mocking** | pytest-mock | 3.12+ | Test doubles | Clean mock/patch syntax, integrates with pytest |
| **Linting** | ruff | 0.1.0+ | Fast Python linter | 10-100x faster than flake8, combines multiple tools, auto-fix |
| **Formatting** | black | 23.12+ | Code formatter | Opinionated, consistent style, no config needed |
| **Type Checking** | mypy | 1.7+ | Static type analysis | Catch type errors before runtime, enforce type hints |
| **Security Scanning** | bandit | 1.7+ | Security linter | Detect common security issues in Python code |
| **Environment Config** | pydantic-settings | 2.1+ | Environment management | Type-safe config from .env files, validation built-in |
| **CORS** | fastapi-cors | Built-in | Cross-origin requests | Frontend-backend communication, secure CORS policy |
| **Rate Limiting** | slowapi | 0.1.9 | API rate limiting | Prevent abuse, cost control, per-endpoint limits |
| **API Documentation** | Swagger UI | via FastAPI | Interactive API docs | Auto-generated from Pydantic models, zero-config |
| **Error Tracking** | Python logging | Built-in | MVP error tracking | Defer Sentry to production phase, use structured logs for now |
| **Metrics** | Python logging | Built-in | MVP metrics | Defer Prometheus to production phase, log-based metrics sufficient |

### Cloud Infrastructure

- **Provider:** Supabase (PostgreSQL) + Self-managed compute (Docker containers)
- **Key Services:** 
  - Supabase PostgreSQL (database with real-time capabilities)
  - OpenAI API (GPT-4o-mini/GPT-4, Whisper STT, TTS)
  - Docker + Docker Compose (local dev and deployment)
- **Deployment Regions:** Initially single region (US-East or AU based on primary user base)
- **Future Cloud:** AWS/GCP/Azure when scaling beyond pilot phase

### Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24+ | Containerization for consistent environments |
| Docker Compose | 2.23+ | Local multi-service orchestration |
| Git | 2.40+ | Version control |
| GitHub Actions | N/A | CI/CD pipeline automation |
| Postman/Insomnia | Latest | API testing and debugging |
| DBeaver/pgAdmin | Latest | Database management and queries |
| Python REPL | Built-in | Quick testing and debugging |

### Key Technology Decisions & Rationale

**1. Python 3.11.9 (LTS Stability)**
- ✅ 2+ years production hardening, all libraries fully compatible
- ✅ Security updates until October 2027
- ✅ 10-60% performance improvement over Python 3.10
- ⚠️ Avoiding 3.12 due to edge cases in AI/ML libraries

**2. FastAPI over Flask/Django**
- ✅ Native async = better concurrency for 50+ concurrent AI sessions
- ✅ Auto OpenAPI documentation = less manual API spec work
- ✅ Pydantic integration = type-safe request/response validation
- ⚠️ Django too heavyweight for API-focused architecture

**3. OpenAI Complete Ecosystem (MVP)**
- ✅ Single vendor = simplified billing, integration, support
- ✅ GPT-4o-mini for dev = 200x cost savings ($0.15/M vs $30/M tokens)
- ✅ GPT-4 for production = superior reasoning when revenue justifies
- ✅ Whisper + TTS = unified audio processing
- 🔄 Provider abstraction enables Azure/GCP migration without code changes

**4. Supabase PostgreSQL**
- ✅ Rapid prototyping without DevOps overhead
- ✅ PostgreSQL 15+ with JSONB for flexible AI-generated data
- ✅ Real-time subscriptions for future recruiter monitoring features
- ✅ Easy migration path to self-hosted PostgreSQL
- ⚠️ Vendor lock-in mitigated by standard PostgreSQL compatibility

**5. UV Package Manager**
- ✅ 10-100x faster dependency resolution than pip
- ✅ Deterministic builds with lockfiles prevent "works on my machine"
- ✅ Drop-in pip replacement (uv pip install) - zero learning curve

**6. Deferred Infrastructure Complexity**
- ✅ **No Redis/Celery:** FastAPI BackgroundTasks sufficient for pilot scale
- ✅ **No Sentry:** Python logging + structlog adequate for MVP debugging
- ✅ **No Prometheus:** Log-based metrics sufficient until production scale
- 🔄 Add infrastructure when monitoring data proves need

**7. pytest-asyncio for Testing**
- ✅ Standard async testing framework for FastAPI
- ✅ Better ecosystem support than alternatives
- ✅ Seamless integration with pytest fixtures

**8. Ruff over Flake8/Pylint**
- ✅ 10-100x faster linting (written in Rust)
- ✅ Combines flake8, isort, pyupgrade in single tool
- ✅ Auto-fix capabilities reduce manual formatting

### Model Selection Strategy

**Development Phase:**
```python
# config/settings.py
OPENAI_MODEL = "gpt-4o-mini"  # $0.15/M input tokens
COST_PER_INTERVIEW = ~$0.02   # Estimated 100K tokens per interview
```

**Production Phase (when revenue-proven):**
```python
# config/settings.py
OPENAI_MODEL = "gpt-4"        # $30/M input tokens  
COST_PER_INTERVIEW = ~$3-5    # Higher quality, justified by revenue
```

**Upgrade Trigger:** When pilot demonstrates product-market fit and pricing model supports higher AI costs.

---


## Data Models

### Candidate

**Purpose:** Represents a job seeker going through the assessment process

**Key Attributes:**
- `id`: UUID - Unique identifier
- `email`: String - Primary contact and login credential (unique)
- `full_name`: String - Candidate's name
- `password_hash`: String - Bcrypt hashed password
- `phone`: String (optional) - Contact number
- `created_at`: DateTime - Account creation timestamp
- `updated_at`: DateTime - Last modification timestamp
- `status`: Enum - `active`, `inactive`, `deleted`

**Relationships:**
- Has many `Resume` records (candidate may upload multiple versions)
- Has many `Interview` records (one candidate can have multiple interviews)

---

### Resume

**Purpose:** Stores uploaded resumes and AI-extracted skill data

**Key Attributes:**
- `id`: UUID - Unique identifier
- `candidate_id`: UUID - Foreign key to Candidate
- `file_url`: String - Storage location (Supabase Storage or S3)
- `file_name`: String - Original filename
- `file_size`: Integer - Size in bytes
- `uploaded_at`: DateTime - Upload timestamp
- `parsed_at`: DateTime (nullable) - When AI parsing completed
- `parsing_status`: Enum - `pending`, `processing`, `completed`, `failed`
- `parsed_data`: JSONB - AI-extracted skills, experience, technologies
  ```json
  {
    "skills": ["React", "TypeScript", "Node.js"],
    "experience_years": 3,
    "education": "BS Computer Science",
    "previous_roles": ["Frontend Developer", "Full-Stack Engineer"],
    "technical_domains": {"frontend": "advanced", "backend": "intermediate"}
  }
  ```

**Relationships:**
- Belongs to one `Candidate`
- Has one `ResumeFeedback` (optional - may not have feedback generated yet)
- Has many `Interview` records (interviews customized from this resume)

---

### ResumeFeedback

**Purpose:** Manages AI-generated feedback workflow and recruiter approval

**Key Attributes:**
- `id`: UUID - Unique identifier
- `resume_id`: UUID - Foreign key to Resume (one-to-one)
- `feedback_content`: Text - AI-generated feedback email body
- `identified_gaps`: JSONB - Specific improvement areas
- `recommended_resources`: JSONB - Learning suggestions
- `status`: Enum - `draft`, `pending_approval`, `approved`, `sent`
- `generated_at`: DateTime - When AI created feedback
- `approved_at`: DateTime (nullable) - When recruiter approved
- `approved_by`: UUID (nullable) - Recruiter who approved
- `sent_at`: DateTime (nullable) - When email was sent to candidate
- `auto_send_at`: DateTime (nullable) - Scheduled auto-send time if not manually approved

**Relationships:**
- Belongs to one `Resume` (one-to-one)
- References one `Recruiter` (approved_by)

---

### Interview

**Purpose:** Represents a complete interview assessment session

**Key Attributes:**
- `id`: UUID - Unique identifier
- `candidate_id`: UUID - Foreign key to Candidate
- `resume_id`: UUID (nullable) - Resume used for customization
- `role_type`: Enum - `react`, `python`, `javascript`, `fullstack`
- `status`: Enum - `scheduled`, `in_progress`, `completed`, `abandoned`
- `started_at`: DateTime (nullable) - When interview began
- `completed_at`: DateTime (nullable) - When interview finished
- `duration_seconds`: Integer (nullable) - Total interview duration
- `ai_model_used`: String - e.g., "gpt-4o-mini" or "gpt-4"
- `total_tokens_used`: Integer - LangChain token count
- `cost_usd`: Decimal - Calculated cost for this interview
- `created_at`: DateTime - Interview scheduled/created timestamp

**Relationships:**
- Belongs to one `Candidate`
- Belongs to one `Resume` (optional - may be scheduled without resume)
- Has one `InterviewSession` (conversation state and memory)
- Has many `InterviewMessage` records (conversation history)
- Has one `AssessmentResult` (scoring and analysis)

---

### InterviewSession

**Purpose:** Manages LangChain conversation state and progressive assessment tracking

**Key Attributes:**
- `id`: UUID - Unique identifier
- `interview_id`: UUID - Foreign key to Interview (one-to-one)
- `conversation_memory`: JSONB - LangChain memory state (messages, context)
- `current_difficulty_level`: Enum - `warmup`, `standard`, `advanced`
- `questions_asked_count`: Integer - Number of questions asked so far
- `skill_boundaries_identified`: JSONB - Map of skill → proficiency level
  ```json
  {
    "react_hooks": "proficient",
    "state_management": "intermediate",
    "performance_optimization": "boundary_reached"
  }
  ```
- `progression_state`: JSONB - Internal state for progressive assessment algorithm
- `last_activity_at`: DateTime - For detecting abandoned sessions

**Relationships:**
- Belongs to one `Interview` (one-to-one)
- Has many `InterviewMessage` records

---

### InterviewMessage

**Purpose:** Stores each question-answer exchange in the interview conversation

**Key Attributes:**
- `id`: UUID - Unique identifier
- `interview_id`: UUID - Foreign key to Interview
- `session_id`: UUID - Foreign key to InterviewSession
- `sequence_number`: Integer - Order in conversation (1, 2, 3...)
- `message_type`: Enum - `ai_question`, `candidate_response`
- `content_text`: Text - The actual text (question or answer)
- `content_audio_url`: String (nullable) - Audio file URL if speech-based
- `audio_duration_seconds`: Integer (nullable) - Audio length
- `audio_metadata`: JSONB (nullable) - Audio technical details for debugging
  ```json
  {
    "sample_rate": 16000,
    "codec": "opus",
    "file_size_bytes": 45231,
    "whisper_processing_time_ms": 850,
    "confidence_score": 0.94
  }
  ```
- `response_time_seconds`: Integer (nullable) - Time from question to response start
- `metadata`: JSONB - Additional data (hesitation markers, speech patterns, etc.)
- `created_at`: DateTime - Message timestamp

**Relationships:**
- Belongs to one `Interview`
- Belongs to one `InterviewSession`

---

### AssessmentResult

**Purpose:** Stores AI-generated scoring, skill maps, and integrity analysis

**Key Attributes:**
- `id`: UUID - Unique identifier
- `interview_id`: UUID - Foreign key to Interview (one-to-one)
- `overall_score`: Decimal - Overall competency score (0-100)
- `skill_scores`: JSONB - Detailed scores per technical area
  ```json
  {
    "react_fundamentals": 85,
    "state_management": 72,
    "hooks_patterns": 88,
    "performance": 45
  }
  ```
- `skill_boundary_map`: JSONB - Visualization data for skill proficiency
- `strengths`: JSONB - Array of identified strengths with evidence
- `weaknesses`: JSONB - Array of improvement areas with evidence
- `integrity_score`: Decimal - Overall integrity rating (0-100)
- `integrity_flags`: JSONB - Specific red flags with severity and evidence
  ```json
  [
    {
      "type": "response_timing_anomaly",
      "severity": "medium",
      "evidence": "Answered complex algorithm question in 8 seconds",
      "confidence": 0.75
    }
  ]
  ```
- `ai_reasoning`: JSONB - AI's explanation for scores and decisions
- `recommended_actions`: JSONB - Suggestions for recruiter
- `generated_at`: DateTime - When assessment was completed

**Relationships:**
- Belongs to one `Interview` (one-to-one)

---

### Recruiter

**Purpose:** Represents recruitment firm staff managing candidates

**Key Attributes:**
- `id`: UUID - Unique identifier
- `email`: String - Login credential (unique)
- `full_name`: String - Recruiter's name
- `password_hash`: String - Bcrypt hashed password
- `role`: Enum - `recruiter`, `admin`, `viewer`
- `organization_id`: UUID (nullable) - Future multi-tenant support
- `created_at`: DateTime
- `last_login_at`: DateTime (nullable)
- `is_active`: Boolean - Can be deactivated without deletion

**Relationships:**
- Can approve `ResumeFeedback` records (via `approved_by`)
- Future: Has many `Interview` records through assignment

---

### IntegrationWebhook (Future - Epic 5)

**Purpose:** Manages external ATS/HRIS webhook configurations

**Key Attributes:**
- `id`: UUID
- `organization_id`: UUID
- `webhook_url`: String - External system endpoint
- `webhook_secret`: String - For signature verification
- `event_types`: JSONB - Which events to send (interview_complete, etc.)
- `is_active`: Boolean
- `last_triggered_at`: DateTime (nullable)
- `created_at`: DateTime

**Note:** Deferred to Epic 5 - ATS Integration phase

---

### Data Model Diagram

```mermaid
erDiagram
    Candidate ||--o{ Resume : uploads
    Candidate ||--o{ Interview : takes
    Resume ||--|| ResumeFeedback : generates
    Resume ||--o{ Interview : customizes
    Interview ||--|| InterviewSession : has
    Interview ||--o{ InterviewMessage : contains
    Interview ||--|| AssessmentResult : produces
    InterviewSession ||--o{ InterviewMessage : tracks
    Recruiter ||--o{ ResumeFeedback : approves
    
    Candidate {
        uuid id PK
        string email UK
        string full_name
        string password_hash
        string phone
        datetime created_at
        datetime updated_at
        enum status
    }
    
    Resume {
        uuid id PK
        uuid candidate_id FK
        string file_url
        string file_name
        int file_size
        datetime uploaded_at
        datetime parsed_at
        enum parsing_status
        jsonb parsed_data
    }
    
    ResumeFeedback {
        uuid id PK
        uuid resume_id FK
        text feedback_content
        jsonb identified_gaps
        jsonb recommended_resources
        enum status
        datetime generated_at
        datetime approved_at
        uuid approved_by FK
        datetime sent_at
        datetime auto_send_at
    }
    
    Interview {
        uuid id PK
        uuid candidate_id FK
        uuid resume_id FK
        enum role_type
        enum status
        datetime started_at
        datetime completed_at
        int duration_seconds
        string ai_model_used
        int total_tokens_used
        decimal cost_usd
        datetime created_at
    }
    
    InterviewSession {
        uuid id PK
        uuid interview_id FK
        jsonb conversation_memory
        enum current_difficulty_level
        int questions_asked_count
        jsonb skill_boundaries_identified
        jsonb progression_state
        datetime last_activity_at
    }
    
    InterviewMessage {
        uuid id PK
        uuid interview_id FK
        uuid session_id FK
        int sequence_number
        enum message_type
        text content_text
        string content_audio_url
        int audio_duration_seconds
        jsonb audio_metadata
        int response_time_seconds
        jsonb metadata
        datetime created_at
    }
    
    AssessmentResult {
        uuid id PK
        uuid interview_id FK
        decimal overall_score
        jsonb skill_scores
        jsonb skill_boundary_map
        jsonb strengths
        jsonb weaknesses
        decimal integrity_score
        jsonb integrity_flags
        jsonb ai_reasoning
        jsonb recommended_actions
        datetime generated_at
    }
    
    Recruiter {
        uuid id PK
        string email UK
        string full_name
        string password_hash
        enum role
        uuid organization_id FK
        datetime created_at
        datetime last_login_at
        boolean is_active
    }
```

---

### Key Design Decisions

**1. Separate ResumeFeedback Table**
- ✅ Clean separation of concerns: Resume = storage, Feedback = workflow
- ✅ Enables feedback iteration history (recruiter edits, multiple versions)
- ✅ Clear approval workflow tracking
- ✅ Easier to query "pending approvals" for recruiter dashboard

**2. Audio Metadata in InterviewMessage**
- ✅ Debug speech processing issues (codec problems, quality degradation)
- ✅ Track Whisper API performance (processing time trends)
- ✅ Confidence scores help identify unreliable transcriptions
- ✅ Sample rate validation ensures quality standards

**3. JSONB for AI-Generated Data**
- ✅ Flexible schema for evolving AI outputs (scores, reasoning, flags)
- ✅ PostgreSQL's JSONB supports indexing and queries: `WHERE parsed_data->>'skills' @> '["React"]'`
- ✅ No schema migrations needed when AI output format changes
- ⚠️ Trade-off: Less type safety, but necessary for AI flexibility

**4. Separate InterviewSession from Interview**
- ✅ Clean separation: Interview = metadata, Session = conversation state
- ✅ LangChain memory isolated for independent management
- ✅ Enables session resumption and state snapshots
- ✅ Progressive assessment state doesn't clutter main Interview table

**5. One-to-One AssessmentResult**
- ✅ Separates "interview conduct" from "scoring/analysis"
- ✅ Allows regenerating scores without affecting interview record
- ✅ Clean boundary for future async scoring service extraction

**6. UUID Primary Keys**
- ✅ Distributed-friendly (no ID collisions when scaling)
- ✅ Non-sequential = harder to enumerate candidates (security)
- ✅ Works seamlessly with Supabase and future microservices

**7. Deferred Audit Logging**
- ✅ Focus on core functionality for MVP
- 🔄 Add comprehensive audit trails in production phase when GDPR compliance critical

---


## Components

### Auth Service

**Responsibility:** Handle candidate and recruiter authentication, authorization, and session management

**Key Interfaces:**
- `register_candidate(email, password, full_name) → Candidate`
- `login_candidate(email, password) → JWT token`
- `register_recruiter(email, password, full_name, role) → Recruiter`
- `login_recruiter(email, password) → JWT token`
- `verify_token(token) → User ID + Role`
- `refresh_token(token) → New JWT token`

**Dependencies:**
- `CandidateRepository` - Database access for candidates
- `RecruiterRepository` - Database access for recruiters
- `passlib` - Password hashing (bcrypt)
- `PyJWT` - Token generation and validation

**Technology Stack:**
- FastAPI dependency injection for auth middleware
- JWT with 24-hour expiration (configurable)
- Bcrypt with cost factor 12 for password hashing
- Rate limiting via SlowAPI (5 failed attempts = 15 min lockout)

**Security Considerations:**
- Passwords never stored in plaintext
- Tokens signed with secret key from environment
- HTTPS-only token transmission (enforced in production)

---

### AI Interview Engine

**Responsibility:** Orchestrate conversational AI interviews with progressive difficulty adjustment and real-time skill boundary detection

**Key Interfaces:**
- `start_interview(candidate_id, resume_id, role_type) → Interview`
- `process_candidate_response(interview_id, response_text) → AI question`
- `get_next_question(session_id) → Question + metadata`
- `detect_skill_boundary(session_id, skill_area) → Proficiency level`
- `complete_interview(interview_id) → Assessment trigger`

**Dependencies:**
- `InterviewRepository` - Interview persistence
- `InterviewSessionRepository` - Conversation state management
- `InterviewMessageRepository` - Message history
- `OpenAIProvider` (via abstraction) - LLM access
- `LangChain` - Conversation memory and prompt management

**Technology Stack:**
- LangChain `ConversationBufferMemory` for context retention
- Custom `ProgressiveAssessmentEngine` class for difficulty logic
- Prompt templates versioned in `backend/prompts/` directory
- Token counting for cost tracking
- Async processing for concurrent sessions

**Progressive Assessment Algorithm:**
1. **Warmup Phase (2-3 questions):** Confidence-building, basic concepts
2. **Standard Phase (5-8 questions):** Core competency evaluation
3. **Advanced Phase (3-5 questions):** Boundary exploration until struggles detected
4. **Adaptive Branching:** AI adjusts based on response quality

**Internal Structure:**
```python
class AIInterviewEngine:
    def __init__(self, ai_provider: AIProvider, session_repo: SessionRepository):
        self.ai_provider = ai_provider
        self.session_repo = session_repo
        self.prompt_manager = PromptTemplateManager()
    
    async def process_response(self, interview_id: UUID, response: str) -> Question:
        # Load session state
        # Analyze response quality
        # Update skill boundaries
        # Determine next difficulty level
        # Generate contextual question
        # Save state
```

---

### Speech Processing Service

**Responsibility:** Handle audio transcription (STT) and voice synthesis (TTS) with provider abstraction

**Key Interfaces:**
- `transcribe_audio(audio_file, metadata) → Transcription + confidence`
- `synthesize_speech(text, voice_config) → Audio URL`
- `validate_audio_quality(audio_metadata) → Quality score`
- `process_audio_stream(stream_chunks) → Real-time text`

**Dependencies:**
- `OpenAIProvider` - Whisper API for STT, TTS API for voice
- `InterviewMessageRepository` - Store audio metadata
- Supabase Storage or S3 - Audio file storage
- `httpx` - Async HTTP client for OpenAI API

**Technology Stack:**
- OpenAI Whisper API (primary for MVP)
- OpenAI TTS API with `alloy` voice (neural)
- Audio format support: WebM, Opus, MP3, WAV
- Target sample rate: 16kHz minimum
- Backend audio processing (never expose API keys to frontend)

**Provider Abstraction:**
```python
class SpeechProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        pass
    
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        pass

class OpenAISpeechProvider(SpeechProvider):
    # OpenAI Whisper + TTS implementation

# Future: AzureSpeechProvider, GCPSpeechProvider
```

**Audio Metadata Capture:**
- Sample rate, codec, file size
- Whisper processing time
- Confidence scores per segment
- Background noise levels (future)

---

### Resume Parser Service

**Responsibility:** Parse uploaded resumes, extract skills/experience, generate feedback

**Key Interfaces:**
- `upload_resume(candidate_id, file) → Resume`
- `parse_resume_async(resume_id) → Background task`
- `extract_skills(resume_text) → Parsed data`
- `generate_feedback(parsed_data) → ResumeFeedback`
- `approve_feedback(feedback_id, recruiter_id) → Send email`

**Dependencies:**
- `ResumeRepository` - Resume persistence
- `ResumeFeedbackRepository` - Feedback workflow
- `OpenAIProvider` - GPT-4o-mini for parsing/feedback
- Supabase Storage - File storage
- `FastAPI BackgroundTasks` - Async processing
- Email service (SendGrid/AWS SES - future)

**Technology Stack:**
- PDF parsing: `PyPDF2` or `pdfplumber`
- DOCX parsing: `python-docx`
- AI extraction: GPT-4o-mini with structured output
- Background processing: FastAPI BackgroundTasks (MVP)
- Processing SLA: 24 hours per NFR15

**Parsing Pipeline:**
1. **Upload:** Store file in Supabase Storage
2. **Extract Text:** PDF/DOCX → plain text
3. **AI Analysis:** GPT-4o-mini extracts structured data
4. **Feedback Generation:** AI creates improvement suggestions
5. **Recruiter Approval:** Optional manual review before sending
6. **Auto-send:** After 4 hours if not manually reviewed

---

### Assessment Scoring Service

**Responsibility:** Generate comprehensive scoring, skill maps, and integrity analysis post-interview

**Key Interfaces:**
- `generate_assessment(interview_id) → AssessmentResult`
- `calculate_skill_scores(messages, session_state) → Skill map`
- `analyze_integrity(messages, timing_data) → Integrity flags`
- `generate_ai_reasoning(scores, evidence) → Explanations`
- `recommend_actions(assessment) → Recruiter suggestions`

**Dependencies:**
- `InterviewRepository` - Interview data
- `InterviewMessageRepository` - Conversation history
- `AssessmentResultRepository` - Results storage
- `OpenAIProvider` - GPT-4o-mini for analysis
- `LangChain` - Structured output parsing

**Technology Stack:**
- Post-interview async processing
- Multi-pass analysis: technical → integrity → recommendations
- Structured output via Pydantic models
- Caching intermediate results in session state

**Scoring Components:**

**1. Technical Scoring:**
- Parse conversation for technical concepts demonstrated
- Map responses to skill proficiency levels
- Generate evidence-backed skill scores (0-100)

**2. Integrity Analysis:**
- Response timing anomalies (too fast = suspicious)
- Pattern matching against known solutions (future: vector similarity)
- Hesitation detection from audio metadata
- Consistency checking across responses

**3. AI Reasoning Generation:**
- For each score, AI explains its rationale
- Cites specific questions/answers as evidence
- Provides confidence levels

---

### API Gateway Layer

**Responsibility:** Single entry point for all HTTP requests with middleware pipeline

**Key Components:**
- FastAPI routers for endpoint organization
- Authentication middleware (JWT validation)
- Rate limiting middleware (SlowAPI)
- CORS configuration
- Request/response logging
- Error handling and standardization

**Router Structure:**
```
/api/v1/
├── /auth/          → Auth Service
├── /candidates/    → Candidate operations
├── /resumes/       → Resume upload/feedback
├── /interviews/    → Interview management
├── /messages/      → Interview messaging
├── /assessments/   → Results retrieval
├── /recruiters/    → Recruiter portal
└── /webhooks/      → External integrations (Epic 5)
```

**Middleware Pipeline:**
1. **CORS** - Frontend origin whitelisting
2. **Rate Limiting** - Per-endpoint limits
3. **Authentication** - JWT validation (protected routes)
4. **Request Logging** - Structured logs with correlation IDs
5. **Error Handling** - Standardized error responses
6. **Response Compression** - Gzip for large payloads

---

### Repository Layer

**Responsibility:** Abstract database access with clean interfaces for all entities

**Repositories:**
- `CandidateRepository`
- `RecruiterRepository`
- `ResumeRepository`
- `ResumeFeedbackRepository`
- `InterviewRepository`
- `InterviewSessionRepository`
- `InterviewMessageRepository`
- `AssessmentResultRepository`

**Standard Interface Pattern:**
```python
class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
```

**Technology Stack:**
- SQLAlchemy 2.0 async ORM
- asyncpg driver for PostgreSQL
- Transaction management via context managers
- Connection pooling (10 connections for MVP)

---

### Component Interaction Diagram

```mermaid
sequenceDiagram
    participant Frontend
    participant API Gateway
    participant Auth
    participant Interview Engine
    participant Speech Service
    participant AI Provider (OpenAI)
    participant Repository
    participant Database

    Frontend->>API Gateway: POST /interviews/{id}/messages (audio)
    API Gateway->>Auth: Verify JWT
    Auth-->>API Gateway: User authenticated
    
    API Gateway->>Speech Service: Transcribe audio
    Speech Service->>AI Provider: Whisper API call
    AI Provider-->>Speech Service: Transcription + confidence
    
    API Gateway->>Interview Engine: Process response(text)
    Interview Engine->>Repository: Load session state
    Repository->>Database: SELECT interview_session
    Database-->>Repository: Session data
    
    Interview Engine->>AI Provider: Generate next question (GPT-4o-mini)
    AI Provider-->>Interview Engine: AI question
    
    Interview Engine->>Repository: Save message + update state
    Repository->>Database: INSERT/UPDATE
    
    Interview Engine->>Speech Service: Synthesize TTS
    Speech Service->>AI Provider: TTS API call
    AI Provider-->>Speech Service: Audio file
    
    API Gateway-->>Frontend: Response (audio URL + text)
```

---


## External APIs & Services

### OpenAI API Integration

**1. Whisper API (Speech-to-Text)**

**Endpoint:** `https://api.openai.com/v1/audio/transcriptions`

**Authentication:** Bearer token in Authorization header

**Request Format:**
```python
{
    "file": <audio_file>,         # multipart/form-data
    "model": "whisper-1",
    "language": "en",             # Optional, improves accuracy
    "response_format": "json",    # json, text, srt, verbose_json, vtt
    "temperature": 0              # 0 = deterministic, 0-1 = creative
}
```

**Response Format:**
```json
{
    "text": "Transcribed text from audio"
}
```

**Rate Limits:**
- 50 requests per minute (RPM) for free tier
- File size limit: 25 MB
- Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm

**Error Handling:**
- 429 (Rate Limit): Exponential backoff with 1s, 2s, 4s retries
- 400 (Bad Request): Log audio metadata, alert for codec issues
- 500 (Server Error): Retry up to 3 times with 2s delay

**Cost:** $0.006 per minute of audio

---

**2. TTS API (Text-to-Speech)**

**Endpoint:** `https://api.openai.com/v1/audio/speech`

**Authentication:** Bearer token in Authorization header

**Request Format:**
```python
{
    "model": "tts-1",           # tts-1 (faster) or tts-1-hd (higher quality)
    "input": "Text to speak",   # Max 4096 characters
    "voice": "alloy",           # alloy, echo, fable, onyx, nova, shimmer
    "response_format": "mp3",   # mp3, opus, aac, flac
    "speed": 1.0                # 0.25 to 4.0
}
```

**Response:** Binary audio file stream

**Voice Selection for MVP:** `alloy` (neutral, professional)

**Rate Limits:**
- 50 requests per minute (RPM)
- Max input length: 4096 characters per request

**Error Handling:**
- 429 (Rate Limit): Queue requests, process sequentially
- 400 (Bad Request): Truncate text if >4096 chars
- 500 (Server Error): Return cached TTS if available, else retry

**Cost:** $0.015 per 1,000 characters (input text)

---

**3. GPT-4 / GPT-4o-mini API (Completions)**

**Endpoint:** `https://api.openai.com/v1/chat/completions`

**Authentication:** Bearer token in Authorization header

**Request Format:**
```python
{
    "model": "gpt-4o-mini",           # or "gpt-4" for production
    "messages": [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Previous response"}
    ],
    "temperature": 0.7,               # 0 = deterministic, 2 = creative
    "max_tokens": 1000,               # Response length limit
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

**Response Format:**
```json
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4o-mini",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "AI response text"
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 56,
        "completion_tokens": 31,
        "total_tokens": 87
    }
}
```

**Model Specifications:**

| Model | Context Window | Input Cost | Output Cost | Use Case |
|-------|---------------|------------|-------------|----------|
| GPT-4o-mini | 128K tokens | $0.150/1M | $0.600/1M | Development, MVP interviews |
| GPT-4 | 8K tokens | $30/1M | $60/1M | Production interviews (when revenue-proven) |

**Rate Limits:**
- Free tier: 3 RPM, 40K TPM (tokens per minute)
- Paid tier 1: 500 RPM, 30K TPD (tokens per day)
- Paid tier 2: 5000 RPM, 300K TPD

**Error Handling:**
- 429 (Rate Limit): Exponential backoff, queue interview requests
- 400 (Invalid Request): Log prompt, validate token count
- 401 (Auth Error): Rotate API keys if compromised
- 500 (Server Error): Retry up to 3 times with 5s delay
- Context Length Error: Truncate conversation history, keep system prompt + last 5 messages

**Token Management:**
- Track usage per interview in `Interview.total_tokens_used`
- Alert at 80% of daily token limit
- Implement token budgeting: max 10K tokens per interview

**Cost Optimization:**
- Use GPT-4o-mini for all non-critical tasks (resume parsing, feedback generation)
- Upgrade to GPT-4 only for production interviews after revenue validation
- Cache system prompts to reduce input tokens

---

### Supabase API Integration

**Database Access:** PostgreSQL via asyncpg driver (not REST API)

**Storage API (File Uploads):**

**Endpoint:** `https://{project_id}.supabase.co/storage/v1/object/{bucket_name}/{file_path}`

**Authentication:** Service role key or user JWT

**Bucket Configuration:**
- `resumes` bucket - Private, max 10MB per file, PDF/DOCX only
- `audio` bucket - Private, max 5MB per file, WebM/Opus/MP3 only

**Upload Example:**
```python
import httpx

async def upload_resume(file_data: bytes, candidate_id: str, filename: str):
    url = f"{SUPABASE_URL}/storage/v1/object/resumes/{candidate_id}/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/pdf"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, content=file_data, headers=headers)
        return response.json()
```

**Signed URLs for Frontend Access:**
```python
# Generate temporary download URL (expires in 1 hour)
url = f"{SUPABASE_URL}/storage/v1/object/sign/resumes/{file_path}?expiresIn=3600"
```

---

### Circuit Breaker & Retry Configuration

**Circuit Breaker Pattern (for OpenAI APIs):**

```python
class CircuitBreaker:
    failure_threshold = 5       # Open circuit after 5 consecutive failures
    timeout = 60                # Keep circuit open for 60 seconds
    half_open_max_calls = 3     # Allow 3 test calls when half-open
    
    states = ["CLOSED", "OPEN", "HALF_OPEN"]
```

**Retry Logic:**
- **Transient Errors (429, 500, 503):** Exponential backoff with jitter
  - Attempt 1: 1 second
  - Attempt 2: 2 seconds + random(0-0.5s)
  - Attempt 3: 4 seconds + random(0-1s)
  - Max attempts: 3

- **Non-Retryable Errors (400, 401, 403):** Immediate failure, log and alert

**Timeout Configuration:**
- Whisper API: 30 seconds (audio processing)
- TTS API: 20 seconds (voice synthesis)
- GPT-4 API: 45 seconds (conversation generation)
- Database queries: 10 seconds (prevent hanging)

---

### Future External Integrations (Epic 5)

**ATS/HRIS Systems:**
- Greenhouse API (REST)
- Lever API (REST)
- BambooHR API (REST)
- Workable API (REST)

**Email Services:**
- SendGrid API (transactional emails)
- AWS SES (cost-effective alternative)

**Analytics:**
- Segment (event tracking)
- Mixpanel (user behavior analysis)

---


## Core Workflows

### Workflow 1: Candidate Completes AI Interview (Speech-Based)

**Trigger:** Candidate clicks "Start Interview" button

**Actors:** Candidate, Frontend, Backend, OpenAI API, Database

```mermaid
sequenceDiagram
    participant C as Candidate
    participant FE as Frontend
    participant API as API Gateway
    participant Auth as Auth Service
    participant IE as Interview Engine
    participant Speech as Speech Service
    participant OpenAI as OpenAI API
    participant DB as Database

    C->>FE: Click "Start Interview"
    FE->>API: POST /api/v1/interviews {candidate_id, resume_id, role_type}
    API->>Auth: Verify JWT
    Auth-->>API: Authorized
    
    API->>IE: start_interview()
    IE->>DB: CREATE Interview record (status='in_progress')
    IE->>DB: CREATE InterviewSession record
    IE->>OpenAI: Generate first question (GPT-4o-mini)
    OpenAI-->>IE: "Tell me about your React experience..."
    
    IE->>Speech: synthesize_speech(question_text)
    Speech->>OpenAI: TTS API call
    OpenAI-->>Speech: Audio file (MP3)
    Speech->>DB: Store audio URL
    
    IE->>DB: INSERT InterviewMessage (type='ai_question')
    IE-->>API: {audio_url, text, session_id}
    API-->>FE: Interview started successfully
    FE->>C: Play audio question
    
    Note over C,FE: Candidate speaks answer
    
    C->>FE: Audio recorded (WebM/Opus)
    FE->>API: POST /api/v1/interviews/{id}/messages {audio_data}
    API->>Auth: Verify JWT
    Auth-->>API: Authorized
    
    API->>Speech: transcribe_audio(audio_data)
    Speech->>OpenAI: Whisper API call
    OpenAI-->>Speech: Transcription + confidence
    Speech->>DB: Store audio URL + metadata
    
    API->>IE: process_candidate_response(interview_id, text)
    IE->>DB: INSERT InterviewMessage (type='candidate_response')
    IE->>DB: UPDATE InterviewSession (skill_boundaries, progression_state)
    
    IE->>OpenAI: Generate next question based on response
    OpenAI-->>IE: Next contextual question
    
    IE->>Speech: synthesize_speech(next_question)
    Speech->>OpenAI: TTS API call
    OpenAI-->>Speech: Audio file
    
    IE->>DB: INSERT InterviewMessage (type='ai_question')
    IE-->>API: {audio_url, text, next_question}
    API-->>FE: Next question ready
    FE->>C: Play next audio question
    
    Note over C,FE: Loop continues for 12-20 questions
    
    C->>FE: Click "Submit Interview"
    FE->>API: POST /api/v1/interviews/{id}/complete
    API->>IE: complete_interview(interview_id)
    IE->>DB: UPDATE Interview (status='completed', completed_at=NOW)
    
    IE->>IE: Trigger async assessment scoring
    Note over IE: BackgroundTask starts
    
    IE-->>API: Interview completed
    API-->>FE: Success, redirecting to results page
    FE->>C: Show "Processing assessment..." screen
    
    Note over IE,DB: Background assessment generation
    IE->>DB: Load all InterviewMessages
    IE->>OpenAI: Analyze conversation for scoring
    OpenAI-->>IE: Skill scores + reasoning
    IE->>OpenAI: Analyze integrity flags
    OpenAI-->>IE: Integrity analysis
    IE->>DB: INSERT AssessmentResult
    
    Note over C: Candidate can view results when ready
```

**Key Steps:**
1. Interview creation with resume context
2. First AI question generation and TTS synthesis
3. Repeated question-answer loop (12-20 exchanges)
4. Real-time transcription via Whisper
5. Progressive difficulty adjustment based on responses
6. Interview completion trigger
7. Async assessment scoring generation

**Error Handling:**
- **OpenAI Rate Limit:** Queue request, show "Generating question..." spinner
- **Whisper Transcription Failure:** Allow candidate to re-record answer
- **TTS Failure:** Display text question as fallback
- **Network Interruption:** Session state persisted, resume from last question

---

### Workflow 2: Resume Upload to Feedback Generation

**Trigger:** Candidate uploads resume file

**Actors:** Candidate, Frontend, Backend, OpenAI API, Recruiter

```mermaid
sequenceDiagram
    participant C as Candidate
    participant FE as Frontend
    participant API as API Gateway
    participant Resume as Resume Parser Service
    participant Storage as Supabase Storage
    participant OpenAI as OpenAI API
    participant DB as Database
    participant Email as Email Service
    participant R as Recruiter

    C->>FE: Upload resume file (PDF/DOCX)
    FE->>API: POST /api/v1/resumes {file, candidate_id}
    API->>Resume: upload_resume(file, candidate_id)
    
    Resume->>Storage: Upload file to 'resumes' bucket
    Storage-->>Resume: {file_url}
    
    Resume->>DB: INSERT Resume (status='pending', file_url)
    Resume-->>API: {resume_id, status='pending'}
    API-->>FE: Upload successful
    FE->>C: Show "Processing resume..." message
    
    Note over Resume: Background task triggered
    
    Resume->>Resume: parse_resume_async(resume_id)
    Resume->>DB: UPDATE Resume (status='processing')
    
    Resume->>Storage: Download file from Supabase
    Storage-->>Resume: File bytes
    
    Resume->>Resume: Extract text (PyPDF2/python-docx)
    Resume->>OpenAI: Parse resume for skills (GPT-4o-mini)
    OpenAI-->>Resume: Structured data (skills, experience, etc.)
    
    Resume->>DB: UPDATE Resume (parsed_data, status='completed', parsed_at=NOW)
    
    Resume->>OpenAI: Generate feedback email (GPT-4o-mini)
    OpenAI-->>Resume: Feedback content + improvement suggestions
    
    Resume->>DB: INSERT ResumeFeedback (status='pending_approval', auto_send_at=+4 hours)
    
    Note over R: Recruiter dashboard shows pending feedback
    
    alt Recruiter approves within 4 hours
        R->>FE: Review feedback, click "Approve & Send"
        FE->>API: POST /api/v1/resumes/{id}/feedback/approve {recruiter_id}
        API->>Resume: approve_feedback(feedback_id, recruiter_id)
        Resume->>DB: UPDATE ResumeFeedback (status='approved', approved_at=NOW, approved_by)
        Resume->>Email: send_email(candidate_email, feedback_content)
        Email-->>Resume: Email sent
        Resume->>DB: UPDATE ResumeFeedback (status='sent', sent_at=NOW)
        Resume-->>API: Feedback sent
        API-->>FE: Success
        FE->>R: Show confirmation
    else Auto-send after 4 hours (no manual action)
        Note over Resume: Scheduled task runs every 5 minutes
        Resume->>DB: SELECT ResumeFeedback WHERE status='pending_approval' AND auto_send_at <= NOW
        Resume->>Email: send_email(candidate_email, feedback_content)
        Email-->>Resume: Email sent
        Resume->>DB: UPDATE ResumeFeedback (status='sent', sent_at=NOW)
    end
    
    Note over C: Candidate receives feedback email
```

**Key Steps:**
1. File upload to Supabase Storage
2. Resume record created with `pending` status
3. Background task extracts text from PDF/DOCX
4. GPT-4o-mini parses skills and experience
5. GPT-4o-mini generates feedback email
6. Recruiter approval workflow (4-hour window)
7. Auto-send if not manually reviewed

**SLA:** 24 hours from upload to feedback delivery (NFR15)

**Error Handling:**
- **File Format Invalid:** Return 400 with "Only PDF/DOCX supported"
- **AI Parsing Failure:** Retry 3 times, then mark as `failed` and alert recruiter
- **Email Delivery Failure:** Retry with exponential backoff, log failure after 5 attempts

---

### Workflow 3: Interview Scoring and Assessment Generation

**Trigger:** Interview marked as `completed`

**Actors:** Background Task, Interview Engine, OpenAI API, Database

```mermaid
sequenceDiagram
    participant BG as Background Task
    participant IE as Interview Engine
    participant Scoring as Assessment Scoring Service
    participant DB as Database
    participant OpenAI as OpenAI API

    Note over BG: Triggered when interview status='completed'
    
    BG->>Scoring: generate_assessment(interview_id)
    Scoring->>DB: Load Interview record
    Scoring->>DB: Load all InterviewMessages (questions + answers)
    Scoring->>DB: Load InterviewSession (skill_boundaries, progression_state)
    
    Note over Scoring: Multi-pass analysis begins
    
    Scoring->>Scoring: PASS 1 - Technical Scoring
    Scoring->>OpenAI: Analyze responses for technical competency (GPT-4o-mini)
    OpenAI-->>Scoring: {react_fundamentals: 85, hooks: 72, performance: 45}
    
    Scoring->>Scoring: PASS 2 - Integrity Analysis
    Scoring->>OpenAI: Detect timing anomalies, inconsistencies (GPT-4o-mini)
    OpenAI-->>Scoring: [{type: "fast_response", severity: "medium", evidence: "..."}]
    
    Scoring->>Scoring: PASS 3 - AI Reasoning Generation
    Scoring->>OpenAI: Generate explanations for scores (GPT-4o-mini)
    OpenAI-->>Scoring: "Strong understanding of hooks but lacks optimization experience..."
    
    Scoring->>Scoring: PASS 4 - Recommendations
    Scoring->>OpenAI: Generate recruiter action items (GPT-4o-mini)
    OpenAI-->>Scoring: ["Schedule technical deep-dive", "Test optimization knowledge in coding task"]
    
    Scoring->>Scoring: Aggregate results
    Scoring->>DB: INSERT AssessmentResult (all scoring data)
    
    Scoring->>DB: UPDATE Interview (status='completed', cost_usd calculated)
    
    Scoring-->>BG: Assessment complete
    
    Note over DB: Recruiter can now view results in portal
```

**Key Steps:**
1. Load interview conversation history
2. **Pass 1:** Technical skill scoring with evidence
3. **Pass 2:** Integrity flag detection
4. **Pass 3:** AI reasoning generation
5. **Pass 4:** Recruiter recommendations
6. Store comprehensive `AssessmentResult`

**Processing Time:** Target <30 seconds for standard interview (NFR6)

**Error Handling:**
- **OpenAI Timeout:** Retry with truncated conversation history
- **Scoring Failure:** Mark assessment as `failed`, alert admin, allow manual retry
- **Partial Success:** Store partial results, flag incomplete sections

---

### Workflow 4: Session Recovery (Interrupted Interview)

**Trigger:** Candidate network drops mid-interview

**Actors:** Candidate, Frontend, Backend

```mermaid
sequenceDiagram
    participant C as Candidate
    participant FE as Frontend
    participant API as API Gateway
    participant IE as Interview Engine
    participant DB as Database

    Note over C,FE: Network interruption during question 7
    
    C->>FE: Browser reconnects
    FE->>FE: Check localStorage for active_interview_id
    FE->>API: GET /api/v1/interviews/{id}/status
    API->>DB: Load Interview record
    
    alt Interview status = 'in_progress'
        API->>DB: Load InterviewSession
        API->>DB: Load last 5 InterviewMessages
        API-->>FE: {status: 'in_progress', last_message, session_state}
        FE->>C: Show "Resume Interview" button
        
        C->>FE: Click "Resume Interview"
        FE->>API: GET /api/v1/interviews/{id}/messages/latest
        API->>DB: Get latest AI question
        API-->>FE: {audio_url, text}
        FE->>C: Replay last question
        
        Note over C: Interview continues from last question
    else Interview status = 'completed'
        API-->>FE: {status: 'completed', redirect_to: '/results/{id}'}
        FE->>C: Redirect to results page
    else Interview status = 'abandoned' (>30 min inactive)
        API-->>FE: {status: 'abandoned', can_restart: true}
        FE->>C: Show "Interview expired, start new interview"
    end
```

**Key Features:**
- Session state persisted after every message
- Frontend stores `active_interview_id` in localStorage
- Backend tracks `last_activity_at` for abandonment detection
- 30-minute inactivity threshold for auto-abandonment

---

### Workflow 5: Candidate Registration & First Login

**Trigger:** Candidate clicks "Sign Up" from landing page

```mermaid
sequenceDiagram
    participant C as Candidate
    participant FE as Frontend
    participant API as API Gateway
    participant Auth as Auth Service
    participant DB as Database

    C->>FE: Enter email, password, full name
    FE->>API: POST /api/v1/auth/register {email, password, full_name}
    API->>Auth: register_candidate()
    
    Auth->>DB: Check if email exists
    
    alt Email already exists
        DB-->>Auth: Email found
        Auth-->>API: Error 409 Conflict
        API-->>FE: "Email already registered"
        FE->>C: Show error, suggest login
    else Email available
        DB-->>Auth: Email available
        Auth->>Auth: Hash password (bcrypt, cost=12)
        Auth->>DB: INSERT Candidate (email, password_hash, full_name, status='active')
        DB-->>Auth: Candidate created
        
        Auth->>Auth: Generate JWT token (expires in 24h)
        Auth-->>API: {token, candidate_id, email}
        API-->>FE: Registration successful + JWT
        
        FE->>FE: Store JWT in localStorage
        FE->>C: Redirect to dashboard
        
        C->>FE: See "Upload Resume" and "Start Interview" options
    end
```

**Validation Rules:**
- Email: Valid email format, unique
- Password: Min 8 characters, 1 uppercase, 1 number, 1 special char
- Full name: Min 2 characters

**Security:**
- Passwords hashed with bcrypt (cost factor 12)
- JWT signed with secret key (256-bit)
- HTTPS-only token transmission

---


## Database Schema

### PostgreSQL DDL (Data Definition Language)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Candidates table
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deleted'))
);

CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_status ON candidates(status);

-- Resumes table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP WITH TIME ZONE,
    parsing_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (parsing_status IN ('pending', 'processing', 'completed', 'failed')),
    parsed_data JSONB
);

CREATE INDEX idx_resumes_candidate_id ON resumes(candidate_id);
CREATE INDEX idx_resumes_parsing_status ON resumes(parsing_status);
CREATE INDEX idx_resumes_parsed_data ON resumes USING GIN (parsed_data);  -- For JSONB queries

-- ResumeFeedback table
CREATE TABLE resume_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID UNIQUE NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    feedback_content TEXT NOT NULL,
    identified_gaps JSONB,
    recommended_resources JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'sent')),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES recruiters(id),
    sent_at TIMESTAMP WITH TIME ZONE,
    auto_send_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_resume_feedback_resume_id ON resume_feedback(resume_id);
CREATE INDEX idx_resume_feedback_status ON resume_feedback(status);
CREATE INDEX idx_resume_feedback_auto_send ON resume_feedback(auto_send_at) WHERE status = 'pending_approval';

-- Interviews table
CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id),
    role_type VARCHAR(50) NOT NULL CHECK (role_type IN ('react', 'python', 'javascript', 'fullstack')),
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'abandoned')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    ai_model_used VARCHAR(50),
    total_tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 4) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_created_at ON interviews(created_at);

-- InterviewSessions table
CREATE TABLE interview_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id UUID UNIQUE NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    conversation_memory JSONB,
    current_difficulty_level VARCHAR(20) DEFAULT 'warmup' CHECK (current_difficulty_level IN ('warmup', 'standard', 'advanced')),
    questions_asked_count INTEGER DEFAULT 0,
    skill_boundaries_identified JSONB,
    progression_state JSONB,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interview_sessions_interview_id ON interview_sessions(interview_id);
CREATE INDEX idx_interview_sessions_last_activity ON interview_sessions(last_activity_at);

-- InterviewMessages table
CREATE TABLE interview_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('ai_question', 'candidate_response')),
    content_text TEXT NOT NULL,
    content_audio_url TEXT,
    audio_duration_seconds INTEGER,
    audio_metadata JSONB,
    response_time_seconds INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interview_messages_interview_id ON interview_messages(interview_id);
CREATE INDEX idx_interview_messages_session_id ON interview_messages(session_id);
CREATE INDEX idx_interview_messages_sequence ON interview_messages(interview_id, sequence_number);

-- AssessmentResults table
CREATE TABLE assessment_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id UUID UNIQUE NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    overall_score DECIMAL(5, 2) NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    skill_scores JSONB NOT NULL,
    skill_boundary_map JSONB,
    strengths JSONB,
    weaknesses JSONB,
    integrity_score DECIMAL(5, 2) CHECK (integrity_score >= 0 AND integrity_score <= 100),
    integrity_flags JSONB,
    ai_reasoning JSONB,
    recommended_actions JSONB,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessment_results_interview_id ON assessment_results(interview_id);
CREATE INDEX idx_assessment_results_overall_score ON assessment_results(overall_score);

-- Recruiters table
CREATE TABLE recruiters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'recruiter' CHECK (role IN ('recruiter', 'admin', 'viewer')),
    organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_recruiters_email ON recruiters(email);
CREATE INDEX idx_recruiters_organization_id ON recruiters(organization_id);

-- IntegrationWebhooks table (Epic 5 - Future)
CREATE TABLE integration_webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID,
    webhook_url TEXT NOT NULL,
    webhook_secret VARCHAR(255) NOT NULL,
    event_types JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_integration_webhooks_organization_id ON integration_webhooks(organization_id);

-- Trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_candidates_updated_at
BEFORE UPDATE ON candidates
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

### Alembic Migration Strategy

**Initial Migration (v1):**
```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema with all tables"

# Apply migration
alembic upgrade head
```

**Future Migrations (Example):**
```bash
# Add new column
alembic revision -m "Add interview_type to interviews"
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Migration File Structure:**
```
backend/
└── alembic/
    ├── versions/
    │   ├── 001_initial_schema.py
    │   ├── 002_add_interview_types.py
    │   └── ...
    ├── env.py
    └── script.py.mako
```

---

### Database Seeding (Development)

```python
# backend/scripts/seed_dev_data.py

async def seed_development_data():
    """Seed database with test data for development"""
    
    # Create test candidate
    candidate = Candidate(
        email="test@example.com",
        full_name="Test Candidate",
        password_hash=hash_password("TestPass123!"),
        status="active"
    )
    
    # Create test recruiter
    recruiter = Recruiter(
        email="recruiter@teamified.com",
        full_name="Test Recruiter",
        password_hash=hash_password("RecruiterPass123!"),
        role="admin"
    )
    
    # Add sample interview with messages
    # ...
```

---


## Source Tree Structure

```
backend/
├── main.py                      # FastAPI application entrypoint
├── requirements.txt             # UV-managed dependencies
├── pyproject.toml              # Project metadata and tool configs
├── .env.example                # Environment variables template
├── .env                        # Actual environment vars (gitignored)
├── alembic/                    # Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── app/
│   ├── __init__.py
│   ├── core/                   # Core application setup
│   │   ├── __init__.py
│   │   ├── config.py          # Pydantic settings from .env
│   │   ├── database.py        # SQLAlchemy async engine setup
│   │   ├── logging.py         # Structlog configuration
│   │   └── security.py        # JWT/bcrypt utilities
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── candidate.py
│   │   ├── recruiter.py
│   │   ├── resume.py
│   │   ├── interview.py
│   │   └── assessment.py
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── candidate.py
│   │   ├── interview.py
│   │   └── assessment.py
│   ├── repositories/          # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py           # BaseRepository abstract class
│   │   ├── candidate.py
│   │   ├── resume.py
│   │   ├── interview.py
│   │   └── session.py
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── interview_engine.py
│   │   ├── speech_service.py
│   │   ├── resume_parser.py
│   │   └── scoring_service.py
│   ├── providers/             # External API abstractions
│   │   ├── __init__.py
│   │   ├── base_ai_provider.py       # Abstract class
│   │   ├── openai_provider.py
│   │   └── base_speech_provider.py
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── deps.py           # FastAPI dependencies
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py       # /api/v1/auth
│   │   │   ├── candidates.py # /api/v1/candidates
│   │   │   ├── resumes.py    # /api/v1/resumes
│   │   │   ├── interviews.py # /api/v1/interviews
│   │   │   └── assessments.py # /api/v1/assessments
│   ├── middleware/            # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── logging_middleware.py
│   │   └── rate_limit_middleware.py
│   ├── prompts/              # LLM prompt templates
│   │   ├── interview_system.txt
│   │   ├── resume_parser.txt
│   │   └── feedback_generator.txt
│   └── utils/                # Helper functions
│       ├── __init__.py
│       ├── audio_utils.py
│       ├── token_counter.py
│       └── validators.py
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_interview_engine.py
│   │   └── test_scoring_service.py
│   ├── integration/
│   │   ├── test_interview_flow.py
│   │   ├── test_resume_upload.py
│   │   └── test_api_endpoints.py
│   └── e2e/
│       └── test_complete_interview.py
├── scripts/                  # Utility scripts
│   ├── seed_dev_data.py
│   ├── migrate_db.sh
│   └── run_local.sh
└── Dockerfile               # Container definition

```

**Key Design Decisions:**

1. **Service Layer Separation:** Business logic in `services/` completely decoupled from API routes
2. **Repository Pattern:** All database access isolated in `repositories/`, enables easy mocking
3. **Provider Abstraction:** External APIs in `providers/` with abstract base classes for future provider swaps
4. **Prompt Versioning:** LLM prompts stored as files for easy version control and A/B testing
5. **Test Organization:** Unit → Integration → E2E hierarchy matching testing pyramid

---

## Infrastructure & Deployment

### Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.11.9-slim

WORKDIR /app

# Install UV package manager
RUN pip install uv

# Copy dependency files
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

**docker-compose.yml (Local Development):**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/teamified
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - db
    volumes:
      - ./backend:/app

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=teamified
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
```

---

### GitHub Actions CI/CD Pipeline

**.github/workflows/backend-ci.yml:**
```yaml
name: Backend CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.11.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.11.9'
      
      - name: Install UV
        run: pip install uv
      
      - name: Install dependencies
        run: |
          cd backend
          uv pip install -r requirements.txt
      
      - name: Run linters
        run: |
          cd backend
          ruff check .
          black --check .
          mypy app/
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Staging
        run: |
          # Deploy commands (Docker push, Kubernetes apply, etc.)
          echo "Deploying to staging..."

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Production
        run: |
          # Production deployment with approval gate
          echo "Deploying to production..."
```

---

### Environment Configuration

**.env.example:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/teamified

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Authentication
JWT_SECRET=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# Application
ENVIRONMENT=development  # development | staging | production
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

---

## Error Handling & Logging

### Exception Hierarchy

```python
# app/core/exceptions.py

class TeamifiedBaseException(Exception):
    """Base exception for all custom exceptions"""
    pass

class AuthenticationError(TeamifiedBaseException):
    """Raised when authentication fails"""
    pass

class AuthorizationError(TeamifiedBaseException):
    """Raised when user lacks permission"""
    pass

class ResourceNotFoundError(TeamifiedBaseException):
    """Raised when requested resource doesn't exist"""
    pass

class ExternalAPIError(TeamifiedBaseException):
    """Raised when external API call fails"""
    pass

class OpenAIRateLimitError(ExternalAPIError):
    """Raised when OpenAI rate limit hit"""
    pass

class DataValidationError(TeamifiedBaseException):
    """Raised when data validation fails"""
    pass
```

### Global Error Handler

```python
# app/api/error_handlers.py

from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(TeamifiedBaseException)
async def custom_exception_handler(request: Request, exc: TeamifiedBaseException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(AuthenticationError)
async def auth_exception_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "Unauthorized", "message": str(exc)}
    )
```

### Structured Logging

```python
# app/core/logging.py

import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage example:
logger.info("interview_started", interview_id=str(interview_id), candidate_id=str(candidate_id))
logger.error("openai_api_failure", error=str(exc), retry_attempt=3)
```

---

## Coding Standards

### Python Style Guide

**1. Type Hints (Required):**
```python
# ✅ Good
async def create_interview(candidate_id: UUID, resume_id: Optional[UUID]) -> Interview:
    pass

# ❌ Bad
async def create_interview(candidate_id, resume_id):
    pass
```

**2. Naming Conventions:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

**3. Async Everywhere:**
```python
# ✅ All I/O operations must be async
async def get_candidate(candidate_id: UUID) -> Candidate:
    return await candidate_repo.get_by_id(candidate_id)
```

**4. Dependency Injection:**
```python
# ✅ Use FastAPI dependencies
@router.post("/interviews")
async def create_interview(
    candidate: Candidate = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    pass
```

**5. Error Handling:**
```python
# ✅ Always handle external API failures
try:
    response = await openai_provider.generate_question(context)
except OpenAIRateLimitError:
    logger.warning("rate_limit_hit", retry_after=60)
    raise HTTPException(status_code=429, detail="Please try again in 1 minute")
```

### Critical Rules for AI Code Generation

**🚨 NEVER:**
- Use `console.log()` (Python has no console.log, use `logger.info()`)
- Store passwords in plaintext
- Expose API keys in frontend code
- Skip input validation on API endpoints
- Use `SELECT *` in queries (specify columns)

**✅ ALWAYS:**
- Use structured logging with context: `logger.info("event_name", key=value)`
- Wrap all API responses in standard format: `{"success": true, "data": {...}}`
- Use repository pattern for database access
- Validate request bodies with Pydantic schemas
- Use async/await for I/O operations

---

## Test Strategy

### Testing Pyramid

```
           /\
          /E2E\        10% - End-to-end tests (full workflows)
         /______\
        /        \
       /Integration\ 30% - Integration tests (service + DB)
      /____________\
     /              \
    /      Unit      \ 60% - Unit tests (pure logic)
   /__________________\
```

### Unit Tests (60% of tests)

```python
# tests/unit/test_auth_service.py

@pytest.mark.asyncio
async def test_register_candidate_success():
    # Arrange
    mock_repo = Mock(spec=CandidateRepository)
    mock_repo.get_by_email.return_value = None  # Email available
    auth_service = AuthService(candidate_repo=mock_repo)
    
    # Act
    candidate = await auth_service.register_candidate(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
    
    # Assert
    assert candidate.email == "test@example.com"
    assert candidate.password_hash != "SecurePass123!"  # Hashed
    mock_repo.create.assert_called_once()
```

### Integration Tests (30% of tests)

```python
# tests/integration/test_interview_flow.py

@pytest.mark.asyncio
async def test_complete_interview_flow(test_db, test_candidate):
    # Uses real database (test instance)
    interview_service = InterviewService(db=test_db)
    
    # Start interview
    interview = await interview_service.start_interview(
        candidate_id=test_candidate.id,
        role_type="react"
    )
    
    # Simulate Q&A
    await interview_service.process_response(interview.id, "I have 3 years React experience")
    
    # Complete interview
    result = await interview_service.complete_interview(interview.id)
    
    assert result.status == "completed"
    assert result.assessment is not None
```

### E2E Tests (10% of tests)

```python
# tests/e2e/test_complete_interview.py

@pytest.mark.e2e
async def test_candidate_completes_interview_via_api(test_client):
    # Uses FastAPI TestClient
    # 1. Register
    response = await test_client.post("/api/v1/auth/register", json={
        "email": "e2e@example.com",
        "password": "Pass123!",
        "full_name": "E2E Test"
    })
    assert response.status_code == 201
    token = response.json()["token"]
    
    # 2. Start interview
    response = await test_client.post(
        "/api/v1/interviews",
        headers={"Authorization": f"Bearer {token}"},
        json={"role_type": "react"}
    )
    interview_id = response.json()["id"]
    
    # 3. Submit answers (mocked audio)
    # ...
    
    # 4. Complete and verify results
    response = await test_client.post(f"/api/v1/interviews/{interview_id}/complete")
    assert response.status_code == 200
```

### Test Fixtures

```python
# tests/conftest.py

@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI API calls"""
    provider = Mock(spec=OpenAIProvider)
    provider.generate_question.return_value = "What is React?"
    provider.transcribe_audio.return_value = TranscriptionResult(text="My answer")
    return provider
```

---

## Security

### Input Validation

**1. Pydantic at API Boundary:**
```python
class CreateInterviewRequest(BaseModel):
    role_type: Literal["react", "python", "javascript", "fullstack"]
    resume_id: Optional[UUID] = None
    
    @validator("role_type")
    def validate_role_type(cls, v):
        if v not in ["react", "python", "javascript", "fullstack"]:
            raise ValueError("Invalid role type")
        return v
```

**2. SQL Injection Prevention:**
```python
# ✅ SQLAlchemy ORM automatically parameterizes
result = await session.execute(
    select(Candidate).where(Candidate.email == email)
)
```

### Authentication & Authorization

**JWT Implementation:**
```python
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(user_id: UUID) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return UUID(payload["sub"])
    except JWTError:
        raise AuthenticationError("Invalid token")
```

### API Security

**1. Rate Limiting:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.client.host)

@router.post("/interviews")
@limiter.limit("10/hour")  # Max 10 interview starts per hour
async def start_interview(...):
    pass
```

**2. CORS Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://teamified.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**3. Security Headers:**
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### Data Protection

**1. Encryption at Rest:** Supabase PostgreSQL encrypts data at rest by default

**2. Encryption in Transit:** HTTPS enforced in production (nginx reverse proxy)

**3. PII Handling:**
```python
# ✅ Never log PII
logger.info("candidate_registered", candidate_id=str(candidate_id))  # ✅

# ❌ Don't log sensitive data
logger.info("candidate_registered", email=email, password=password)  # ❌
```

**4. Secrets Management:**
```python
# ✅ Load from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ❌ Never hardcode
OPENAI_API_KEY = "sk-abc123..."  # ❌ NEVER DO THIS
```

---

## Deployment Checklist

**Pre-Production:**
- [ ] Environment variables configured in production
- [ ] Database migrations tested on staging
- [ ] HTTPS certificates installed
- [ ] Rate limiting configured
- [ ] CORS origins whitelisted
- [ ] Backup strategy implemented
- [ ] Monitoring/alerting configured
- [ ] Security headers enabled
- [ ] API keys rotated
- [ ] Test coverage >80%

**Post-Deployment:**
- [ ] Smoke tests passed
- [ ] Health check endpoint responding
- [ ] Database connection pool stable
- [ ] OpenAI API calls succeeding
- [ ] Log aggregation working
- [ ] Error tracking operational

---

## Next Steps

This backend architecture document provides a comprehensive blueprint for AI-driven development. Recommended next actions:

1. **Generate OpenAPI Specification** - Use FastAPI's auto-generated docs as starting point
2. **Create Alembic Initial Migration** - Run `alembic revision --autogenerate`
3. **Set Up Development Environment** - `docker-compose up` for local PostgreSQL
4. **Implement Core Services** - Start with Auth Service → Interview Engine → Speech Service
5. **Write Integration Tests** - Test database interactions early
6. **Configure CI/CD Pipeline** - GitHub Actions for automated testing

**Questions to Address:**
1. Which deployment platform? (AWS, GCP, Azure, DigitalOcean, Render, Fly.io)
2. Backup retention policy? (Daily for 30 days recommended)
3. Monitoring solution? (Datadog, New Relic, or defer to logging for MVP)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-28  
**Author:** Winston (Architect)

