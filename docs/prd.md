# Teamified Candidates Portal Product Requirements Document (PRD)

> **Note:** This PRD has been sharded into multiple files for better organization and maintainability.
> 
> **📂 View the complete PRD:** [docs/prds/](./prds/)  
> **📂 View epics:** [docs/epics/](./epics/)

## Quick Navigation

### Requirements & Design
- **[Index & Overview](./prds/00-index.md)** - Complete table of contents
- **[Goals & Background](./prds/01-goals-background.md)** - Project goals, background, change log
- **[Requirements](./prds/02-requirements.md)** - Functional and non-functional requirements (FR1-FR20, NFR1-NFR15)
- **[UI Design Goals](./prds/03-ui-design-goals.md)** - UX vision, interaction paradigms, core screens
- **[Technical Assumptions](./prds/04-technical-assumptions.md)** - Repository structure, service architecture, testing, risks
- **[Checklist Results](./prds/05-checklist-results.md)** - PM checklist validation results
- **[Next Steps](./prds/06-next-steps.md)** - Actions for UX Expert and Architect
- **[Epic List](./prds/07-epic-list.md)** - Overview of all epics

### Epic Breakdown
- **[Epic Index](./epics/00-index.md)** - All epics with descriptions
- **[Epic 01: Foundation & Core AI Interview Engine](./epics/epic-01-foundation.md)**
  - Story 1.1: Project Initialization & Monorepo Setup
  - Story 1.2: Database Schema & Core Data Models
  - Story 1.3: Authentication & Candidate Session Management
  - Story 1.4: OpenAI Integration & LangChain Setup
  - Story 1.5: Progressive Assessment Engine - Core Logic
  - Story 1.6: Candidate Interview UI - Text Chat Interface
  - Story 1.7: Real-Time Interview Conversation Flow
  - Story 1.8: Interview Completion & Basic Results
  - Story 1.9: CI/CD Pipeline & Deployment Foundation
  
- **[Epic 01.5: Speech-to-Speech AI Interview Capability](./epics/epic-01.5-speech.md)**
  - Story 1.5.1: OpenAI Speech Services Integration (Backend-Processed)
  - Story 1.5.2: Real-Time Audio Capture - Frontend
  - Story 1.5.3: Speech-to-Text Processing Pipeline
  - Story 1.5.4: Text-to-Speech AI Response Generation
  - Story 1.5.5: Voice-Based Interview UI Enhancement
  - Story 1.5.6: Hybrid Input Mode - Voice + Text
  - Story 1.5.7: WebRTC Audio Streaming Setup
  - Story 1.5.8: Audio Metadata Analysis for Integrity Monitoring
  - Story 1.5.9: Graceful Degradation & Fallback Handling

---

**For AI Agents:** Load specific sections from `docs/prds/` for requirements or `docs/epics/` for story details.
