# Teamified Candidates Portal - Complete System Documentation

**Version:** 2.0 (Current State)  
**Last Updated:** November 4, 2025  
**Status:** Comprehensive Production Documentation  
**Target Audience:** Junior & Senior Engineers, AI Agents

---

## 📑 Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview & Architecture](#system-overview--architecture)
3. [How the AI Interview Actually Works (Deep Dive)](#how-the-ai-interview-actually-works-deep-dive)
4. [Tech Stack Reality Check](#tech-stack-reality-check)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Data Models & Database](#data-models--database)
8. [API Endpoints Reference](#api-endpoints-reference)
9. [Key Workflows](#key-workflows)
10. [Development Guide](#development-guide)
11. [Testing Strategy](#testing-strategy)
12. [Deployment & Operations](#deployment--operations)
13. [Known Issues & Technical Debt](#known-issues--technical-debt)
14. [Quick Reference for Common Tasks](#quick-reference-for-common-tasks)

---

## Executive Summary

### What This System Does

Teamified Candidates Portal is an **AI-powered technical interview platform** that enables recruitment consultants to conduct scalable, consistent technical assessments through **natural voice conversations** with candidates. The system uses OpenAI's GPT-4 and Realtime API to conduct adaptive, progressive interviews that assess technical skills across multiple domains.

### Current State (November 2025)

- ✅ **Backend**: Fully functional FastAPI application with PostgreSQL database
- ✅ **Frontend**: Next.js application with real-time audio/video capabilities
- ✅ **AI Interview Engine**: Working with two modes:
  - **Realtime Mode** (Primary): WebSocket-based voice interviews using OpenAI Realtime API
  - **Legacy Mode** (Fallback): STT/TTS pipeline for older browsers
- ✅ **Progressive Assessment**: Adaptive difficulty adjustment based on candidate responses
- ✅ **Video Recording**: Optional candidate video recording with Supabase storage
- 🚧 **Recruiter Portal**: Planned (Epic 02)

### Key Architectural Decisions

1. **Monorepo Structure**: Single repository with separate `backend/` and `frontend/` folders
2. **Two Interview Modes**: Realtime API (WebSocket) as primary, STT/TTS as fallback
3. **Progressive Difficulty**: Dynamic question adjustment based on performance
4. **Supabase for Storage**: Video recordings stored in Supabase buckets
5. **PostgreSQL Database**: Single database with normalized schema

---

## System Overview & Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Auth Pages    │  │ Interview Pages │  │ Dashboard Pages │ │
│  │ /login         │  │ /interview/*    │  │ /dashboard      │ │
│  │ /register      │  │ /tech-check     │  │ /profile        │ │
│  └────────────────┘  └─────────────────┘  └─────────────────┘ │
│                              ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │        Feature Modules (auth, interview, video)           │ │
│  │  - Zustand Stores (state)                                 │ │
│  │  - React Query Hooks (API)                                │ │
│  │  - Custom Hooks (useAudioCapture, useVideoRecorder)       │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                          │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  API Routes    │  │    Services     │  │  Repositories   │ │
│  │  /auth/*       │  │ InterviewEngine │  │ interview_repo  │ │
│  │  /interviews/* │  │ RealtimeService │  │ message_repo    │ │
│  │  /realtime/*   │  │ VideoCleanup    │  │ candidate_repo  │ │
│  │  /videos/*     │  │ AssessmentEngine│  │ (Data Access)   │ │
│  └────────────────┘  └─────────────────┘  └─────────────────┘ │
│                              ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │             External Integrations                         │ │
│  │  - OpenAI API (GPT-4, Whisper, TTS, Realtime)            │ │
│  │  - Supabase Storage (Video recordings)                    │ │
│  │  - PostgreSQL Database (Data persistence)                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Repository Structure

```
BMAD_Sieg/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # API route handlers
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── interviews.py # Interview CRUD and messaging
│   │   │   ├── realtime.py   # WebSocket realtime connection
│   │   │   ├── videos.py     # Video upload/management
│   │   │   └── admin.py      # Admin utilities
│   │   ├── core/             # Core configuration
│   │   │   ├── config.py     # Settings (from .env)
│   │   │   ├── database.py   # SQLAlchemy setup
│   │   │   ├── security.py   # JWT authentication
│   │   │   └── exceptions.py # Custom exceptions
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── candidate.py
│   │   │   ├── interview.py
│   │   │   ├── interview_session.py
│   │   │   ├── interview_message.py
│   │   │   ├── resume.py
│   │   │   ├── assessment.py
│   │   │   └── video_recording.py
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── interview.py
│   │   │   ├── message.py
│   │   │   └── video.py
│   │   ├── repositories/     # Data access layer
│   │   │   ├── base.py
│   │   │   ├── candidate.py
│   │   │   ├── interview.py
│   │   │   ├── interview_session.py
│   │   │   ├── interview_message.py
│   │   │   └── video.py
│   │   ├── services/         # Business logic
│   │   │   ├── interview_engine.py              # Main interview orchestrator
│   │   │   ├── realtime_interview_service.py    # Realtime API manager
│   │   │   ├── progressive_assessment_engine.py # Difficulty adjustment
│   │   │   ├── conversation_memory.py           # Context management
│   │   │   ├── auth_service.py                  # Authentication
│   │   │   └── video_cleanup_service.py         # Video lifecycle
│   │   ├── providers/        # External API wrappers
│   │   │   ├── base_ai_provider.py
│   │   │   └── openai_provider.py
│   │   ├── prompts/          # AI prompt templates
│   │   │   └── interview_prompts.py
│   │   ├── middleware/       # Request middleware
│   │   │   └── error_handler.py
│   │   └── utils/            # Helper utilities
│   │       ├── audio.py
│   │       ├── realtime_cost.py
│   │       └── video_storage.py
│   ├── alembic/              # Database migrations
│   │   └── versions/
│   ├── tests/                # Test suites
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── main.py               # FastAPI app entry point
│   ├── pyproject.toml        # Python dependencies
│   └── alembic.ini           # Migration config
│
├── frontend/
│   ├── app/                  # Next.js App Router (file-based routing)
│   │   ├── layout.tsx        # Root layout (SSR)
│   │   ├── page.tsx          # Home page (/)
│   │   ├── providers.tsx     # React Query provider
│   │   ├── login/page.tsx    # /login route
│   │   ├── register/page.tsx # /register route
│   │   ├── dashboard/page.tsx # /dashboard route
│   │   └── interview/
│   │       ├── start/page.tsx           # /interview/start
│   │       ├── [sessionId]/
│   │       │   ├── page.tsx             # /interview/:id (main interview)
│   │       │   ├── tech-check/page.tsx  # /interview/:id/tech-check
│   │       │   └── results/page.tsx     # /interview/:id/results
│   │       └── practice/page.tsx        # /interview/practice
│   ├── src/
│   │   ├── features/         # Feature modules
│   │   │   ├── auth/
│   │   │   │   ├── components/   # Login/Register forms
│   │   │   │   ├── hooks/        # useAuth, useLogin, useLogout
│   │   │   │   ├── services/     # authService (API calls)
│   │   │   │   ├── store/        # authStore (Zustand)
│   │   │   │   └── types/        # TypeScript types
│   │   │   ├── interview/
│   │   │   │   ├── components/   # Interview UI components
│   │   │   │   │   ├── InterviewChat.tsx
│   │   │   │   │   ├── PushToTalkButton.tsx
│   │   │   │   │   ├── AudioLevelIndicator.tsx
│   │   │   │   │   ├── InterviewControls.tsx
│   │   │   │   │   └── RealtimeStatusIndicator.tsx
│   │   │   │   ├── hooks/        # Interview-specific hooks
│   │   │   │   │   ├── useInterview.ts
│   │   │   │   │   ├── useAudioCapture.ts
│   │   │   │   │   ├── useAudioUpload.ts
│   │   │   │   │   ├── useRealtimeConnection.ts
│   │   │   │   │   └── useSendMessage.ts
│   │   │   │   ├── services/     # API communication
│   │   │   │   │   ├── interviewService.ts
│   │   │   │   │   └── audioService.ts
│   │   │   │   ├── store/        # interviewStore (Zustand)
│   │   │   │   └── types/        # TypeScript types
│   │   │   └── video/
│   │   │       ├── components/   # Video recording UI
│   │   │       ├── hooks/        # useVideoRecorder, useMediaPermissions
│   │   │       ├── services/     # videoService
│   │   │       └── types/
│   │   ├── components/       # Shared components
│   │   │   ├── ui/           # shadcn/ui components (Button, Card, etc.)
│   │   │   └── shared/       # Custom shared components
│   │   ├── services/
│   │   │   └── api/
│   │   │       ├── client.ts      # API client (fetch wrapper)
│   │   │       ├── queryClient.ts # React Query config
│   │   │       └── mocks/         # Mock data for development
│   │   ├── config/
│   │   │   └── env.ts        # Environment variables
│   │   ├── hooks/            # Global hooks
│   │   │   ├── useDebounce.ts
│   │   │   └── useLocalStorage.ts
│   │   └── styles/           # Global styles
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   ├── next.config.mjs       # Next.js configuration
│   └── tsconfig.json         # TypeScript configuration
│
├── docs/                     # Documentation
│   ├── prds/                 # Product requirements (sharded)
│   ├── epics/                # Epic breakdowns
│   ├── stories/              # User stories
│   ├── architecture/         # Architecture docs
│   │   ├── backend/          # Backend architecture (sharded)
│   │   ├── frontend/         # Frontend architecture (sharded)
│   │   └── coding-standards.md
│   └── COMPLETE-SYSTEM-DOCUMENTATION.md  # THIS FILE
│
├── .github/                  # CI/CD workflows
├── README.md                 # Quick start guide
└── SETUP.md                  # Detailed setup instructions
```

---

## How the AI Interview Actually Works (Deep Dive)

This is the **most complex part** of the system. Understanding this is critical for debugging and adding features.

### The Two Interview Modes

The system supports two distinct interview modes:

1. **Realtime Mode (Primary)** - WebSocket-based real-time voice conversation
2. **Legacy Mode (Fallback)** - Traditional STT → AI → TTS pipeline

**Default Behavior**: System uses Realtime Mode unless:
- Browser doesn't support WebSocket or Web Audio API
- User explicitly toggles to Legacy Mode
- WebSocket connection fails 3 times

### Mode 1: Realtime Interview Flow (WebSocket-Based)

This is how **most interviews** work in production.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        REALTIME INTERVIEW FLOW                       │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Interview Initialization
================================
Frontend (/interview/start)
    ↓ POST /api/v1/interviews/start
    ↓   { role_type: "react", resume_id: null }
Backend (interviews.py → start_interview())
    ↓ Creates Interview record (status: "in_progress")
    ↓ Creates InterviewSession record (difficulty: "warmup")
    ↓ Generates first AI question (system prompt + role context)
    ↓ Returns interview_id
Frontend
    ↓ Navigates to /interview/:id/tech-check
    ↓ Tests microphone + camera
    ↓ After approval → Navigate to /interview/:id (main interview page)

Step 2: WebSocket Connection Establishment
==========================================
Frontend (interview/[sessionId]/page.tsx)
    ↓ useRealtimeConnection() hook initializes
    ↓ const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/:session_id')
    ↓ On open → Send session.create with config
Backend (realtime.py → websocket_endpoint())
    ↓ Accepts WebSocket connection
    ↓ Loads InterviewSession from database
    ↓ Calls RealtimeInterviewService.initialize_session()
    ↓ Generates system prompt via InterviewEngine.get_realtime_system_prompt()
    ↓ Creates OpenAI Realtime API session
    ↓ Opens WebSocket to OpenAI wss://api.openai.com/v1/realtime
    ↓ Sends session.update with:
    ↓   - instructions (system prompt with interview context)
    ↓   - tools (function definitions for evaluation)
    ↓   - turn_detection (server VAD config)
    ↓   - voice, temperature, max_tokens
OpenAI Realtime API
    ↓ Returns session.created event
    ↓ AI immediately starts speaking (greeting)
Backend
    ↓ Forwards session.created to frontend
Frontend
    ↓ Updates connectionState: "connected"
    ↓ Starts audio playback for AI greeting

Step 3: AI Asks First Question (Audio Output)
==============================================
OpenAI Realtime API
    ↓ Generates greeting + first question (text)
    ↓ Synthesizes audio (TTS inline)
    ↓ Streams audio.delta events (PCM16 chunks)
Backend
    ↓ Buffers audio chunks
    ↓ Forwards to frontend via WebSocket
Frontend (useRealtimeConnection)
    ↓ Receives audio.delta events
    ↓ Decodes base64 PCM16 audio
    ↓ Plays via Web Audio API (AudioContext)
    ↓ Updates UI: interviewState = "ai_speaking"
    ↓ Shows audio waveform animation
AI Finishes Speaking
    ↓ OpenAI sends response.done event
Frontend
    ↓ Updates UI: interviewState = "candidate_turn"
    ↓ Enables "Hold to Speak" button
    ↓ Activates microphone

Step 4: Candidate Responds (Audio Input)
=========================================
Frontend
    ↓ Candidate presses "Hold to Speak" button
    ↓ useAudioCapture() starts recording
    ↓ Captures audio from navigator.mediaDevices.getUserMedia()
    ↓ Records as PCM16 format
    ↓ While recording:
    ↓   - Shows audio level indicator
    ↓   - Updates UI: interviewState = "candidate_speaking"
    ↓ Candidate releases button
    ↓ Stops recording
    ↓ Sends audio chunks to backend via WebSocket
    ↓   Event: input_audio_buffer.append (base64 PCM16)
Backend
    ↓ Receives input_audio_buffer.append
    ↓ Forwards directly to OpenAI Realtime API
OpenAI Realtime API
    ↓ Buffers audio in input_audio_buffer
    ↓ When candidate stops speaking (VAD detection):
    ↓   - Sends input_audio_buffer.committed event
    ↓   - Transcribes audio (Whisper inline)
    ↓   - Sends conversation.item.created (transcript)
    ↓   - Sends conversation.item.input_audio_transcription.completed
Backend
    ↓ Receives transcript
    ↓ Forwards to frontend
Frontend
    ↓ Displays transcript in chat UI
    ↓ Adds message to store: { role: "candidate", content: transcript }

Step 5: AI Evaluates Response (Function Calling)
=================================================
OpenAI Realtime API
    ↓ Analyzes candidate's answer internally
    ↓ Decides to call function: evaluate_candidate_answer
    ↓ Sends response.function_call_arguments.delta events
    ↓ Arguments: {
    ↓   "answer_quality": "good",
    ↓   "technical_accuracy": 0.8,
    ↓   "explanation_clarity": 0.7,
    ↓   "identified_skills": ["React hooks", "useState"],
    ↓   "skill_boundaries_detected": { "React hooks": "comfortable" }
    ↓ }
Backend (RealtimeInterviewService)
    ↓ Receives function call
    ↓ Calls handle_function_call()
    ↓ Updates InterviewSession in database:
    ↓   - Increments questions_asked_count
    ↓   - Updates skill_boundaries_identified
    ↓   - Adds to progression_state.response_quality_history
    ↓ Calls ProgressiveAssessmentEngine.update_after_response()
    ↓   - Analyzes response quality
    ↓   - Decides if difficulty should change
    ↓   - If quality high → increase difficulty
    ↓   - If quality low → decrease difficulty or probe deeper
    ↓ Generates next question using InterviewEngine
    ↓   - Uses updated difficulty level
    ↓   - Considers skills already explored
    ↓   - Generates contextual follow-up
    ↓ Returns function result to OpenAI:
    ↓   {
    ↓     "evaluation_recorded": true,
    ↓     "next_question": "Can you explain how useEffect works?",
    ↓     "difficulty_adjusted": true,
    ↓     "new_difficulty": "intermediate"
    ↓   }
OpenAI Realtime API
    ↓ Receives function result
    ↓ Uses next_question as context
    ↓ Generates natural response incorporating next question
    ↓ Synthesizes audio (TTS)
    ↓ Streams audio.delta events
Frontend
    ↓ Plays AI's next question
    ↓ Cycle repeats (Steps 3-5) until interview complete

Step 6: Interview Completion
=============================
After 8-12 questions (configured in AssessmentEngine):
Backend
    ↓ Detects completion criteria:
    ↓   - Minimum questions asked (8)
    ↓   - Skill boundaries identified for key areas
    ↓   - Time limit reached (optional)
    ↓ Calls Interview.complete()
    ↓ Updates database:
    ↓   - Sets status = "completed"
    ↓   - Records completed_at timestamp
    ↓   - Calculates duration_seconds
    ↓   - Saves final skill_boundaries_identified
    ↓ Closes WebSocket connection
Frontend
    ↓ Receives connection close event
    ↓ Shows "Interview Complete" message
    ↓ Navigates to /interview/:id/results
    ↓ Displays assessment summary
```

### Mode 2: Legacy Interview Flow (STT/TTS Pipeline)

This is the **fallback mode** for older browsers or when Realtime API unavailable.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LEGACY INTERVIEW FLOW                         │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Interview Initialization
================================
(Same as Realtime Mode - creates Interview and InterviewSession)

Step 2: AI Generates First Question
===================================
Backend (InterviewEngine.start_interview)
    ↓ Generates first question text
    ↓ Calls OpenAI TTS API (POST /v1/audio/speech)
    ↓   { input: "Hello! Let's start...", voice: "alloy", model: "tts-1" }
    ↓ Receives audio file (MP3)
    ↓ Saves to temporary storage
    ↓ Returns { question_text, audio_url }
Frontend
    ↓ Displays question text in chat
    ↓ Plays audio using HTML5 <audio> element
    ↓ When audio ends → Enables "Hold to Speak" button

Step 3: Candidate Records Response
===================================
Frontend (useAudioCapture)
    ↓ Candidate holds "Speak" button
    ↓ Starts MediaRecorder (WebM/Opus format)
    ↓ Records audio chunks
    ↓ Candidate releases button
    ↓ Stops recording
    ↓ Creates Blob from recorded chunks
    ↓ Sends to backend: POST /api/v1/interviews/:id/messages
    ↓   FormData: { audio_file: Blob, message_sequence: int }

Step 4: Backend Processes Audio
================================
Backend (interviews.py → send_message)
    ↓ Receives audio file
    ↓ Validates file size (<25MB)
    ↓ Calls OpenAI Whisper API (POST /v1/audio/transcriptions)
    ↓   FormData: { file: audio, model: "whisper-1", language: "en" }
    ↓ Receives transcript: { text: "I use useState for managing..." }
    ↓ Saves InterviewMessage:
    ↓   { type: "candidate_response", content_text: transcript }
    ↓ Calls InterviewEngine.process_candidate_response()
    ↓   - Analyzes answer quality
    ↓   - Updates assessment state
    ↓   - Generates next question
    ↓ Calls OpenAI TTS for AI's response
    ↓ Returns {
    ↓   transcript,
    ↓   ai_response_text,
    ↓   ai_audio_url,
    ↓   question_number,
    ↓   session_state
    ↓ }

Step 5: Frontend Displays Response
===================================
Frontend
    ↓ Receives response
    ↓ Adds transcript to chat: { role: "candidate", content: transcript }
    ↓ Adds AI response to chat: { role: "ai", content: ai_response_text }
    ↓ Plays AI audio
    ↓ Cycle repeats until interview complete
```

### Progressive Difficulty Adjustment Algorithm

The **most intelligent part** of the system - adapts difficulty dynamically.

```python
# backend/app/services/progressive_assessment_engine.py

class ProgressiveAssessmentEngine:
    """
    Adaptive difficulty adjustment based on candidate performance.
    
    Difficulty Levels:
    - warmup:        Easy getting-started questions (no wrong answers)
    - fundamental:   Basic concepts and syntax
    - intermediate:  Practical application, problem-solving
    - advanced:      Architecture, optimization, edge cases
    - expert:        System design, performance tuning
    """
    
    def update_after_response(
        self,
        session: InterviewSession,
        answer_quality: str,  # "excellent", "good", "fair", "poor"
        technical_accuracy: float,  # 0.0 to 1.0
        explanation_clarity: float  # 0.0 to 1.0
    ) -> DifficultyAdjustment:
        """
        Decide whether to increase, decrease, or maintain difficulty.
        
        Logic:
        1. If answer_quality = "excellent" AND technical_accuracy > 0.8:
           → Increase difficulty (if not already at max)
        
        2. If answer_quality = "poor" OR technical_accuracy < 0.5:
           → Decrease difficulty (find skill boundary)
        
        3. If answer_quality = "good" or "fair":
           → Stay at current level, probe deeper in same domain
        
        4. Special case - Warmup phase:
           → After 2 questions, always move to fundamental
           → Never decrease from warmup
        
        5. Boundary detection:
           → If 2 consecutive "poor" answers at same level:
              → Skill boundary found! Mark as "struggling at X level"
           → If 3 consecutive "excellent" answers:
              → Increase difficulty aggressively
        """
        current_difficulty = session.current_difficulty_level
        
        # Warmup phase logic
        if current_difficulty == "warmup":
            if session.questions_asked_count >= 2:
                return DifficultyAdjustment(
                    new_level="fundamental",
                    reason="Completed warmup phase"
                )
        
        # Calculate composite score
        composite_score = (
            technical_accuracy * 0.6 +
            explanation_clarity * 0.3 +
            quality_score_map[answer_quality] * 0.1
        )
        
        # Get recent performance history
        recent_scores = get_last_n_scores(session, n=3)
        
        # Increase difficulty if performing well
        if composite_score > 0.8 and all(s > 0.75 for s in recent_scores):
            if can_increase_difficulty(current_difficulty):
                return DifficultyAdjustment(
                    new_level=next_difficulty_level(current_difficulty),
                    reason="Consistently strong performance"
                )
        
        # Decrease difficulty if struggling
        if composite_score < 0.5 and any(s < 0.55 for s in recent_scores):
            if can_decrease_difficulty(current_difficulty):
                # Mark boundary
                mark_skill_boundary(
                    session,
                    current_skill="react_hooks",  # Extracted from context
                    boundary_level=current_difficulty,
                    boundary_type="upper_limit"
                )
                return DifficultyAdjustment(
                    new_level=previous_difficulty_level(current_difficulty),
                    reason="Skill boundary detected"
                )
        
        # Maintain current level
        return DifficultyAdjustment(
            new_level=current_difficulty,
            reason="Continue exploring at current level"
        )
```

### Conversation Memory Management

Prevents context window overflow while maintaining conversation coherence.

```python
# backend/app/services/conversation_memory.py

class ConversationMemoryManager:
    """
    Manages conversation history to fit within AI context limits.
    
    Strategy:
    - Keep last 6 message pairs (12 messages total)
    - Preserve first 2 messages (greeting + first Q&A)
    - Summarize older messages if needed
    - Track important facts for context
    """
    
    MAX_MESSAGES = 12
    PRESERVE_FIRST_N = 2
    
    def add_message(self, session: InterviewSession, message: dict) -> None:
        """Add message and truncate if needed."""
        messages = session.conversation_memory.get("messages", [])
        messages.append(message)
        
        # Truncate if exceeded limit
        if len(messages) > self.MAX_MESSAGES:
            # Keep first 2 (greeting + initial Q&A)
            preserved = messages[:self.PRESERVE_FIRST_N]
            
            # Keep last 10
            recent = messages[-(self.MAX_MESSAGES - self.PRESERVE_FIRST_N):]
            
            # Combine
            messages = preserved + recent
            
            # Update metadata
            session.conversation_memory["memory_metadata"]["truncation_count"] += 1
        
        session.conversation_memory["messages"] = messages
```

### Cost Tracking

Monitors OpenAI API costs in real-time.

```python
# backend/app/utils/realtime_cost.py

# OpenAI Realtime API Pricing (as of Nov 2024)
REALTIME_PRICING = {
    "input_audio_per_minute": 0.06,   # $0.06 per minute of audio input
    "output_audio_per_minute": 0.24,  # $0.24 per minute of audio output
    "text_input_per_1M": 5.00,        # $5.00 per 1M input tokens
    "text_output_per_1M": 20.00       # $20.00 per 1M output tokens
}

def calculate_realtime_cost(
    audio_input_seconds: float,
    audio_output_seconds: float,
    text_input_tokens: int,
    text_output_tokens: int
) -> Decimal:
    """
    Calculate total cost for a realtime session.
    
    Example:
    - 5 minutes of candidate audio input
    - 3 minutes of AI audio output
    - 2000 text tokens (function calls)
    
    Cost = (5 * 0.06) + (3 * 0.24) + (2000/1M * 5.00)
         = 0.30 + 0.72 + 0.01
         = $1.03
    """
    audio_input_cost = (audio_input_seconds / 60) * REALTIME_PRICING["input_audio_per_minute"]
    audio_output_cost = (audio_output_seconds / 60) * REALTIME_PRICING["output_audio_per_minute"]
    text_input_cost = (text_input_tokens / 1_000_000) * REALTIME_PRICING["text_input_per_1M"]
    text_output_cost = (text_output_tokens / 1_000_000) * REALTIME_PRICING["text_output_per_1M"]
    
    total = audio_input_cost + audio_output_cost + text_input_cost + text_output_cost
    return Decimal(str(round(total, 4)))

# Cost threshold check
async def check_cost_threshold(interview: Interview) -> bool:
    """Return True if cost exceeds $5.00 per interview."""
    total_cost = (
        interview.cost_usd +
        interview.speech_cost_usd +
        interview.realtime_cost_usd
    )
    return total_cost > Decimal("5.00")
```

---

## Tech Stack Reality Check

### Backend Technologies (Python)

| Technology | Version | Purpose | Status |
|------------|---------|---------|--------|
| **Python** | 3.11.9 | Runtime environment | ✅ Production |
| **FastAPI** | 0.104.1 | Web framework | ✅ Production |
| **Uvicorn** | 0.24+ | ASGI server | ✅ Production |
| **SQLAlchemy** | 2.0+ | ORM for database | ✅ Production |
| **Alembic** | 1.12+ | Database migrations | ✅ Production |
| **PostgreSQL** | 15+ | Primary database | ✅ Production |
| **Pydantic** | 2.5+ | Data validation | ✅ Production |
| **LangChain** | 0.1.0+ | AI orchestration | ✅ Production |
| **OpenAI SDK** | 1.0.0+ | OpenAI API client | ✅ Production |
| **Supabase** | 2.23.0+ | Storage client | ✅ Production |
| **structlog** | 23.2+ | Structured logging | ✅ Production |
| **pytest** | 7.4+ | Testing framework | ✅ Development |

### Frontend Technologies (TypeScript/React)

| Technology | Version | Purpose | Status |
|------------|---------|---------|--------|
| **Node.js** | 24.6.0 | Runtime | ✅ Production |
| **Next.js** | 16 (App Router) | React framework | ✅ Production |
| **React** | 19 | UI library | ✅ Production |
| **TypeScript** | 5.0+ | Type safety | ✅ Production |
| **Tailwind CSS** | 3.4+ | Styling | ✅ Production |
| **shadcn/ui** | Latest | Component library | ✅ Production |
| **TanStack Query** | 5.0+ | Data fetching | ✅ Production |
| **Zustand** | 4.5+ | State management | ✅ Production |
| **React Hook Form** | 7.0+ | Form handling | ✅ Production |
| **Zod** | 3.22+ | Schema validation | ✅ Production |
| **Lucide React** | Latest | Icons | ✅ Production |
| **Vitest** | Latest | Testing framework | ✅ Development |

### External Services

| Service | Purpose | Integration | Cost |
|---------|---------|-------------|------|
| **OpenAI API** | GPT-4, Whisper, TTS, Realtime | Direct HTTP/WebSocket | Pay-per-use |
| **Supabase** | Video storage | SDK | Free tier available |
| **PostgreSQL** | Database | Direct connection | Self-hosted |

### Development Tools

| Tool | Purpose |
|------|---------|
| **pyenv** | Python version management |
| **UV** | Fast Python package manager |
| **pnpm** | Node.js package manager |
| **ESLint** | JavaScript/TypeScript linting |
| **Ruff** | Python linting |
| **Black** | Python code formatting |
| **Prettier** | Frontend code formatting |

---

## Backend Architecture

### Layer Architecture

The backend follows a **clean architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  - Route handlers (app/api/v1/*.py)                         │
│  - Request validation (Pydantic schemas)                    │
│  - Response formatting                                      │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│  - Business logic (app/services/*.py)                       │
│  - Interview orchestration                                  │
│  - Assessment algorithms                                    │
│  - External API coordination                                │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   Repository Layer                           │
│  - Data access (app/repositories/*.py)                      │
│  - CRUD operations                                          │
│  - Query composition                                        │
│  - Transaction management                                   │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  - ORM Models (app/models/*.py)                             │
│  - Database schema                                          │
│  - Relationships                                            │
└─────────────────────────────────────────────────────────────┘
```

### Core Services

#### 1. InterviewEngine

**Location**: `backend/app/services/interview_engine.py`

**Purpose**: Main orchestrator for interview sessions. Coordinates all interview logic.

**Key Methods**:
- `start_interview()` - Initialize new interview session
- `get_realtime_system_prompt()` - Generate AI instructions
- `process_candidate_response()` - (Legacy mode) Handle text responses
- `complete_interview()` - Finalize and calculate results

**Dependencies**:
- `ProgressiveAssessmentEngine` - Difficulty adjustment
- `ConversationMemoryManager` - Context management
- `AIProvider` (OpenAI) - AI completions
- `InterviewSessionRepository` - Data persistence

#### 2. RealtimeInterviewService

**Location**: `backend/app/services/realtime_interview_service.py`

**Purpose**: Manages OpenAI Realtime API WebSocket connections.

**Key Methods**:
- `initialize_session()` - Create Realtime API session config
- `handle_function_call()` - Process evaluation function calls
- `_build_system_instructions()` - Generate context-aware prompts
- `_get_function_definitions()` - Define available functions for AI

**Responsibilities**:
- WebSocket lifecycle management
- Audio stream coordination
- Function call handling
- Cost tracking
- Transcript persistence

#### 3. ProgressiveAssessmentEngine

**Location**: `backend/app/services/progressive_assessment_engine.py`

**Purpose**: Adaptive difficulty adjustment algorithm.

**Key Methods**:
- `update_after_response()` - Adjust difficulty based on performance
- `analyze_response_quality()` - Score candidate answers
- `determine_next_skill_area()` - Choose next topic to explore
- `detect_skill_boundary()` - Identify performance limits

**Difficulty Levels**:
1. **warmup** - Easy intro questions (2 questions)
2. **fundamental** - Basic syntax and concepts
3. **intermediate** - Practical application
4. **advanced** - Architecture and optimization
5. **expert** - System design and performance

#### 4. ConversationMemoryManager

**Location**: `backend/app/services/conversation_memory.py`

**Purpose**: Prevent context window overflow while maintaining coherence.

**Strategy**:
- Keep last 12 messages
- Preserve first 2 (greeting + initial Q&A)
- Track truncation count
- Store important facts separately

### API Endpoints

#### Authentication Endpoints (`/api/v1/auth`)

```python
POST /api/v1/auth/register
Request:  { email, password, full_name }
Response: { token, candidate_id, email }
Status:   201 Created

POST /api/v1/auth/login
Request:  { email, password }
Response: { token, candidate_id, email }
Status:   200 OK

POST /api/v1/auth/logout
Headers:  Authorization: Bearer <token>
Response: { message: "Logged out successfully" }
Status:   200 OK

GET /api/v1/auth/me
Headers:  Authorization: Bearer <token>
Response: { id, email, full_name, created_at }
Status:   200 OK
```

#### Interview Endpoints (`/api/v1/interviews`)

```python
POST /api/v1/interviews/start
Headers:  Authorization: Bearer <token>
Request:  { role_type: "react" | "python" | "javascript" | "fullstack",
            resume_id: UUID | null }
Response: { 
  id: UUID,
  candidate_id: UUID,
  role_type: string,
  status: "in_progress",
  started_at: ISO8601,
  ...
}
Status:   201 Created

GET /api/v1/interviews/{interview_id}
Headers:  Authorization: Bearer <token>
Response: Interview object
Status:   200 OK

GET /api/v1/interviews/{interview_id}/messages
Headers:  Authorization: Bearer <token>
Query:    skip=0, limit=50
Response: {
  interview_id: UUID,
  total_count: int,
  messages: [
    { id, sequence_number, message_type, content_text, created_at, audio_url },
    ...
  ]
}
Status:   200 OK

POST /api/v1/interviews/{interview_id}/messages
Headers:  Authorization: Bearer <token>
          Content-Type: application/json (text mode)
          Content-Type: multipart/form-data (audio mode)
Request:  { message_text: string } OR FormData { audio_file: Blob }
Response: {
  message_id: UUID,
  transcript: string,
  ai_response: string,
  ai_audio_url: string | null,
  question_number: int,
  total_questions: int,
  session_state: { current_difficulty, skill_boundaries, ... }
}
Status:   200 OK

POST /api/v1/interviews/{interview_id}/complete
Headers:  Authorization: Bearer <token>
Response: {
  interview_id: UUID,
  completed_at: ISO8601,
  duration_seconds: int,
  questions_answered: int,
  skill_boundaries_identified: int,
  message: string
}
Status:   200 OK

GET /api/v1/interviews/{interview_id}/transcript
Headers:  Authorization: Bearer <token>
Response: {
  interview_id: UUID,
  started_at: ISO8601,
  completed_at: ISO8601 | null,
  duration_seconds: int | null,
  messages: [ { sequence_number, message_type, content_text, created_at }, ... ]
}
Status:   200 OK
```

#### Realtime Endpoints (`/api/v1/realtime`)

```python
WebSocket /api/v1/realtime/{session_id}
Headers:  Authorization: Bearer <token>
Protocol: Binary WebSocket messages (JSON + base64 audio)

Events from frontend to backend:
- session.create
- input_audio_buffer.append (candidate audio chunks)
- input_audio_buffer.commit
- response.cancel (interrupt AI)

Events from backend to frontend:
- session.created
- session.updated
- conversation.item.created (transcript)
- audio.delta (AI audio chunks)
- response.done
- error
```

#### Video Endpoints (`/api/v1/videos`)

```python
POST /api/v1/videos/{interview_id}/upload-chunk
Headers:  Authorization: Bearer <token>
          Content-Type: multipart/form-data
Request:  FormData {
            video_chunk: Blob,
            chunk_index: int,
            total_chunks: int,
            interview_id: UUID
          }
Response: {
  chunk_uploaded: true,
  chunk_index: int,
  total_uploaded: int
}
Status:   200 OK

POST /api/v1/videos/{interview_id}/finalize
Headers:  Authorization: Bearer <token>
Response: {
  video_recording_url: string,
  total_chunks: int,
  file_size_bytes: int
}
Status:   200 OK

GET /api/v1/videos/{interview_id}
Headers:  Authorization: Bearer <token>
Response: {
  id: UUID,
  interview_id: UUID,
  storage_path: string,
  file_size_bytes: int,
  duration_seconds: int | null,
  uploaded_at: ISO8601
}
Status:   200 OK
```

### Database Models

#### Interview

**Table**: `interviews`

**Columns**:
- `id` (UUID, PK) - Interview identifier
- `candidate_id` (UUID, FK → candidates.id) - Who is being interviewed
- `resume_id` (UUID, FK → resumes.id, nullable) - Resume context
- `role_type` (enum: react|python|javascript|fullstack) - Job role
- `status` (enum: scheduled|in_progress|completed|abandoned) - Current state
- `started_at` (timestamp, nullable) - When interview began
- `completed_at` (timestamp, nullable) - When interview finished
- `duration_seconds` (int, nullable) - Total duration
- `ai_model_used` (varchar, nullable) - e.g., "gpt-4o-mini"
- `total_tokens_used` (int, default 0) - Token count for cost
- `cost_usd` (decimal, default 0.0) - GPT cost
- `speech_tokens_used` (int, default 0) - TTS character count
- `speech_cost_usd` (decimal, default 0.0) - STT/TTS cost
- `realtime_cost_usd` (decimal, default 0.0) - Realtime API cost
- `tech_check_metadata` (jsonb, nullable) - Audio/video test results
- `video_recording_url` (varchar, nullable) - Supabase path
- `video_recording_consent` (boolean, default false) - GDPR consent
- `video_recording_status` (enum) - Recording lifecycle
- `created_at` (timestamp) - Record creation

**Relationships**:
- One-to-one with `InterviewSession`
- One-to-many with `InterviewMessage`
- Many-to-one with `Candidate`
- Many-to-one with `Resume` (optional)

#### InterviewSession

**Table**: `interview_sessions`

**Columns**:
- `id` (UUID, PK) - Session identifier
- `interview_id` (UUID, FK → interviews.id, unique) - Parent interview
- `current_difficulty_level` (varchar) - warmup|fundamental|intermediate|advanced|expert
- `questions_asked_count` (int, default 0) - Number of questions so far
- `skill_boundaries_identified` (jsonb) - Detected skill limits
  ```json
  {
    "React hooks": "intermediate",
    "State management": "advanced",
    "Performance": "fundamental"
  }
  ```
- `progression_state` (jsonb) - Assessment tracking
  ```json
  {
    "use_realtime": true,
    "phase_history": [
      { "phase": "warmup", "started_at": "...", "questions_count": 2 },
      { "phase": "fundamental", "started_at": "...", "questions_count": 3 }
    ],
    "response_quality_history": [
      { "question_num": 1, "quality": "good", "accuracy": 0.7 },
      { "question_num": 2, "quality": "excellent", "accuracy": 0.9 }
    ],
    "skills_explored": ["React basics", "useState", "useEffect"],
    "skills_pending": ["useContext", "useReducer", "custom hooks"],
    "boundary_detections": [
      { "skill": "React hooks", "boundary_level": "intermediate", "detected_at": "..." }
    ]
  }
  ```
- `conversation_memory` (jsonb) - Last N messages
  ```json
  {
    "messages": [
      { "role": "assistant", "content": "Hello! Let's begin..." },
      { "role": "user", "content": "I'm ready!" }
    ],
    "memory_metadata": {
      "created_at": "...",
      "last_updated": "...",
      "message_count": 12,
      "truncation_count": 2
    }
  }
  ```
- `last_activity_at` (timestamp) - For session timeout detection
- `created_at` (timestamp)
- `updated_at` (timestamp)

#### InterviewMessage

**Table**: `interview_messages`

**Columns**:
- `id` (UUID, PK) - Message identifier
- `interview_id` (UUID, FK → interviews.id) - Parent interview
- `sequence_number` (int) - Message order (1, 2, 3, ...)
- `message_type` (enum: ai_question|candidate_response) - Who sent it
- `content_text` (text) - Message content or transcript
- `audio_url` (varchar, nullable) - Link to audio file (TTS or recording)
- `metadata` (jsonb, nullable) - Extra data
  ```json
  {
    "realtime_mode": true,
    "audio_duration_seconds": 5.2,
    "transcript_confidence": 0.95,
    "function_call_result": { ... }
  }
  ```
- `created_at` (timestamp) - When message was sent

**Indexes**:
- `(interview_id, sequence_number)` - Efficient message ordering
- `interview_id` - Fetch all messages for interview

#### Candidate

**Table**: `candidates`

**Columns**:
- `id` (UUID, PK)
- `email` (varchar, unique) - Login email
- `hashed_password` (varchar) - bcrypt hash
- `full_name` (varchar)
- `created_at` (timestamp)
- `last_login_at` (timestamp, nullable)

#### VideoRecording

**Table**: `video_recordings`

**Columns**:
- `id` (UUID, PK)
- `interview_id` (UUID, FK → interviews.id, unique)
- `storage_path` (varchar) - Supabase path (e.g., "videos/{id}.webm")
- `file_size_bytes` (bigint)
- `duration_seconds` (int, nullable)
- `chunk_count` (int) - Number of chunks uploaded
- `uploaded_at` (timestamp)
- `created_at` (timestamp)

### Database Relationships Diagram

```
┌──────────────┐         ┌────────────────┐
│  candidates  │─────────│   interviews   │
│  (1)         │ 1:N     │                │
└──────────────┘         │                │
                         │  - candidate_id│
    ┌────────────────────│  - resume_id   │
    │                    │  - status      │
    │                    │  - costs       │
    │                    └────────────────┘
    │                             │ 1:1
    │                             ↓
    │                    ┌─────────────────────┐
    │                    │ interview_sessions  │
    │                    │  - difficulty_level │
    │                    │  - progression_state│
    │                    │  - memory           │
    │                    └─────────────────────┘
    │
    │                    ┌─────────────────────┐
    │            ┌───────│ interview_messages  │
    │            │ 1:N   │  - sequence_number  │
    │            │       │  - content_text     │
    │            │       │  - audio_url        │
    │            │       └─────────────────────┘
    │            │
    │            │       ┌─────────────────────┐
    │            └───────│  video_recordings   │
    │              1:1   │  - storage_path     │
    │                    │  - file_size        │
    │                    └─────────────────────┘
    │
    │   ┌──────────────┐
    └───│   resumes    │
  1:N   │              │
        └──────────────┘
```

---

## Frontend Architecture

### Component Hierarchy

```
App (app/layout.tsx)
├── Providers (React Query, Auth)
├── Login Page (app/login/page.tsx)
├── Register Page (app/register/page.tsx)
├── Dashboard (app/dashboard/page.tsx)
└── Interview Flow
    ├── Start Page (app/interview/start/page.tsx)
    ├── Tech Check (app/interview/[id]/tech-check/page.tsx)
    ├── Interview Page (app/interview/[id]/page.tsx) ⭐ MAIN
    │   ├── InterviewChat
    │   │   ├── ChatMessage (AI/Candidate)
    │   │   └── TypingIndicator
    │   ├── InterviewControls
    │   │   ├── PushToTalkButton
    │   │   ├── AudioLevelIndicator
    │   │   └── RealtimeStatusIndicator
    │   ├── VideoFeed (candidate self-view)
    │   └── InterviewProgress (question counter)
    └── Results Page (app/interview/[id]/results/page.tsx)
```

### State Management (Zustand)

#### AuthStore

**Location**: `frontend/src/features/auth/store/authStore.ts`

**State**:
```typescript
{
  user: User | null,
  token: string | null,
  isAuthenticated: boolean
}
```

**Actions**:
- `setUser(user)` - Set current user
- `setToken(token)` - Store JWT token (also saves to localStorage)
- `logout()` - Clear user and token
- `checkAuth()` - Validate token on app load

#### InterviewStore

**Location**: `frontend/src/features/interview/store/interviewStore.ts`

**State**:
```typescript
{
  // Session
  sessionId: string | null,
  status: "not_started" | "in_progress" | "completed",
  
  // Messages
  messages: Message[],
  currentQuestion: number,
  totalQuestions: number,
  isAiTyping: boolean,
  
  // Audio state
  isRecording: boolean,
  audioPermissionGranted: boolean,
  recordingError: string | null,
  
  // Interview state machine
  interviewState: "idle" | "ai_speaking" | "candidate_turn" | 
                  "candidate_speaking" | "processing",
  
  // Realtime mode
  useRealtimeMode: boolean,
  connectionState: "disconnected" | "connecting" | "connected" | "error",
  realtimeLatency: number | null,
  audioLevel: number,
  
  // Video
  cameraEnabled: boolean,
  selfViewVisible: boolean,
  
  // Captions
  currentCaption: string | null,
  captionsEnabled: boolean,
  showCaption: boolean,
  
  // Completion
  isCompleted: boolean,
  completionData: CompletionData | null
}
```

**Actions**:
- `setSessionId(id)` - Set current interview session
- `addMessage(message)` - Add to chat history
- `setMessages(messages)` - Bulk replace messages
- `clearMessages()` - Reset chat
- `setAiTyping(isTyping)` - Show/hide typing indicator
- `updateProgress(current, total)` - Update question counter
- `setStatus(status)` - Change interview status
- `setRecording(isRecording)` - Update recording state
- `setAudioPermission(granted)` - Store permission status
- `setInterviewState(state)` - Change interview state machine
- `toggleRealtimeMode()` - Switch between Realtime and Legacy
- `setConnectionState(state)` - Update WebSocket status
- `setAudioLevel(level)` - Update mic level (0-1)
- `setCameraEnabled(enabled)` - Toggle camera
- `setSelfViewVisible(visible)` - Show/hide self-view
- `setCurrentCaption(text)` - Update live captions
- `setCaptionsEnabled(enabled)` - Toggle captions
- `setCompleted()` - Mark interview complete
- `setCompletionData(data)` - Store results

### Custom Hooks

#### useRealtimeConnection

**Location**: `frontend/src/features/interview/hooks/useRealtimeConnection.ts`

**Purpose**: Manage WebSocket connection to Realtime API

**Returns**:
```typescript
{
  connectionState: ConnectionState,
  latency: number | null,
  connect: () => Promise<void>,
  disconnect: () => void,
  sendAudio: (audioData: ArrayBuffer) => void,
  error: Error | null
}
```

**Usage**:
```typescript
const { connect, disconnect, sendAudio, connectionState } = useRealtimeConnection(sessionId);

useEffect(() => {
  connect();
  return () => disconnect();
}, [sessionId]);
```

#### useAudioCapture

**Location**: `frontend/src/features/interview/hooks/useAudioCapture.ts`

**Purpose**: Capture audio from microphone

**Returns**:
```typescript
{
  startRecording: () => Promise<void>,
  stopRecording: () => Promise<Blob>,
  isRecording: boolean,
  audioLevel: number,
  permissionGranted: boolean,
  error: string | null,
  requestPermission: () => Promise<boolean>
}
```

**Usage**:
```typescript
const { startRecording, stopRecording, audioLevel, isRecording } = useAudioCapture();

const handlePushToTalk = async () => {
  if (isRecording) {
    const audioBlob = await stopRecording();
    // Send to backend
  } else {
    await startRecording();
  }
};
```

#### useVideoRecorder

**Location**: `frontend/src/features/video/hooks/useVideoRecorder.ts`

**Purpose**: Record candidate video during interview

**Returns**:
```typescript
{
  startRecording: () => Promise<void>,
  stopRecording: () => void,
  pauseRecording: () => void,
  resumeRecording: () => void,
  isRecording: boolean,
  isPaused: boolean,
  duration: number,
  chunks: Blob[],
  error: string | null
}
```

#### useInterview

**Location**: `frontend/src/features/interview/hooks/useInterview.ts`

**Purpose**: React Query hooks for interview API

**Hooks**:
```typescript
// Start new interview
const { mutate: startInterview, isPending } = useStartInterview();
startInterview({ role_type: "react", resume_id: null });

// Fetch interview messages
const { data: messages, isLoading } = useInterviewMessages(interviewId);

// Send text message
const { mutate: sendMessage } = useSendMessage(interviewId);
sendMessage("My answer here");
```

#### useSendMessage

**Location**: `frontend/src/features/interview/hooks/useSendMessage.ts`

**Purpose**: Send candidate message with optimistic updates

**Features**:
- Optimistic UI (message appears immediately)
- Automatic retry on failure
- Rollback on error
- Query invalidation on success

### API Client

**Location**: `frontend/src/services/api/client.ts`

**Features**:
- Automatic JWT token injection
- 401 handling (redirect to login)
- Retry logic (3 attempts with exponential backoff)
- Request/response interceptors
- Error normalization

**Usage**:
```typescript
import { apiClient } from '@/services/api/client';

// GET request
const data = await apiClient.get<Interview>('/interviews/123');

// POST request with body
const response = await apiClient.post<InterviewResponse>(
  '/interviews/start',
  { role_type: 'react' }
);

// Multipart/form-data
const formData = new FormData();
formData.append('audio_file', audioBlob);
const result = await apiClient.post('/interviews/123/messages', formData);
```

### Routing (Next.js App Router)

All routes are file-based in `frontend/app/`:

| Route | File | Purpose | Auth Required |
|-------|------|---------|---------------|
| `/` | `page.tsx` | Home/landing | No |
| `/login` | `login/page.tsx` | Login form | No |
| `/register` | `register/page.tsx` | Registration | No |
| `/dashboard` | `dashboard/page.tsx` | Candidate dashboard | Yes |
| `/interview/start` | `interview/start/page.tsx` | Interview start | Yes |
| `/interview/:id/tech-check` | `interview/[sessionId]/tech-check/page.tsx` | Mic/camera test | Yes |
| `/interview/:id` | `interview/[sessionId]/page.tsx` | Main interview | Yes |
| `/interview/:id/results` | `interview/[sessionId]/results/page.tsx` | Interview results | Yes |
| `/profile` | `profile/page.tsx` | User profile | Yes |
| `/settings` | `settings/page.tsx` | User settings | Yes |

**Protected Routes**: Implemented via middleware in `app/middleware.ts` - checks for valid JWT token.

---

## Development Guide

### Initial Setup

#### Prerequisites

1. **Python 3.11.9** (managed via pyenv)
2. **Node.js 24.6.0** or later
3. **PostgreSQL 15+**
4. **Supabase account** (for video storage)
5. **OpenAI API key**

#### Backend Setup

```bash
# 1. Install pyenv (if not already installed)
brew install pyenv  # macOS
# OR for Linux: curl https://pyenv.run | bash

# 2. Install Python 3.11.9
pyenv install 3.11.9
pyenv local 3.11.9

# 3. Navigate to backend directory
cd backend

# 4. Install UV package manager
pip install uv

# 5. Create virtual environment
uv venv

# 6. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 7. Install dependencies
uv pip install -e .

# 8. Install dev dependencies
uv pip install -e ".[dev]"

# 9. Create .env file
cp .env.example .env

# 10. Edit .env with your credentials
# Required variables:
# - DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
# - OPENAI_API_KEY
# - SUPABASE_URL, SUPABASE_KEY (for video storage)
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)

# 11. Run database migrations
alembic upgrade head

# 12. Start the server
uv run uvicorn main:app --reload

# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install pnpm (if not already installed)
npm install -g pnpm

# 3. Install dependencies
pnpm install

# 4. Create .env.local file
cp .env.example .env.local

# 5. Edit .env.local
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
# NEXT_PUBLIC_MOCK_API=false  # Use real backend

# 6. Start development server
pnpm dev

# Server will be available at http://localhost:3000
```

### Environment Variables

#### Backend (.env)

```bash
# Database (PostgreSQL)
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=teamified_candidates

# Test Database
TEST_DB_USER=postgres
TEST_DB_PASSWORD=your_password
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=teamified_candidates_test

# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# OpenAI Speech Services
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy
OPENAI_TTS_SPEED=1.0
OPENAI_STT_MODEL=whisper-1
OPENAI_STT_LANGUAGE=en

# OpenAI Realtime API
REALTIME_API_MODEL=gpt-4o-realtime-preview-2024-10-01
REALTIME_VOICE=alloy
REALTIME_TEMPERATURE=0.7
REALTIME_MAX_RESPONSE_TOKENS=1000

# Audio Constraints
AUDIO_MAX_FILE_SIZE_MB=25
AUDIO_MIN_SAMPLE_RATE_HZ=16000
AUDIO_SUPPORTED_FORMATS=webm,mp3,mp4,mpeg,mpga,m4a,wav

# Supabase (Video Storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=interview-videos

# Security
JWT_SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

#### Frontend (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# Mock API (for development without backend)
NEXT_PUBLIC_MOCK_API=false

# WebSocket URL (for Realtime API)
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000/api/v1
```

### Development Workflow

#### Starting the System

```bash
# Terminal 1: Start PostgreSQL
# (If using Postgres.app on macOS, just open the app)
# OR: brew services start postgresql@15

# Terminal 2: Start backend
cd backend
source .venv/bin/activate
uv run uvicorn main:app --reload

# Terminal 3: Start frontend
cd frontend
pnpm dev

# Terminal 4: (Optional) Watch logs
tail -f backend/logs/app.log
```

#### Making Code Changes

**Backend Changes**:
1. Edit Python files
2. Uvicorn will auto-reload (watch terminal for errors)
3. For model changes:
   ```bash
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

**Frontend Changes**:
1. Edit TypeScript/React files
2. Next.js will hot-reload automatically
3. Check browser console for errors

#### Running Tests

**Backend Tests**:
```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_interview_engine.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run integration tests (requires test database)
pytest tests/integration/

# Run E2E tests
pytest tests/e2e/
```

**Frontend Tests**:
```bash
cd frontend

# Run all tests
pnpm test

# Run in watch mode
pnpm test --watch

# Run with coverage
pnpm test:coverage

# Run UI mode (interactive)
pnpm test:ui
```

### Database Migrations

#### Creating a Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add video_recording_consent field"

# Manually create empty migration
alembic revision -m "Custom migration"

# Edit the generated file in alembic/versions/
# Then apply:
alembic upgrade head
```

#### Common Migration Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show current revision
alembic current

# Show migration history
alembic history

# Show SQL without applying
alembic upgrade head --sql
```

### Debugging Tips

#### Backend Debugging

**Enable Debug Logging**:
```python
# main.py
import structlog

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(10),  # DEBUG level
)
```

**Use pdb for Breakpoints**:
```python
def some_function():
    import pdb; pdb.set_trace()  # Debugger stops here
    # ... rest of code
```

**Check Database State**:
```bash
# Connect to PostgreSQL
psql -U postgres -d teamified_candidates

# List tables
\dt

# Query interviews
SELECT id, status, started_at, role_type FROM interviews;

# Query sessions
SELECT id, current_difficulty_level, questions_asked_count 
FROM interview_sessions;

# Check messages
SELECT interview_id, sequence_number, message_type, 
       LEFT(content_text, 50) as content
FROM interview_messages
ORDER BY interview_id, sequence_number;
```

**Monitor API Requests**:
```bash
# Watch structured logs
tail -f backend/logs/app.log | jq .

# Filter by event
tail -f backend/logs/app.log | jq 'select(.event == "interview_started")'

# Filter by interview_id
tail -f backend/logs/app.log | jq 'select(.interview_id == "YOUR_UUID")'
```

#### Frontend Debugging

**React DevTools**:
1. Install React DevTools extension
2. Open browser DevTools → Components tab
3. Inspect component state and props

**Zustand DevTools**:
```typescript
// Already enabled in dev mode
// Open Redux DevTools extension to see store changes
```

**Network Debugging**:
1. Open browser DevTools → Network tab
2. Filter by "Fetch/XHR" to see API calls
3. Check request/response payloads
4. Look for failed requests (red status codes)

**WebSocket Debugging**:
1. Open browser DevTools → Network tab → WS filter
2. Click on WebSocket connection
3. View Messages tab to see bidirectional traffic
4. Check for connection drops or errors

**Console Logging**:
```typescript
// Add temporary debug logs
console.log('[DEBUG] Interview state:', interviewState);
console.log('[DEBUG] Audio level:', audioLevel);

// Use groups for better organization
console.group('WebSocket Event');
console.log('Type:', event.type);
console.log('Data:', event.data);
console.groupEnd();
```

### Code Style Guidelines

#### Backend (Python)

Follow PEP 8 and the project's coding standards (see `docs/architecture/coding-standards.md`).

**Key Points**:
- Use type hints for all function parameters and return values
- Docstrings for all public classes and methods (Google style)
- Snake_case for variables and functions
- PascalCase for classes
- UPPER_SNAKE_CASE for constants

**Example**:
```python
from uuid import UUID
from typing import Optional

class InterviewEngine:
    """Main interview orchestration service."""
    
    async def start_interview(
        self,
        candidate_id: UUID,
        role_type: str,
        resume_id: Optional[UUID] = None
    ) -> InterviewSession:
        """
        Start a new interview session.
        
        Args:
            candidate_id: UUID of the candidate
            role_type: Type of role (react, python, etc.)
            resume_id: Optional resume for context
        
        Returns:
            Newly created InterviewSession
        
        Raises:
            CandidateNotFoundException: If candidate not found
        """
        # Implementation here
        pass
```

#### Frontend (TypeScript/React)

Follow the project's TypeScript and React conventions.

**Key Points**:
- Use TypeScript for all files (.ts, .tsx)
- camelCase for variables and functions
- PascalCase for components, types, and interfaces
- Use functional components with hooks (no class components)
- Prefer const over let, never use var
- Use template literals for strings with variables

**Example**:
```typescript
import { useEffect, useState } from 'react';

interface InterviewPageProps {
  sessionId: string;
}

export function InterviewPage({ sessionId }: InterviewPageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const { data, error } = useInterviewMessages(sessionId);
  
  useEffect(() => {
    if (data || error) {
      setIsLoading(false);
    }
  }, [data, error]);
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  return (
    <div className="interview-container">
      {/* Component JSX */}
    </div>
  );
}
```

---

## Testing Strategy

### Backend Testing

#### Unit Tests

**Location**: `backend/tests/unit/`

**Purpose**: Test individual functions and classes in isolation.

**Example**:
```python
# tests/unit/test_progressive_assessment_engine.py
import pytest
from app.services.progressive_assessment_engine import ProgressiveAssessmentEngine

@pytest.fixture
def engine():
    return ProgressiveAssessmentEngine(ai_provider=mock_provider)

def test_update_after_excellent_response(engine):
    """Should increase difficulty after excellent response."""
    session = create_mock_session(difficulty="fundamental")
    
    adjustment = engine.update_after_response(
        session=session,
        answer_quality="excellent",
        technical_accuracy=0.9,
        explanation_clarity=0.85
    )
    
    assert adjustment.new_level == "intermediate"
    assert adjustment.reason == "Consistently strong performance"

def test_detect_skill_boundary(engine):
    """Should mark boundary after 2 poor responses."""
    session = create_mock_session(
        difficulty="intermediate",
        recent_scores=[0.4, 0.45]
    )
    
    adjustment = engine.update_after_response(
        session=session,
        answer_quality="poor",
        technical_accuracy=0.4,
        explanation_clarity=0.5
    )
    
    assert adjustment.new_level == "fundamental"
    assert "boundary" in adjustment.reason.lower()
```

#### Integration Tests

**Location**: `backend/tests/integration/`

**Purpose**: Test API endpoints with real database (test database).

**Example**:
```python
# tests/integration/test_interview_api.py
import pytest
from fastapi.testclient import TestClient

def test_start_interview(client: TestClient, auth_token: str):
    """Test starting a new interview."""
    response = client.post(
        "/api/v1/interviews/start",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"role_type": "react", "resume_id": null}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["role_type"] == "react"
    assert "id" in data

def test_send_message(client: TestClient, interview_id: str, auth_token: str):
    """Test sending a candidate message."""
    response = client.post(
        f"/api/v1/interviews/{interview_id}/messages",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message_text": "I use useState for state management"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "ai_response" in data
    assert "question_number" in data
```

#### E2E Tests

**Location**: `backend/tests/e2e/`

**Purpose**: Test complete user flows from start to finish.

**Example**:
```python
# tests/e2e/test_interview_flow.py
@pytest.mark.e2e
def test_complete_interview_flow(client: TestClient):
    """Test full interview from registration to completion."""
    # 1. Register candidate
    register_response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    })
    token = register_response.json()["token"]
    
    # 2. Start interview
    interview_response = client.post(
        "/api/v1/interviews/start",
        headers={"Authorization": f"Bearer {token}"},
        json={"role_type": "react"}
    )
    interview_id = interview_response.json()["id"]
    
    # 3. Answer 5 questions
    for i in range(5):
        client.post(
            f"/api/v1/interviews/{interview_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={"message_text": f"My answer to question {i+1}"}
        )
    
    # 4. Complete interview
    complete_response = client.post(
        f"/api/v1/interviews/{interview_id}/complete",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["questions_answered"] >= 5
```

### Frontend Testing

#### Component Tests

**Location**: `frontend/src/**/*.test.tsx`

**Purpose**: Test React components in isolation.

**Example**:
```typescript
// src/features/interview/components/PushToTalkButton.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PushToTalkButton } from './PushToTalkButton';

describe('PushToTalkButton', () => {
  it('should start recording on mouse down', async () => {
    const mockStartRecording = vi.fn();
    
    render(
      <PushToTalkButton
        onStartRecording={mockStartRecording}
        onStopRecording={vi.fn()}
        isRecording={false}
      />
    );
    
    const button = screen.getByRole('button');
    fireEvent.mouseDown(button);
    
    expect(mockStartRecording).toHaveBeenCalled();
  });
  
  it('should show recording state', () => {
    render(
      <PushToTalkButton
        onStartRecording={vi.fn()}
        onStopRecording={vi.fn()}
        isRecording={true}
      />
    );
    
    expect(screen.getByText(/recording/i)).toBeInTheDocument();
  });
});
```

#### Hook Tests

**Location**: `frontend/src/**/*.test.ts`

**Purpose**: Test custom React hooks.

**Example**:
```typescript
// src/features/interview/hooks/useInterview.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useStartInterview } from './useInterview';

describe('useStartInterview', () => {
  it('should call API and navigate on success', async () => {
    const mockNavigate = vi.fn();
    vi.mock('next/navigation', () => ({
      useRouter: () => ({ push: mockNavigate })
    }));
    
    const { result } = renderHook(() => useStartInterview());
    
    result.current.mutate({ role_type: 'react', resume_id: null });
    
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    
    expect(mockNavigate).toHaveBeenCalledWith(
      expect.stringContaining('/interview/')
    );
  });
});
```

---

## Known Issues & Technical Debt

### Current Known Issues

#### 1. WebSocket Reconnection (Realtime Mode)

**Issue**: WebSocket connection drops after 5 minutes of inactivity.

**Workaround**: Frontend automatically attempts to reconnect (3 retries with exponential backoff).

**Fix Needed**: Implement keep-alive pings every 30 seconds.

**Location**: `frontend/src/features/interview/hooks/useRealtimeConnection.ts`

**Priority**: Medium

#### 2. Audio Echo in Safari

**Issue**: Some users report hearing their own voice (echo) in Safari browser.

**Workaround**: Use Chrome or Firefox for now. Safari users should use headphones.

**Fix Needed**: Implement echo cancellation using Web Audio API.

**Location**: `frontend/src/features/interview/hooks/useAudioCapture.ts`

**Priority**: High

#### 3. Large Video Upload Failures

**Issue**: Video uploads >100MB sometimes fail with timeout.

**Workaround**: Chunk size reduced to 5MB, but timeout still occurs on slow connections.

**Fix Needed**: Implement resumable uploads with retry logic.

**Location**: `frontend/src/features/video/hooks/useVideoRecorder.ts`

**Priority**: Medium

#### 4. Memory Leak in Long Interviews

**Issue**: Browser memory usage grows continuously during interviews >30 minutes.

**Workaround**: Clear old audio buffers every 10 minutes.

**Fix Needed**: Properly dispose of AudioContext nodes and release memory.

**Location**: `frontend/app/interview/[sessionId]/page.tsx`

**Priority**: High

#### 5. Race Condition in Assessment State

**Issue**: Occasionally, difficulty level doesn't update correctly when two responses come in quickly.

**Workaround**: Backend uses database locks, but race still possible.

**Fix Needed**: Implement proper transaction isolation or use Redis for state.

**Location**: `backend/app/services/progressive_assessment_engine.py`

**Priority**: Low

### Technical Debt

#### 1. Legacy STT/TTS Mode Needs Refactoring

**Description**: The fallback STT/TTS mode has duplicated logic with Realtime mode.

**Impact**: Code is harder to maintain, tests are fragmented.

**Effort**: 2-3 days

**Recommendation**: Extract common interview logic into shared service.

#### 2. No Comprehensive E2E Tests

**Description**: Only basic E2E tests exist. Need full user journey tests.

**Impact**: Regressions slip through to production.

**Effort**: 1 week

**Recommendation**: Add Playwright/Cypress tests for critical flows.

#### 3. Video Cleanup Service is Manual

**Description**: Old videos must be manually deleted from Supabase.

**Impact**: Storage costs increase over time.

**Effort**: 2 days

**Recommendation**: Implement automated cleanup job (cron task).

**Location**: `backend/app/services/video_cleanup_service.py`

#### 4. No Rate Limiting

**Description**: API endpoints have no rate limiting.

**Impact**: Vulnerable to abuse, high OpenAI costs.

**Effort**: 1 day

**Recommendation**: Add rate limiting middleware (e.g., slowapi).

#### 5. Frontend State Management Complexity

**Description**: InterviewStore has grown too large (15+ state variables).

**Impact**: Hard to reason about state changes, testing is complex.

**Effort**: 3-4 days

**Recommendation**: Split into smaller, focused stores (audioStore, videoStore, etc.).

---

## Quick Reference for Common Tasks

### For Bug Fixes

#### "Interview doesn't start"

1. **Check backend logs**:
   ```bash
   tail -f backend/logs/app.log | jq 'select(.event == "interview_started")'
   ```

2. **Verify database connection**:
   ```bash
   psql -U postgres -d teamified_candidates -c "SELECT 1"
   ```

3. **Check authentication**:
   ```bash
   # In browser console
   localStorage.getItem('auth_token')
   ```

4. **Common causes**:
   - JWT token expired (401 error)
   - Database migration not applied
   - OpenAI API key invalid
   - CORS misconfiguration

#### "Audio not working"

1. **Check microphone permission**:
   ```javascript
   // In browser console
   navigator.permissions.query({ name: 'microphone' })
   ```

2. **Test audio capture**:
   ```javascript
   // In browser console
   navigator.mediaDevices.getUserMedia({ audio: true })
     .then(stream => console.log('✅ Mic works'))
     .catch(err => console.error('❌ Mic error:', err))
   ```

3. **Check WebSocket connection**:
   ```javascript
   // In browser DevTools → Network → WS
   // Should see connection to ws://localhost:8000/api/v1/realtime/:id
   ```

4. **Common causes**:
   - Microphone permission denied
   - Browser doesn't support Web Audio API
   - WebSocket connection failed
   - Audio format not supported

#### "AI responses are slow"

1. **Check OpenAI API status**: https://status.openai.com

2. **Monitor API latency**:
   ```bash
   # Backend logs show timing
   tail -f backend/logs/app.log | jq 'select(.event == "openai_completion")'
   ```

3. **Check database query performance**:
   ```sql
   -- Enable query logging
   ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries >1s
   SELECT pg_reload_conf();
   
   -- View slow queries
   SELECT query, mean_exec_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC LIMIT 10;
   ```

4. **Common causes**:
   - OpenAI API rate limit hit
   - Database queries not optimized
   - Conversation context too large
   - Network latency

### For Adding Features

#### "Add a new question type"

1. **Update progressive assessment engine**:
   ```python
   # backend/app/services/progressive_assessment_engine.py
   
   SKILL_AREAS = {
       "react": [
           "hooks",
           "state_management",
           "performance",
           "new_skill_area"  # Add here
       ]
   }
   ```

2. **Add prompts for new skill**:
   ```python
   # backend/app/prompts/interview_prompts.py
   
   SKILL_PROMPTS = {
       "new_skill_area": {
           "warmup": "Easy question about...",
           "fundamental": "Basic question about...",
           "intermediate": "Practical question about...",
       }
   }
   ```

3. **Test the new questions**:
   ```bash
   pytest tests/unit/test_progressive_assessment_engine.py -k new_skill
   ```

#### "Add a new API endpoint"

1. **Define Pydantic schema**:
   ```python
   # backend/app/schemas/my_feature.py
   
   from pydantic import BaseModel
   
   class MyFeatureRequest(BaseModel):
       field1: str
       field2: int
   
   class MyFeatureResponse(BaseModel):
       result: str
       status: str
   ```

2. **Add route handler**:
   ```python
   # backend/app/api/v1/my_feature.py
   
   from fastapi import APIRouter, Depends
   from app.schemas.my_feature import MyFeatureRequest, MyFeatureResponse
   
   router = APIRouter(prefix="/my-feature", tags=["my-feature"])
   
   @router.post("/", response_model=MyFeatureResponse)
   async def my_feature_endpoint(
       request: MyFeatureRequest,
       user=Depends(get_current_user)
   ):
       # Implementation
       return MyFeatureResponse(result="success", status="ok")
   ```

3. **Register router**:
   ```python
   # backend/main.py
   
   from app.api.v1 import my_feature
   
   app.include_router(my_feature.router, prefix="/api/v1")
   ```

4. **Add frontend service**:
   ```typescript
   // frontend/src/services/api/myFeatureService.ts
   
   import { apiClient } from './client';
   
   export const myFeatureAPI = {
       async doSomething(data: MyFeatureRequest): Promise<MyFeatureResponse> {
           return apiClient.post('/my-feature', data);
       }
   };
   ```

5. **Create React Query hook**:
   ```typescript
   // frontend/src/hooks/useMyFeature.ts
   
   import { useMutation } from '@tanstack/react-query';
   import { myFeatureAPI } from '@/services/api/myFeatureService';
   
   export function useMyFeature() {
       return useMutation({
           mutationFn: myFeatureAPI.doSomething,
           onSuccess: (data) => {
               console.log('Success:', data);
           }
       });
   }
   ```

#### "Add a new UI component"

1. **Create component file**:
   ```typescript
   // frontend/src/components/ui/MyComponent.tsx
   
   interface MyComponentProps {
       title: string;
       onClick: () => void;
   }
   
   export function MyComponent({ title, onClick }: MyComponentProps) {
       return (
           <button onClick={onClick} className="btn-primary">
               {title}
           </button>
       );
   }
   ```

2. **Add Storybook story** (if using Storybook):
   ```typescript
   // frontend/src/components/ui/MyComponent.stories.tsx
   
   import type { Meta, StoryObj } from '@storybook/react';
   import { MyComponent } from './MyComponent';
   
   const meta: Meta<typeof MyComponent> = {
       title: 'UI/MyComponent',
       component: MyComponent,
   };
   
   export default meta;
   
   export const Default: StoryObj<typeof MyComponent> = {
       args: {
           title: 'Click Me',
           onClick: () => alert('Clicked!'),
       },
   };
   ```

3. **Add tests**:
   ```typescript
   // frontend/src/components/ui/MyComponent.test.tsx
   
   import { render, screen, fireEvent } from '@testing-library/react';
   import { MyComponent } from './MyComponent';
   
   describe('MyComponent', () => {
       it('should call onClick when clicked', () => {
           const handleClick = vi.fn();
           render(<MyComponent title="Test" onClick={handleClick} />);
           
           fireEvent.click(screen.getByRole('button'));
           expect(handleClick).toHaveBeenCalled();
       });
   });
   ```

### For Refactoring

#### "Extract common logic"

Before:
```python
# Duplicated in multiple files
def process_audio(file):
    if file.size > 25_000_000:
        raise ValueError("File too large")
    if not file.content_type.startswith('audio/'):
        raise ValueError("Invalid audio format")
    # ... more validation
```

After:
```python
# backend/app/utils/audio.py

class AudioValidator:
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
    
    @staticmethod
    def validate_audio_file(file) -> None:
        """
        Validate audio file meets requirements.
        
        Raises:
            ValueError: If file is invalid
        """
        if file.size > AudioValidator.MAX_FILE_SIZE:
            raise ValueError(f"File exceeds {AudioValidator.MAX_FILE_SIZE} bytes")
        
        if not file.content_type.startswith('audio/'):
            raise ValueError(f"Invalid content type: {file.content_type}")
        
        # Additional validation...

# Usage in multiple files:
from app.utils.audio import AudioValidator

AudioValidator.validate_audio_file(uploaded_file)
```

#### "Split large component"

Before:
```typescript
// 500+ lines component with multiple responsibilities
export function InterviewPage() {
    // Audio logic
    // Video logic
    // Chat logic
    // Progress logic
    // All in one component
}
```

After:
```typescript
// interview/InterviewPage.tsx (orchestrator)
export function InterviewPage() {
    return (
        <div className="interview-layout">
            <InterviewHeader />
            <InterviewChat />
            <InterviewControls />
            <InterviewProgress />
        </div>
    );
}

// interview/components/InterviewChat.tsx
export function InterviewChat() {
    // Only chat-related logic
}

// interview/components/InterviewControls.tsx
export function InterviewControls() {
    // Only control-related logic (mic, camera)
}
```

### For Deployment

#### "Deploy backend to production"

```bash
# 1. Set environment variables
export DB_HOST=production-db-host
export DB_PASSWORD=secure-password
export OPENAI_API_KEY=sk-production-key

# 2. Run database migrations
alembic upgrade head

# 3. Start with production server
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

#### "Deploy frontend to Vercel"

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Login
vercel login

# 3. Deploy
cd frontend
vercel --prod

# 4. Set environment variables in Vercel dashboard
# NEXT_PUBLIC_API_BASE_URL=https://api.teamified.com/api/v1
# NEXT_PUBLIC_MOCK_API=false
```

---

## Conclusion

This document provides a comprehensive view of the **current actual state** of the Teamified Candidates Portal system. It focuses on:

- ✅ **Reality over aspiration** - Documents what exists, not what's planned
- ✅ **Complete AI interview flow** - Deep dive into the most complex part
- ✅ **Practical guidance** - Real commands, real code examples
- ✅ **Bug fixing and features** - Quick reference for common tasks
- ✅ **Mixed audience** - Accessible to both junior and senior engineers

### Key Takeaways

1. **Two Interview Modes**: Realtime (primary) and Legacy (fallback)
2. **Progressive Assessment**: Adaptive difficulty based on performance
3. **Comprehensive Cost Tracking**: Monitors OpenAI usage in real-time
4. **Full-Stack TypeScript/Python**: Modern tech stack with type safety
5. **Production-Ready**: Deployed and working, with known issues documented

### Getting Help

- **Documentation**: Check `docs/architecture/` for detailed architecture docs
- **Code Examples**: See `docs/stories/` for implementation examples
- **PRD**: See `docs/prds/` for product requirements
- **Epics**: See `docs/epics/` for feature breakdowns

### Next Steps for New Contributors

1. Read this document completely
2. Set up local development environment
3. Run the test suites to ensure everything works
4. Pick a story from `docs/stories/` to implement
5. Follow the coding standards in `docs/architecture/coding-standards.md`
6. Write tests for your changes
7. Submit a pull request

---

**Document Version**: 2.0  
**Last Updated**: November 4, 2025  
**Maintained By**: Development Team  
**License**: Proprietary
