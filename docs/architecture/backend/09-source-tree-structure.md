# Source Tree Structure

\`\`\`
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

\`\`\`

**Key Design Decisions:**

1. **Service Layer Separation:** Business logic in `services/` completely decoupled from API routes
2. **Repository Pattern:** All database access isolated in `repositories/`, enables easy mocking
3. **Provider Abstraction:** External APIs in `providers/` with abstract base classes for future provider swaps
4. **Prompt Versioning:** LLM prompts stored as files for easy version control and A/B testing
5. **Test Organization:** Unit → Integration → E2E hierarchy matching testing pyramid

---
