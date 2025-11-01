# Introduction

This document outlines the backend architecture for **Teamified Candidates Portal**, including server-side systems, AI services integration, database design, API specifications, and infrastructure. Its primary goal is to serve as the guiding architectural blueprint for AI-driven backend development, ensuring consistency and adherence to chosen patterns and technologies.

**Relationship to Frontend Architecture:**

This backend architecture works in conjunction with the existing [Frontend Architecture Document](../../ui-architecture.md). The frontend handles user interactions, real-time audio capture, and visual components, while this backend architecture manages:
- AI interview orchestration (OpenAI GPT-4 via LangChain)
- Speech processing (OpenAI Whisper STT + OpenAI TTS)
- Assessment scoring and integrity analysis
- Resume parsing and candidate data management
- RESTful APIs and external integrations
- Database persistence and state management

Core technology stack choices documented in the "Tech Stack" section are definitive for the entire project.

## Starter Template or Existing Project

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

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-28 | 1.0 | Initial backend architecture document creation | Winston (Architect) |
| 2025-11-01 | 1.1 | Added Speech Services integration (Story 1.5.1): OpenAI Whisper STT/TTS provider abstraction, cost tracking, audio metadata persistence | Winston (Architect) |

---

