# Tech Stack

## Technology Stack Table

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

## Cloud Infrastructure

- **Provider:** Supabase (PostgreSQL) + Self-managed compute (Docker containers)
- **Key Services:** 
  - Supabase PostgreSQL (database with real-time capabilities)
  - OpenAI API (GPT-4o-mini/GPT-4, Whisper STT, TTS)
  - Docker + Docker Compose (local dev and deployment)
- **Deployment Regions:** Initially single region (US-East or AU based on primary user base)
- **Future Cloud:** AWS/GCP/Azure when scaling beyond pilot phase

## Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24+ | Containerization for consistent environments |
| Docker Compose | 2.23+ | Local multi-service orchestration |
| Git | 2.40+ | Version control |
| GitHub Actions | N/A | CI/CD pipeline automation |
| Postman/Insomnia | Latest | API testing and debugging |
| DBeaver/pgAdmin | Latest | Database management and queries |
| Python REPL | Built-in | Quick testing and debugging |

## Key Technology Decisions & Rationale

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

## Model Selection Strategy

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

