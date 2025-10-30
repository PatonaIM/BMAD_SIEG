# Teamified Candidates Portal

An AI-powered technical interview platform designed for recruitment firms to efficiently assess technical candidates through natural speech-to-speech interviews.

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

\`\`\`
├── backend/                # FastAPI Python backend
│   ├── app/               # Application code
│   ├── tests/             # Backend tests
│   └── main.py            # API entrypoint
├── app/                   # Next.js frontend (App Router)
│   ├── login/            # Login page
│   ├── register/         # Registration page
│   ├── interview/        # Interview pages
│   └── health/           # Health check page
├── components/            # React components
│   ├── auth/             # Authentication components
│   └── interview/        # Interview components
├── lib/                   # Shared utilities and logic
│   ├── auth/             # Auth store, hooks, services
│   ├── interview/        # Interview store, hooks, services
│   ├── api/              # API client
│   └── config/           # Configuration
└── docs/                  # Project documentation
    ├── architecture/      # Technical architecture
    ├── prd/              # Product requirements
    └── stories/          # User stories
\`\`\`

## 📋 Prerequisites

### Required

- **Python 3.11.9** (managed via pyenv)
- **Node.js 18+** (currently using v24.6.0)
- **UV Package Manager** (for Python dependencies)
- **npm 8+** (for Node.js dependencies)

### Recommended

- **Git** 2.40+
- **Docker** 24+ (for future deployment)
- **VS Code** with ESLint and Prettier extensions

## 🚀 Installation & Setup

### 1. Install pyenv (Python Version Manager)

**macOS:**
\`\`\`bash
brew install pyenv
# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
\`\`\`

**Linux:**
\`\`\`bash
curl https://pyenv.run | bash
# Add to your shell profile (~/.bashrc or ~/.zshrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
\`\`\`

**Windows:**
Follow instructions at: https://github.com/pyenv-win/pyenv-win

### 2. Install Python 3.11.9

\`\`\`bash
pyenv install 3.11.9
pyenv local 3.11.9
python --version  # Should output: Python 3.11.9
\`\`\`

### 3. Backend Setup

\`\`\`bash
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
\`\`\`

### 4. Frontend Setup

\`\`\`bash
# From root directory

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
# Edit .env.local if needed (default: http://localhost:8000/api/v1)
\`\`\`

## 🏃 Running the Application

### Start Backend (Terminal 1)

\`\`\`bash
cd backend
source .venv/bin/activate  # Activate venv
uvicorn main:app --reload

# Backend will run on: http://localhost:8000
# OpenAPI docs at: http://localhost:8000/docs
\`\`\`

### Start Frontend (Terminal 2)

\`\`\`bash
# From root directory
npm run dev

# Frontend will run on: http://localhost:3000
\`\`\`

### Health Check

Once both services are running, visit:
- Backend Health: http://localhost:8000/health
- Frontend Health Check: http://localhost:3000/health
- Login Page: http://localhost:3000/login

## 🧪 Testing

### Backend Tests

\`\`\`bash
cd backend
source .venv/bin/activate
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest --cov=app --cov-report=term-missing  # With coverage
\`\`\`

### Frontend Tests

\`\`\`bash
# From root directory
npm run test              # Run tests in watch mode
npm run test:ui           # Run tests with UI
npm run test:coverage     # Run with coverage report
\`\`\`

## 🔍 Code Quality

### Backend Linting & Formatting

\`\`\`bash
cd backend
source .venv/bin/activate

# Check code quality
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
black .

# Type checking
mypy .
\`\`\`

### Frontend Linting & Formatting

\`\`\`bash
# From root directory

# Lint code
npm run lint

# Auto-fix lint issues
npm run lint:fix

# Format code
npm run format
\`\`\`

## 📚 Documentation

- **[Architecture Documentation](./docs/architecture/)** - Technical architecture and design decisions
- **[Product Requirements](./docs/prd/)** - Product goals and requirements
- **[User Stories](./docs/stories/)** - Development stories and tasks
- **[Coding Standards](./docs/architecture/coding-standards.md)** - Development best practices

## 🛠️ Tech Stack

### Backend
- **Language**: Python 3.11.9
- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0+ with asyncpg
- **AI**: OpenAI API (GPT-4o-mini/GPT-4, Whisper, TTS)
- **AI Orchestration**: LangChain
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: ruff, black, mypy

### Frontend
- **Framework**: Next.js 16 with React 19.2
- **Language**: TypeScript 5.9+
- **UI Library**: Material-UI (MUI) 7.3+ with Tailwind CSS 4
- **State Management**: Zustand 5.0+
- **Data Fetching**: TanStack Query 5.90+
- **Form Handling**: React Hook Form 7.65+ with Zod validation
- **Animations**: Framer Motion 12.23+
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
- ✅ Frontend migrated from React Router to Next.js 16
- ✅ Authentication system (login/register)
- ✅ Interview system with AI chat interface
- ✅ Material-UI design system integrated
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

**Happy coding! 🎉**
