# High Level Architecture

## Technical Summary

Teamified Candidates Portal backend follows a **monolithic architecture with microservices-ready design**, leveraging Python 3.11.9 and FastAPI for high-performance async operations. The system orchestrates AI-driven technical interviews through OpenAI GPT-4 (via LangChain), processes speech using OpenAI Whisper/TTS, and persists data in PostgreSQL (Supabase). Key architectural patterns include Repository Pattern for data access, Service Layer for business logic, and provider-agnostic abstractions for AI services enabling future cloud migration. This design supports the PRD's goal of 50+ concurrent interview sessions with <2 second AI response times while maintaining clear boundaries for eventual microservices extraction.

## High Level Overview

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

\`\`\`
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
\`\`\`

**5. Key Architectural Decisions**

- **OpenAI as Primary AI Provider** - Single vendor for LLM + Speech simplifies MVP
- **LangChain for AI Orchestration** - Manages conversation memory, prompt templates, token optimization
- **Provider Abstraction Layer** - Clean interfaces enable Azure/GCP migration without breaking changes
- **PostgreSQL with JSONB** - Flexible schema for AI-generated data (scores, reasoning, red flags)
- **Async FastAPI** - Native async/await critical for concurrent sessions and external API calls
- **UV Package Management** - 10-100x faster than pip, deterministic builds
- **No Redis/Celery for MVP** - FastAPI async sufficient for pilot scale; defer infrastructure complexity

## High Level Project Diagram

\`\`\`mermaid
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
\`\`\`

## Architectural and Design Patterns

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
