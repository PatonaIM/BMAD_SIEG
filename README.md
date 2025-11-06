# Teamified Candidates Portal

An AI-powered technical interview platform designed for recruitment firms to efficiently assess technical candidates through natural speech-to-speech interviews.

> **📚 Quick Links:**  
> - **🚀 [Quick Start Guide](./docs/QUICK-START.md)** ← Start here for rapid setup!
> - **📖 [Complete System Documentation](./docs/COMPLETE-SYSTEM-DOCUMENTATION.md)** - Full technical guide
> - **⚠️ Important:** Backend: Always use `uv run` | Frontend: Always use `pnpm`

## 🎯 Project Overview

Teamified Candidates Portal enables recruitment consultants to conduct scalable, consistent, and fair technical assessments using AI-driven conversational interviews. The platform evaluates candidates across multiple technical domains (React, Python, JavaScript, Full-Stack) while providing detailed skill mapping and integrity indicators.

### Key Features

- **AI-Powered Interviews**: Natural speech-to-speech conversations powered by OpenAI GPT-4
- **Multi-Domain Assessment**: Support for React, Python, JavaScript, and Full-Stack roles
- **Resume-Based Questioning**: Tailored questions based on candidate's uploaded resume
- **Real-Time Speech Processing**: Whisper STT and OpenAI TTS for natural conversations
- **Comprehensive Skill Mapping**: Detailed technical proficiency assessments
- **Recruiter Dashboard**: Quick candidate review with transcripts and insights

## 🏗️ Architecture

This is a monorepo containing both frontend and backend applications:

```
├── backend/                # FastAPI Python backend
│   ├── app/               # Application code
│   ├── tests/             # Backend tests
│   └── main.py            # API entrypoint
├── frontend/              # React TypeScript frontend
│   ├── src/               # Source code
│   └── tests/             # Frontend tests
└── docs/                  # Project documentation
    ├── architecture/      # Technical architecture
    ├── prd/              # Product requirements
    └── stories/          # User stories
```

## 📋 Prerequisites

### Required

- **Python 3.11.9** (managed via pyenv)
- **Node.js 18+** (currently using v24.6.0)
- **UV Package Manager** (for Python dependencies)
- **pnpm 8+** (for Node.js dependencies - faster and more efficient than npm)

### Recommended

- **Git** 2.40+
- **Docker** 24+ (for future deployment)
- **VS Code** with ESLint and Prettier extensions

## 🚀 Installation & Setup

### 1. Install pyenv (Python Version Manager)

**macOS:**
```bash
brew install pyenv
# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

**Linux:**
```bash
curl https://pyenv.run | bash
# Add to your shell profile (~/.bashrc or ~/.zshrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
Follow instructions at: https://github.com/pyenv-win/pyenv-win

### 2. Install Python 3.11.9

```bash
pyenv install 3.11.9
pyenv local 3.11.9
python --version  # Should output: Python 3.11.9
```

### 3. Backend Setup

```bash
cd backend

# Install UV package manager
pip install uv

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration (DATABASE_URL, OPENAI_API_KEY, etc.)
```

### 4. Frontend Setup

```bash
cd frontend

# Install pnpm if not already installed
npm install -g pnpm

# Install dependencies
pnpm install

# Create environment file
cp .env.example .env.development
# Edit .env.development if needed
```

## 🏃 Running the Application

### Start Backend (from backend directory)

```bash
cd backend
source .venv/bin/activate  # Activate venv
uv run uvicorn main:app --reload

# Backend will run on: http://localhost:8000
# OpenAPI docs at: http://localhost:8000/docs
```

> **⚠️ Important:** Always use `uv run` to execute Python commands. This ensures the correct virtual environment and dependencies are used.

### Seed Sample Job Postings (Optional - for Development)

```bash
cd backend
uv run python scripts/seed_job_postings.py

# This generates 20+ diverse job postings across multiple tech stacks
# Run this after database migrations to populate the job postings table for testing
```

### Start Frontend (from frontend directory)

```bash
cd frontend
pnpm dev

# Frontend will run on: http://localhost:3000
```

### Health Check

Once both services are running, visit:
- Backend Health: http://localhost:8000/health
- Frontend: http://localhost:3000 (displays backend connection status)

## ⚡ Development Best Practices

### Backend: Always Use `uv run` for Python Commands

**✅ Correct:**
```bash
uv run uvicorn main:app --reload
uv run python scripts/seed_job_postings.py
uv run pytest
uv run alembic upgrade head
```

**❌ Incorrect:**
```bash
uvicorn main:app --reload        # Missing uv run
python scripts/seed.py           # Missing uv run
pytest                           # Missing uv run
```

**Why?** Using `uv run` ensures:
- Correct virtual environment activation
- Proper dependency resolution
- Consistent behavior across all environments
- No PATH or PYTHONPATH conflicts

### Frontend: Always Use `pnpm`

**✅ Correct:**
```bash
pnpm install
pnpm dev
pnpm test
pnpm build
```

**❌ Incorrect:**
```bash
npm install                      # Use pnpm instead
yarn dev                         # Use pnpm instead
```

**Why?** Using `pnpm` consistently:
- Faster installs (up to 2x faster than npm)
- Saves disk space (content-addressable storage)
- Stricter dependency management (prevents phantom dependencies)
- Avoids lock file conflicts (npm vs pnpm vs yarn)

## 🧪 Testing

### Backend Tests

```bash
cd backend
source .venv/bin/activate
uv run pytest tests/unit/              # Unit tests
uv run pytest tests/integration/       # Integration tests
uv run pytest --cov=app --cov-report=term-missing  # With coverage
```

### Frontend Tests

```bash
cd frontend
pnpm test              # Run tests in watch mode
pnpm test:ui           # Run tests with UI
pnpm test:coverage     # Run with coverage report
```

## 🔍 Code Quality

### Backend Linting & Formatting

```bash
cd backend
source .venv/bin/activate

# Check code quality
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Format code
uv run black .

# Type checking
uv run mypy .
```

### Frontend Linting & Formatting

```bash
cd frontend

# Lint code
pnpm lint

# Auto-fix lint issues
pnpm lint:fix

# Format code
pnpm format
```

## 📚 Documentation

- **[Architecture Documentation](./docs/architecture/)** - Technical architecture and design decisions
- **[Product Requirements](./docs/prd/)** - Product goals and requirements
- **[User Stories](./docs/stories/)** - Development stories and tasks
- **[Coding Standards](./docs/architecture/coding-standards.md)** - Development best practices

## � API Documentation

Interactive API documentation is available at **http://localhost:8000/docs** (Swagger UI) when the backend server is running.

### Job Postings API (Epic 03)

**List Job Postings**
```
GET /api/v1/job-postings
Query Parameters: role_category, tech_stack, location, employment_type, work_setup, experience_level, search, skip, limit
Response: { jobs: JobPosting[], total: number, skip: number, limit: number }
Authentication: None (public endpoint)
```

**Get Job Posting Details**
```
GET /api/v1/job-postings/{id}
Response: JobPosting object
Authentication: None (public endpoint)
```

### Applications API (Epic 03)

**Submit Application**
```
POST /api/v1/applications
Body: { job_posting_id: UUID }
Response: ApplicationDetailResponse with created interview
Authentication: Required (JWT)
```

**Get My Applications**
```
GET /api/v1/applications/me
Response: ApplicationWithJobDetails[] (includes job posting and interview data)
Authentication: Required (JWT)
```

**Get Application Details**
```
GET /api/v1/applications/{id}
Response: ApplicationDetailResponse
Authentication: Required (JWT)
```

### Enhanced Interview API (Epic 03)

**Start Interview (Enhanced)**
```
POST /api/v1/interviews/start
Body: { role_type?: string, resume_id?: UUID, application_id?: UUID }
Response: InterviewResponse
Authentication: Required (JWT)
Note: When application_id provided, role_type derived from job posting's tech_stack
```

## �🛠️ Tech Stack

### Backend
- **Language**: Python 3.11.9
- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0+ with asyncpg
- **AI**: OpenAI API (GPT-4o-mini/GPT-4, Whisper, TTS)
- **AI Orchestration**: LangChain
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: ruff, black, mypy

### Frontend
- **Framework**: React 18+ with TypeScript 5.0+
- **Build Tool**: Vite 5.0+
- **UI Library**: Material-UI (MUI) 5.14+
- **State Management**: Zustand 4.4+
- **Data Fetching**: TanStack Query 5.0+
- **Routing**: React Router 6.20+
- **Form Handling**: React Hook Form 7.48+ with Zod validation
- **Testing**: Vitest, React Testing Library

### Infrastructure (Coming Soon)
- **Database**: PostgreSQL 15+ (Supabase hosted)
- **Deployment**: Frontend (Vercel) + Backend (Render)
- **CI/CD**: GitHub Actions

## 🎯 Project Status

**Current Phase**: Foundation (Epic 1)
**Story**: 1.1 - Project Initialization & Monorepo Setup ✅

### Completed
- ✅ Monorepo structure with frontend and backend
- ✅ Python 3.11.9 environment with pyenv
- ✅ Backend FastAPI with health check endpoint
- ✅ Frontend React + TypeScript with Vite
- ✅ Basic health check UI connecting to backend
- ✅ Linting and formatting tools configured

### Next Steps
- Story 1.2: Database schema and core data models
- Story 1.3: Authentication and authorization
- Story 1.4: Resume upload and parsing

## 🤝 Contributing

### Development Workflow

1. Create a feature branch from `main`
2. Follow the coding standards in `docs/architecture/coding-standards.md`
3. Write tests for new functionality
4. Ensure all tests pass and linting is clean
5. Submit a pull request with detailed description

### Code Review Checklist

- [ ] All tests passing
- [ ] Code follows project standards
- [ ] No linting errors
- [ ] Documentation updated if needed
- [ ] Acceptance criteria met

## 📄 License

Proprietary - Teamified Candidates Portal

## 👥 Team

Built by the Teamified development team.

---

**For detailed setup instructions**, see [SETUP.md](./SETUP.md)

**For development questions**, refer to the architecture documentation in `docs/architecture/`
## 📖 Documentation

- [Development Setup](SETUP.md) - Quick start guide
- [Coding Standards](docs/architecture/coding-standards.md) - Code style and best practices
- [Style Guide](docs/style-guide/) - UI/UX design system
- [PRD](docs/prd.md) - Product requirements
- [Architecture](docs/architecture/) - Technical design documents

## 🤝 Contributing

See [Coding Standards](docs/architecture/coding-standards.md) for development guidelines.

---

**Happy coding! 🎉**
