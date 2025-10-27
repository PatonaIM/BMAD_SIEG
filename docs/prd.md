# Teamified Candidates Portal Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Deliver an AI-driven candidate assessment platform that enables recruitment firms to conduct consistent, scalable technical interviews
- Reduce assessment time per candidate by 40-50% while maintaining or improving quality standards
- Achieve 90%+ interview completion rates with reliable scoring and integrity protection
- Enable pilot implementations for 3-5 early adopter recruitment firms within 10-11 months
- Provide seamless integration with existing ATS/HRIS systems through core APIs
- Build foundation for multi-modal deployment (autonomous AI, AI-assisted human, hybrid development modes)

### Background Context

Technical recruitment faces a critical challenge: consistent, accurate skill assessment at scale. Traditional methods either lack depth (automated screening) or consistency (human interviews), creating particular pain points for recruitment firms processing high volumes while maintaining quality standards. When clients demand "plug-and-play" candidates ready for immediate contribution, assessment reliability becomes paramount.

Teamified Candidates Portal addresses this through an intelligent AI-driven platform featuring progressive assessment methodology (confidence-building to boundary-exploration), multi-signal cheating detection, and adaptive question flows. The MVP delivers speech-to-speech AI interviews where candidates speak naturally with an AI interviewer, with optional text fallback for technical code examples. This speech-first approach for technical roles (React, Python, JavaScript) creates a more natural interview experience while enabling advanced behavioral analysis through voice patterns.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-27 | 1.0 | Initial PRD creation from Project Brief | PM Agent |

## Requirements

### Functional Requirements

**FR1:** The system shall conduct speech-to-speech conversational AI interviews for technical roles including React, Python, JavaScript, and general software development, with optional text input for code examples.

**FR2:** The system shall implement progressive assessment methodology starting with confidence-building questions before systematically increasing difficulty to map skill boundaries.

**FR3:** The system shall accept resume uploads and parse them in batch mode to extract skills, technologies, and experience for interview customization.

**FR4:** The system shall generate adaptive question flows based on candidate responses, previous answers, and extracted resume data in real-time during interviews.

**FR5:** The system shall provide real-time scoring showing technical competency levels, confidence ratings, and skill boundary identification during interviews.

**FR6:** The system shall implement AI-powered response timing analysis to detect patterns indicating rehearsed or copied answers.

**FR7:** The system shall use AI to recognize patterns in responses that suggest gaming attempts or lack of genuine understanding.

**FR8:** The system shall generate comprehensive candidate reports including competency scores, skill maps, interview transcripts, and integrity indicators.

**FR9:** The system shall provide candidate-facing interface with microphone controls, real-time audio visualization, optional text input for code examples, and progress indicators during AI-driven interviews.

**FR10:** The system shall maintain interview session state to allow the AI assessment engine to build context across the entire conversation.

**FR11:** The system shall use AI to generate skill boundary maps showing candidate proficiency levels across different technical domains.

**FR12:** The system shall support multiple concurrent AI interview sessions without performance degradation.

**FR13:** The system shall provide RESTful APIs for integration with external ATS/HRIS systems to receive candidate data and return assessment results.

**FR14:** The system shall log all candidate interactions, AI-generated questions, responses, and scoring decisions for quality improvement and model refinement.

**FR15:** The system shall notify candidates via email about resume processing completion and provide feedback on areas for improvement before interview scheduling.

**FR16:** The system shall capture and process candidate speech input using speech-to-text technology for AI analysis.

**FR17:** The system shall generate AI voice responses using text-to-speech technology for natural conversational flow.

**FR18:** The system shall support hybrid input mode where candidates can speak answers but type code examples or technical snippets when needed.

**FR19:** The system shall provide visual feedback during speech capture (voice level indicators, speaking/listening states).

**FR20:** The system shall handle speech-specific integrity indicators including speech pattern analysis, hesitation detection, and vocal confidence assessment.

### Non-Functional Requirements

**NFR1:** The system shall maintain 99% uptime during standard business hours across Australia (AEST/AEDT), Philippines (PHT), and India (IST) time zones.

**NFR2:** AI response generation times shall be less than 2 seconds for 95% of interactions to maintain natural conversational flow.

**NFR3:** The system shall support at least 50 concurrent AI interview sessions without performance degradation.

**NFR4:** All candidate data shall be encrypted in transit (TLS 1.3+) and at rest (AES-256).

**NFR5:** The system shall comply with GDPR data handling requirements including right to erasure and data portability.

**NFR6:** OpenAI API costs shall be monitored and optimized to maintain sustainable unit economics for pilot pricing.

**NFR7:** The system architecture shall be designed with clear API boundaries to support future microservices migration.

**NFR8:** Frontend shall be responsive and functional on desktop and tablet devices with modern browsers (Chrome, Firefox, Safari, Edge).

**NFR9:** All API endpoints shall include proper error handling and return meaningful error messages.

**NFR10:** The system shall implement rate limiting on APIs to prevent abuse and manage costs (10 interview starts per hour per IP address, adjustable based on usage patterns).

**NFR11:** Backend services shall implement structured logging for AI decision tracking, debugging, and performance monitoring.

**NFR12:** The platform shall be designed to handle 500+ interviews per month with linear scaling characteristics.

**NFR13:** AI model responses shall be validated for relevance and appropriateness before presentation to candidates.

**NFR14:** The system shall maintain detailed audit logs of all AI interactions and scoring decisions for model improvement and compliance.

**NFR15:** Resume parsing batch jobs shall complete within 24 hours of submission with 95% success rate.

**NFR16:** Speech-to-text processing latency shall be less than 1 second for 95% of audio segments to maintain conversational flow.

**NFR17:** Text-to-speech response generation shall complete within 1 second to maintain natural interview pacing.

**NFR18:** The system shall support WebRTC for real-time audio streaming with sub-200ms latency.

**NFR19:** Audio quality shall support 16kHz sample rate minimum for accurate speech recognition.

**NFR20:** The system shall gracefully degrade to text-only mode if microphone access is denied or audio processing fails.

## User Interface Design Goals

### Overall UX Vision

The platform delivers a professional, distraction-free interview experience that reduces candidate anxiety while maintaining assessment integrity. The candidate interface emphasizes clarity and conversational flow, mimicking natural chat interactions with progress indicators only - no scoring visible during the interview. For recruitment firms, the portal provides comprehensive candidate insights through data-rich dashboards with detailed AI reasoning, specific integrity red flags, and intuitive filtering and comparison tools.

The design prioritizes trust-building through transparency - candidates understand the assessment process and their progress, while recruiters gain confidence through detailed scoring breakdowns, AI decision reasoning, and specific integrity violation indicators.

### Key Interaction Paradigms

**Conversational Interview Flow**: Chat-like interface with typing indicators, smooth message transitions, and clear turn-taking between AI and candidate. Progressive disclosure of complexity keeps candidates engaged without overwhelming them.

**Progress-Only Feedback for Candidates**: Candidates see interview completion progress (e.g., "Question 8 of ~15-20") and encouraging affirmations, but no scores or competency indicators until interview completion. This maintains focus and reduces anxiety.

**Detailed AI Reasoning for Recruiters**: Real-time monitoring dashboard (future consideration) and post-interview reports show not just scores, but AI's reasoning - "Why did the AI rate this response as junior level?", "What patterns triggered integrity concerns?", "How did the AI determine skill boundaries?"

**Granular Integrity Indicators**: Instead of simple pass/fail, show specific red flags with severity levels: "Response timing anomaly - answered complex algorithm question in 15 seconds", "Pattern match - 85% similarity to common online solution", "Inconsistency detected - contradicts earlier stated experience with React hooks"

**Skill Boundary Visualization**: Interactive skill maps and competency charts use color-coding and radar graphs to quickly communicate proficiency levels across technical domains, with drill-down capability to see specific question/answer pairs that determined each rating.

**Batch Processing with Approval Workflow**: Resume upload provides clear status updates and estimated processing time. Automated feedback generation with recruiter approval option before sending - recruiter can review, edit, and approve or auto-send after X hours.

### Core Screens and Views

**Candidate Resume Upload Screen**: Simple drag-and-drop interface with format validation (PDF/DOCX), upload progress indicator, and confirmation message with expected processing timeline (within 24 hours).

**Candidate Interview Screen**: Full-screen interview interface with AI voice questions (with text transcript displayed), microphone controls (push-to-talk or voice-activated), real-time audio visualization showing candidate speaking, optional text input area for code examples, progress indicator showing approximate completion (e.g., "~60% complete"), and visual states (AI speaking, AI listening, candidate speaking). No scoring or competency indicators visible during interview.

**Candidate Results Screen**: Post-interview summary displaying overall competency score, skill boundary map visualization, strengths/areas for improvement breakdown, specific recommendations, and next steps. This is the first time candidates see any scoring information.

**Recruiter Dashboard**: Multi-candidate overview with sortable/filterable table showing key metrics (completion status, overall scores, integrity risk levels - color coded: green/yellow/red), quick actions (view details, export report, approve resume feedback), and search functionality.

**Recruiter Candidate Detail View**: Comprehensive single-candidate report including:
- **Interview Transcript**: Full conversation with AI questions and candidate responses
- **AI Scoring Reasoning**: For each major assessment area, show the AI's reasoning (e.g., "Rated React proficiency as 'Intermediate' because: demonstrated understanding of hooks and state management, but struggled with performance optimization concepts")
- **Detailed Integrity Analysis**: Specific red flags with severity and evidence:
  - Response timing anomalies with specific examples
  - Pattern matching results with similarity percentages
  - Inconsistency detection with contradicting statements highlighted
  - Behavioral indicators the AI detected
- **Skill Boundary Visualization**: Interactive charts showing proficiency across domains with drill-down to supporting evidence
- **Recommended Actions**: AI-generated suggestions for recruiter (e.g., "Schedule follow-up on React performance topics", "High integrity risk - recommend supervised technical assessment")

**Recruiter Resume Feedback Approval Screen**: Shows auto-generated feedback email with:
- Parsed skills summary
- Identified technical areas and gaps
- Specific improvement suggestions
- Call-to-action to schedule interview
- Recruiter options: "Send Now", "Edit & Send", "Auto-send in 4 hours if not reviewed"

**Resume Feedback Email**: Email template providing parsed skills summary, identified technical areas, specific suggestions for improvement, and call-to-action to schedule interview when ready.

### Accessibility

**WCAG AA Compliance**: Keyboard navigation support, proper ARIA labels, sufficient color contrast ratios (4.5:1 minimum for text), and screen reader compatibility for all interactive elements.

### Branding

**Professional Technical Aesthetic**: Clean, modern interface with emphasis on data visualization and information hierarchy. Color palette uses trust-building blues and greens with severity-coded integrity warnings (green=passed, yellow=minor concerns, red=significant red flags). Typography prioritizes readability with clear font hierarchy distinguishing AI questions, candidate responses, AI reasoning explanations, and system messages.

The design should feel more like a professional technical assessment tool than a casual chat app - balancing approachability with credibility. Emphasis on transparency and explainability of AI decisions.

### Target Device and Platforms

**Web Responsive (Desktop Primary, Tablet Secondary)**: Optimized for desktop browsers (Chrome, Firefox, Safari, Edge) with 1920x1080 and 1366x768 viewport support. Tablet support (iPad landscape) for recruiter review workflows. Mobile devices out of scope for MVP - interviews require focused desktop/laptop environment.

## Technical Assumptions

### Repository Structure

**Monorepo**: Single repository containing frontend and backend modules for streamlined development, simplified dependency management, and easier coordination for a small team (2-4 developers). Enables atomic commits across full-stack features and reduces context switching.

### Service Architecture

**Monolithic with Microservices-Ready Design**: Initial deployment as a monolithic application with clear internal module boundaries and API contracts. This approach:
- Simplifies initial development and deployment for MVP
- Reduces operational complexity for bootstrap/self-funded phase
- Maintains clear separation of concerns (AI Engine, Assessment Service, Resume Parser, API Gateway)
- Enables future migration to microservices when scale demands it (post-pilot phase)

Key architectural boundaries identified for future extraction:
- **AI Interview Engine**: Handles conversational AI, adaptive questioning, and real-time scoring
- **Resume Parser Service**: Batch processing for resume analysis and skill extraction
- **Assessment Scoring Service**: Integrity analysis, skill boundary mapping, and report generation
- **Integration API Gateway**: External ATS/HRIS connectivity and webhook management

### Testing Requirements

**Unit + Integration Testing with AI-Specific Strategies**: 
- **Unit Tests**: Core business logic, utility functions, data transformations (target 80%+ coverage)
- **Integration Tests**: API endpoints, database operations, external service mocking (OpenAI API mocks for cost control)
- **AI Response Testing**: Snapshot testing for AI prompts, regression testing for scoring algorithms, A/B testing framework for prompt optimization
- **End-to-End Tests**: Critical user paths (resume upload → interview → results) using headless browser automation
- **Manual Testing Support**: Developer-friendly test data generators, interview replay capability, and local OpenAI API stubbing for rapid iteration

Focus on testing the integration points with AI services rather than AI behavior itself - mock OpenAI responses for deterministic testing.

### Additional Technical Assumptions and Requests

**Frontend (ReactJS)**:
- **Framework**: React 18+ with TypeScript for type safety
- **State Management**: Context API for simple state, consider Zustand for complex interview state management
- **UI Component Library**: Material-UI (MUI) or Chakra UI for rapid development with accessible components
- **Real-time Audio**: WebRTC for audio streaming, MediaRecorder API for audio capture
- **Audio Visualization**: Web Audio API for real-time voice level visualization
- **Speech Recognition**: Browser SpeechRecognition API as fallback, Azure Speech SDK for primary
- **Rich Text Editor**: For recruiter feedback editing and AI response display formatting
- **Data Visualization**: Chart.js or Recharts for skill boundary maps and scoring visualizations

**Backend (FastAPI)**:
- **Framework**: FastAPI with Python 3.11+ for async performance and type hints
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Background Jobs**: Celery with Redis for resume parsing batch processing
- **Async Processing**: Native async/await for concurrent interview sessions
- **AI Service Integration**: LangChain framework for managing OpenAI API calls, prompt templates, and conversation memory
- **Structured Logging**: Python structlog for detailed AI decision tracking

**Database (PostgreSQL on Supabase)**:
- **Primary Database**: PostgreSQL 15+ on Supabase for rapid prototyping
- **Schema Design**: JSONB columns for flexible AI-generated data (scores, reasoning, red flags)
- **Real-time Capabilities**: Supabase real-time subscriptions for future live monitoring
- **Migration Strategy**: Alembic for database migrations to support future production PostgreSQL migration
- **Data Retention**: Archive strategy for completed interviews to manage storage costs

**AI Services**:
- **Primary LLM**: OpenAI GPT-4 for interview conversations and assessment reasoning
- **Speech-to-Text**: Azure Speech Services (Cognitive Services) for candidate audio transcription
- **Text-to-Speech**: Azure Speech Services with neural voices for natural AI responses
- **Voice Analysis**: Azure Speech Services for prosody analysis (speech patterns, hesitation, confidence)
- **Resume Parsing**: OpenAI GPT-4 with structured output for skill extraction
- **Prompt Management**: Version-controlled prompt templates, A/B testing capability for optimization
- **Cost Management**: Token counting for LLM, audio minute tracking for speech services, response caching, usage monitoring dashboards
- **Fallback Strategy**: Graceful degradation to text-only mode if speech services fail or rate limits hit

**Infrastructure & DevOps**:
- **Deployment**: Docker containers for consistent environments
- **Container Orchestration**: Docker Compose for MVP, Kubernetes-ready for scaling
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Environment Management**: Development, staging, and production environments
- **Secrets Management**: Environment variables with proper rotation policies
- **Monitoring**: Application performance monitoring (APM) and error tracking (Sentry or similar)
- **API Cost Tracking**: Dashboard for real-time OpenAI API usage and cost projections

**Security & Compliance**:
- **Authentication**: JWT tokens with secure password hashing (bcrypt)
- **API Security**: Rate limiting (per IP and per user), CORS configuration, input validation
- **Data Encryption**: TLS 1.3+ for transit, AES-256 for data at rest via Supabase
- **GDPR Compliance**: Data export APIs, data deletion workflows, audit logging
- **Secrets**: Never commit API keys - use environment variables and secret management tools

**Integration Requirements**:
- **RESTful APIs**: JSON-based with consistent error handling and pagination
- **Webhook Support**: For ATS integration callbacks (interview completion, results ready)
- **OAuth 2.0**: For secure third-party integrations
- **API Versioning**: URL-based versioning (/api/v1/) for backward compatibility
- **Rate Limiting**: Protect against abuse and manage costs

### High-Complexity Areas & Technical Risks

The following areas represent significant technical complexity and should be prioritized for architectural deep-dive and potential proof-of-concept work:

**1. Azure Speech Services Integration**
- **Risk Level:** High
- **Complexity:** Real-time speech-to-text and text-to-speech with low latency requirements (<1 second)
- **Challenges:** Audio quality variations, accent handling, technical terminology pronunciation, cost optimization
- **Mitigation:** Early prototype, comprehensive fallback to text-only mode, audio quality monitoring

**2. WebRTC Real-Time Audio Streaming**
- **Risk Level:** Medium-High
- **Complexity:** Browser compatibility, network variability, connection management
- **Challenges:** Sub-200ms latency requirement, reconnection handling, audio buffer management
- **Mitigation:** Fallback to HTTP-based audio transfer, extensive browser testing, connection quality monitoring

**3. AI Prompt Consistency & Quality**
- **Risk Level:** Medium
- **Complexity:** Ensuring consistent, high-quality interview questions across diverse technical domains
- **Challenges:** Avoiding repetitive questions, maintaining appropriate difficulty progression, handling edge cases
- **Mitigation:** Version-controlled prompt templates, A/B testing framework, comprehensive logging for refinement

**4. LangChain Conversation Memory at Scale**
- **Risk Level:** Medium
- **Complexity:** Managing conversation context for 50+ concurrent sessions with token optimization
- **Challenges:** Memory persistence, context window limits, cost control
- **Mitigation:** Efficient memory pruning strategies, conversation state snapshots, token usage monitoring

**5. Real-Time Integrity Analysis**
- **Risk Level:** Medium
- **Complexity:** Multi-signal cheating detection combining timing, pattern matching, and voice analysis
- **Challenges:** Avoiding false positives, balancing sensitivity, processing overhead
- **Mitigation:** Configurable thresholds, human review workflow, gradual rollout of integrity features

## Epic List

**Epic 1: Foundation & Core AI Interview Engine (Text-Based)**
Establish project infrastructure, core AI interview capability with text-based interaction, and basic candidate experience. Delivers first vertical slice: candidates can complete AI-driven technical interviews with adaptive questioning and progressive assessment methodology through text chat interface.

**Epic 1.5: Speech-to-Speech AI Interview Capability**
Add speech-to-text and text-to-speech integration, voice-based interview interface, and audio processing pipeline. Transforms text-based interviews into natural voice conversations while maintaining text fallback for code examples.

**Epic 2: Resume Intelligence & Interview Customization**
Add resume upload, batch parsing, and AI-powered interview customization based on candidate background. Delivers intelligent, personalized interview experiences tailored to each candidate's stated expertise.

**Epic 3: Integrity Monitoring & Assessment Scoring**
Implement multi-signal cheating detection, detailed scoring with AI reasoning, and skill boundary mapping. Delivers comprehensive assessment reports with integrity indicators that recruitment firms can trust.

**Epic 4: Recruiter Portal & Candidate Management**
Build recruiter dashboard, candidate detail views, and resume feedback approval workflow. Delivers complete recruiter experience for managing candidates, reviewing assessments, and controlling communication.

**Epic 5: ATS Integration & Production Readiness**
Implement RESTful APIs for ATS/HRIS integration, webhooks, deployment infrastructure, and production monitoring. Delivers pilot-ready platform with external system connectivity and enterprise operational capabilities.

## Epic 1: Foundation & Core AI Interview Engine (Text-Based)

**Epic Goal:** Establish foundational project infrastructure (monorepo setup, core dependencies, CI/CD pipeline) while delivering the first vertical slice of AI-driven interview capability through text-based interaction. By epic completion, candidates can start an interview session, interact with an adaptive AI interviewer that implements progressive assessment methodology via text chat, and receive basic completion confirmation. This proves the core AI logic and technical feasibility before adding speech complexity.

### Story 1.1: Project Initialization & Monorepo Setup

**As a** developer,  
**I want** a properly configured monorepo with frontend and backend scaffolding,  
**so that** the team can begin development with consistent tooling and structure.

**Acceptance Criteria:**

1. Monorepo created with separate `/frontend` and `/backend` directories
2. Frontend initialized with React 18+ TypeScript, Material-UI, and essential dependencies (Zustand, Axios)
3. Backend initialized with FastAPI Python 3.11+, project structure following best practices
4. Git repository initialized with `.gitignore` configured for Python and Node.js
5. README.md with project overview, setup instructions, and development guidelines
6. Package managers configured (npm/yarn for frontend, poetry/pip for backend)
7. Environment variable management setup (.env.example files for both frontend and backend)
8. Basic health check endpoints work: frontend serves on localhost:3000, backend API responds on localhost:8000/health

### Story 1.2: Database Schema & Core Data Models

**As a** developer,  
**I want** PostgreSQL database schema with core entities for interviews and candidates,  
**so that** the application can persist interview data and candidate information.

**Acceptance Criteria:**

1. Supabase PostgreSQL instance provisioned and connection configured
2. Database migration tool (Alembic) initialized with version control
3. Core tables created: `candidates`, `interviews`, `interview_messages`, `interview_sessions`
4. JSONB columns included for flexible AI-generated data storage (scores, reasoning, metadata)
5. Database models defined in backend with SQLAlchemy ORM
6. Proper indexes created for query performance (candidate_id, session_id, timestamps)
7. Database connection pooling configured for concurrent session support
8. Migration scripts tested: can initialize fresh database and rollback changes

### Story 1.3: Authentication & Candidate Session Management

**As a** candidate,  
**I want** to start an interview session with simple authentication,  
**so that** my interview progress is saved and associated with my identity.

**Acceptance Criteria:**

1. Simple candidate authentication implemented (email-based, JWT tokens)
2. Candidate registration endpoint created (`POST /api/v1/candidates/register`)
3. Candidate login endpoint created (`POST /api/v1/candidates/login`) returning JWT token
4. JWT middleware validates tokens on protected routes
5. Interview session creation endpoint (`POST /api/v1/interviews/start`) creates new session record
6. Session state persisted in database with candidate association
7. Frontend login/register UI components created with form validation
8. Successful authentication redirects candidate to interview start screen

### Story 1.4: OpenAI Integration & LangChain Setup

**As a** developer,  
**I want** OpenAI API integrated using LangChain framework,  
**so that** the system can conduct AI-powered conversations with candidates.

**Acceptance Criteria:**

1. OpenAI API key configured in environment variables with secure storage
2. LangChain library installed and configured for GPT-4 access
3. Conversation memory implementation using LangChain's ConversationBufferMemory
4. Prompt template system created for version-controlled interview prompts
5. Basic prompt templates created for technical interview scenarios (React, Python, JavaScript)
6. Token counting implemented to monitor API usage and costs
7. Error handling for API rate limits and timeouts with graceful degradation
8. Local development supports OpenAI API mocking for cost-free testing

### Story 1.5: Progressive Assessment Engine - Core Logic

**As a** developer,  
**I want** the AI interview engine to implement progressive difficulty adjustment,  
**so that** interviews start with confidence-building questions before exploring skill boundaries.

**Acceptance Criteria:**

1. Progressive assessment algorithm implemented with three difficulty levels: Warm-up, Standard, Advanced
2. Interview flow starts with 2-3 warm-up questions to build candidate confidence
3. AI analyzes candidate responses to determine current proficiency level
4. Difficulty automatically increases when candidate demonstrates competency
5. Skill boundary detection logic tracks where candidate begins to struggle
6. Question generation adapts to candidate's demonstrated knowledge level
7. Interview session stores progression state (current difficulty, questions asked, boundaries identified)
8. Unit tests verify progression logic with mocked AI responses

### Story 1.6: Candidate Interview UI - Text Chat Interface

**As a** candidate,  
**I want** a conversational text chat interface to interact with the AI interviewer,  
**so that** I can answer questions by typing and see my progress.

**Acceptance Criteria:**

1. Full-screen chat interface created with message bubbles (AI questions, candidate responses)
2. Text input area with character counter and submit button (enter key to send)
3. AI typing indicator displays while waiting for next question
4. Progress indicator shows approximate completion percentage
5. Message history displays full conversation in chronological order
6. Real-time message rendering as AI generates questions
7. Responsive design works on desktop (1920x1080 and 1366x768)
8. Auto-scroll keeps latest message visible

### Story 1.7: Real-Time Interview Conversation Flow

**As a** candidate,  
**I want** to have a natural back-and-forth conversation with the AI interviewer,  
**so that** I can demonstrate my technical knowledge through interactive dialogue.

**Acceptance Criteria:**

1. Backend API endpoint handles candidate message submission (`POST /api/v1/interviews/{id}/messages`)
2. AI generates contextually relevant follow-up questions based on previous responses
3. Conversation maintains context across entire interview session using LangChain memory
4. AI validates response relevance before generating next question
5. Interview session state updates with each message exchange
6. Frontend displays AI responses within 2 seconds of candidate message submission (per NFR2)
7. Error handling gracefully manages API failures without losing candidate progress
8. Interview conversation can be paused and resumed without context loss

### Story 1.8: Interview Completion & Basic Results

**As a** candidate,  
**I want** to receive confirmation when my interview is complete,  
**so that** I understand the interview has ended and know what happens next.

**Acceptance Criteria:**

1. AI interview engine detects interview completion based on question count and skill boundary coverage
2. Interview status updated to "completed" in database
3. Candidate sees completion confirmation screen with "Thank you" message
4. Basic completion summary displayed (interview duration, questions answered)
5. Next steps message explains when to expect full results
6. Interview session marked as immutable (no further message submissions accepted)
7. Backend API endpoint retrieves interview transcript (`GET /api/v1/interviews/{id}/transcript`)
8. Completed interview data persisted for later scoring and analysis

### Story 1.9: CI/CD Pipeline & Deployment Foundation

**As a** developer,  
**I want** automated testing and deployment pipeline,  
**so that** code changes are validated and can be deployed reliably.

**Acceptance Criteria:**

1. GitHub Actions workflow created for automated testing on push/PR
2. Frontend tests run automatically (unit tests for components)
3. Backend tests run automatically (unit tests for API endpoints and business logic)
4. Linting and code formatting checks enforce code quality standards (ESLint, Prettier, Black, mypy)
5. Docker Compose configuration created for local development environment
6. Dockerfiles created for frontend and backend with multi-stage builds
7. Development environment can be started with single command (`docker-compose up`)
8. CI pipeline prevents merging if tests fail or linting errors exist

## Epic 1.5: Speech-to-Speech AI Interview Capability

**Epic Goal:** Transform the text-based interview system into a natural voice-driven experience by integrating Azure Speech Services for speech-to-text and text-to-speech capabilities. By epic completion, candidates can speak their answers naturally while the AI responds with voice, creating an engaging conversational interview. The system maintains hybrid mode support (speak answers, type code) and gracefully degrades to text-only if speech services fail. This epic delivers the "wow factor" that differentiates Teamified from competitors.

### Story 1.5.1: Azure Speech Services Integration

**As a** developer,  
**I want** Azure Speech Services integrated for speech-to-text and text-to-speech processing,  
**so that** the system can capture candidate speech and generate AI voice responses.

**Acceptance Criteria:**

1. Azure Speech Services account provisioned with API keys configured in environment variables
2. Azure Speech SDK installed and configured in backend (Python SDK)
3. Speech-to-text service integrated with support for continuous recognition
4. Text-to-speech service integrated with neural voice selection (natural sounding)
5. Voice selection configured (professional, neutral tone appropriate for interviews)
6. Audio format handling implemented (support for common formats: WAV, MP3, WebM)
7. Error handling for Azure API failures with fallback to text-only mode
8. Cost tracking implemented for speech service usage (audio minutes consumed)

### Story 1.5.2: Real-Time Audio Capture - Frontend

**As a** candidate,  
**I want** to speak my answers using my microphone,  
**so that** I can respond naturally without typing.

**Acceptance Criteria:**

1. Microphone permission request implemented with clear explanation to candidate
2. MediaRecorder API integrated for audio capture from browser
3. Real-time audio visualization displays voice level (volume meter)
4. Push-to-talk button implemented (hold to speak, release to submit)
5. Voice-activated mode implemented (automatic speech detection, stops after silence)
6. Audio recording state management (idle, recording, processing, error)
7. Visual feedback shows recording state (microphone icon changes, pulsing animation)
8. Audio chunks streamed to backend for processing (not waiting for complete answer)

### Story 1.5.3: Speech-to-Text Processing Pipeline

**As a** developer,  
**I want** candidate speech converted to text in real-time,  
**so that** the AI can analyze responses and generate follow-up questions.

**Acceptance Criteria:**

1. Backend endpoint accepts audio stream chunks (`POST /api/v1/interviews/{id}/audio`)
2. Azure Speech Services processes audio and returns transcribed text
3. Speech processing completes within 1 second of audio completion (per NFR16)
4. Transcribed text stored in interview_messages table with audio metadata
5. Partial transcription support (live updates as candidate speaks)
6. Confidence scores captured for each transcription segment
7. Language detection and validation (English for MVP)
8. Error handling gracefully manages poor audio quality or silence

### Story 1.5.4: Text-to-Speech AI Response Generation

**As a** candidate,  
**I want** to hear the AI interviewer's questions spoken aloud,  
**so that** the interview feels like a natural conversation.

**Acceptance Criteria:**

1. AI-generated questions converted to speech using Azure Text-to-Speech
2. Neural voice used for natural, engaging speech quality
3. Speech generation completes within 1 second (per NFR17)
4. Audio file (or stream) returned to frontend for playback
5. Speech rate and prosody optimized for interview context (clear, professional pace)
6. Technical terms and acronyms pronounced correctly (React, API, JavaScript)
7. Audio caching implemented for repeated phrases to reduce costs
8. Backend endpoint serves generated audio (`GET /api/v1/interviews/{id}/audio/{message_id}`)

### Story 1.5.5: Voice-Based Interview UI Enhancement

**As a** candidate,  
**I want** an intuitive voice interview interface with clear visual feedback,  
**so that** I understand when to speak and when the AI is responding.

**Acceptance Criteria:**

1. Interview screen updated with prominent microphone controls
2. Visual states clearly differentiate: AI Speaking, AI Listening, Candidate Speaking, Processing
3. AI speech plays automatically through browser audio
4. Text transcript displays alongside voice (AI questions and candidate responses shown as text)
5. Volume controls allow candidate to adjust AI voice level
6. Replay button allows candidate to rehear last AI question
7. "Switch to Text Mode" button available for fallback preference
8. Loading/processing indicators show when audio is being transcribed or generated

### Story 1.5.6: Hybrid Input Mode - Voice + Text

**As a** candidate,  
**I want** to speak my answers but type code examples when needed,  
**so that** I can communicate complex technical details effectively.

**Acceptance Criteria:**

1. Text input area remains available during voice interview
2. Mode toggle button switches between voice-only and hybrid mode
3. Candidate can speak answer, then type code snippet before submitting
4. AI recognizes when candidate says "let me type this" or similar phrases
5. Interview flow seamlessly handles mixed voice and text responses
6. Transcript clearly indicates which parts were spoken vs typed
7. Text responses processed through same AI analysis pipeline
8. Hybrid responses stored with clear delineation (speech_part, text_part)

### Story 1.5.7: WebRTC Audio Streaming Setup

**As a** developer,  
**I want** low-latency audio streaming using WebRTC,  
**so that** voice conversations feel natural without noticeable delays.

**Acceptance Criteria:**

1. WebRTC peer connection established between frontend and backend
2. Audio streams transmitted with sub-200ms latency (per NFR18)
3. Audio quality maintains 16kHz sample rate minimum (per NFR19)
4. Network adaptation handles varying bandwidth conditions
5. Reconnection logic implemented for dropped connections
6. Audio buffer management prevents choppy playback
7. Real-time metrics monitor latency and audio quality
8. Fallback to HTTP-based audio transfer if WebRTC fails

### Story 1.5.8: Voice Pattern Analysis for Integrity Monitoring

**As a** developer,  
**I want** to capture speech patterns for integrity analysis,  
**so that** the system can detect hesitation, confidence levels, and potential cheating indicators.

**Acceptance Criteria:**

1. Azure Speech Services prosody analysis integrated (pitch, pace, volume variations)
2. Hesitation detection implemented (pauses, filler words, repeated starts)
3. Vocal confidence metrics captured (steady vs uncertain speech patterns)
4. Response timing tracked (time from question completion to speech start)
5. Speech pattern data stored in JSONB column for later analysis
6. Unusual patterns flagged (reading from script detection, multiple speakers)
7. Metrics available for Epic 3 integrity monitoring features
8. Privacy-conscious: audio files can be deleted post-transcription per GDPR

### Story 1.5.9: Graceful Degradation & Fallback Handling

**As a** candidate,  
**I want** the interview to continue even if speech features fail,  
**so that** technical issues don't prevent me from completing my assessment.

**Acceptance Criteria:**

1. Microphone access denial gracefully switches to text-only mode
2. Azure Speech Services failures trigger automatic text fallback
3. Poor audio quality detection prompts candidate to switch to text
4. Network latency issues handled without interview disruption
5. Clear messaging explains fallback reasons to candidate
6. Text-only mode fully functional as backup
7. Interview state preserved during mode transitions
8. System logs capture failure reasons for debugging and monitoring

## Checklist Results Report

### PM Checklist Validation - October 27, 2025

**Overall PRD Completeness:** 88%  
**MVP Scope Appropriateness:** Just Right (with adjusted 10-11 month timeline)  
**Readiness for Architecture Phase:** ✅ **READY**

#### Key Decisions Made:
1. ✅ **Epic 1.5 Speech-to-Speech retained** - Critical differentiator, timeline extended to 10-11 months
2. ✅ **Technical risk flags added** - High-complexity areas identified for architect focus
3. ✅ **Functional requirements renumbered** - FR1-FR20 now sequential
4. ✅ **Rate limiting specified** - 10 interview starts/hour per IP
5. ⏭️ **Deferred to later phases** - Cost projections, detailed operational procedures, GDPR workflows

#### Category Validation Summary:

| Category                         | Status | Score | Notes                                           |
| -------------------------------- | ------ | ----- | ----------------------------------------------- |
| 1. Problem Definition & Context  | PASS   | 95%   | Clear problem articulation                      |
| 2. MVP Scope Definition          | PASS   | 85%   | Timeline adjusted to 10-11 months for Epic 1.5  |
| 3. User Experience Requirements  | PASS   | 92%   | Comprehensive UX vision                         |
| 4. Functional Requirements       | PASS   | 95%   | Renumbered FR1-FR20 sequentially                |
| 5. Non-Functional Requirements   | PASS   | 92%   | Rate limiting specifics added                   |
| 6. Epic & Story Structure        | PASS   | 90%   | Epic 1.5 retained with timeline accommodation   |
| 7. Technical Guidance            | PASS   | 90%   | High-complexity areas flagged                   |
| 8. Cross-Functional Requirements | PASS   | 80%   | Production details deferred appropriately       |
| 9. Clarity & Communication       | PASS   | 95%   | Excellent structure and clarity                 |

#### Recommendations for Architect:

**Priority Areas for Deep-Dive:**
1. Azure Speech Services integration architecture (Epic 1.5)
2. WebRTC audio streaming implementation design
3. LangChain conversation memory management at scale
4. Database schema design with JSONB structure for AI outputs
5. Cost monitoring and optimization strategies

**Ready for Immediate Action:**
- Epic 1 architecture and story refinement can begin immediately
- Epic 1.5 requires architectural proof-of-concept for Azure Speech + WebRTC
- Clear technical boundaries enable parallel architecture work

### Validation Status: ✅ READY FOR ARCHITECTURE PHASE

The PRD provides sufficient detail and clarity for the architect to begin technical design. Speech-to-speech capability (Epic 1.5) is confirmed as a critical MVP feature with timeline adjusted to accommodate the additional complexity.

## Next Steps

### For UX Expert

Review this PRD and create detailed UX/UI specifications including:
- Complete user flow diagrams for candidate interview journey (voice-based)
- Wireframes/mockups for all core screens listed in UI Design Goals
- Voice interaction design patterns and audio UI components
- Accessibility implementation guide for WCAG AA compliance
- Design system and component library recommendations

**Command to initiate:** Load PRD and begin UX specification development focusing on speech-first interview experience.

### For Architect

Review this PRD and create comprehensive technical architecture including:
- Detailed system architecture diagram showing all components and integrations
- Database schema design with all tables, relationships, and indexes
- API contract specifications for all endpoints
- Azure Speech Services integration architecture
- WebRTC audio streaming implementation design
- Security architecture and data flow diagrams
- Deployment architecture for development, staging, and production environments
- Cost estimation for OpenAI and Azure services at pilot scale (500 interviews/month)

**Command to initiate:** Load PRD and begin architecture mode using this document as input foundation.

