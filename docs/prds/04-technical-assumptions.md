# Technical Assumptions

## Repository Structure

**Monorepo**: Single repository containing frontend and backend modules for streamlined development, simplified dependency management, and easier coordination for a small team (2-4 developers). Enables atomic commits across full-stack features and reduces context switching.

## Service Architecture

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

## Testing Requirements

**Unit + Integration Testing with AI-Specific Strategies**: 
- **Unit Tests**: Core business logic, utility functions, data transformations (target 80%+ coverage)
- **Integration Tests**: API endpoints, database operations, external service mocking (OpenAI API mocks for cost control)
- **AI Response Testing**: Snapshot testing for AI prompts, regression testing for scoring algorithms, A/B testing framework for prompt optimization
- **End-to-End Tests**: Critical user paths (resume upload → interview → results) using headless browser automation
- **Manual Testing Support**: Developer-friendly test data generators, interview replay capability, and local OpenAI API stubbing for rapid iteration

Focus on testing the integration points with AI services rather than AI behavior itself - mock OpenAI responses for deterministic testing.

## Additional Technical Assumptions and Requests

**Frontend (ReactJS)**:
- **Framework**: React 18+ with TypeScript for type safety
- **State Management**: Context API for simple state, consider Zustand for complex interview state management
- **UI Component Library**: Material-UI (MUI) or Chakra UI for rapid development with accessible components
- **Real-time Audio**: WebRTC for audio streaming, MediaRecorder API for audio capture
- **Audio Visualization**: Web Audio API for real-time voice level visualization
- **Speech Recognition**: Browser SpeechRecognition API as fallback, backend-processed OpenAI Whisper for primary
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
- **Speech-to-Text**: OpenAI Whisper API for candidate audio transcription (backend-processed for security)
- **Text-to-Speech**: OpenAI TTS API with neural voices for natural AI responses
- **Voice Analysis**: Audio metadata analysis via OpenAI Whisper (confidence scores, timing patterns)
- **Resume Parsing**: OpenAI GPT-4 with structured output for skill extraction
- **Provider Abstraction**: Clean interfaces enabling future migration to Azure/GCP speech services without code changes
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

## High-Complexity Areas & Technical Risks

The following areas represent significant technical complexity and should be prioritized for architectural deep-dive and potential proof-of-concept work:

**1. OpenAI Speech Services Integration (Whisper STT + TTS API)**
- **Risk Level:** High
- **Complexity:** Real-time speech-to-text and text-to-speech with low latency requirements (<1 second)
- **Challenges:** Audio quality variations, accent handling, technical terminology pronunciation, 2-3s processing latency vs real-time streaming, cost optimization
- **Mitigation:** Backend audio processing for security, provider abstraction layer for future Azure/GCP migration, comprehensive fallback to text-only mode, audio quality monitoring

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
