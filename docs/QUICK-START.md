# Quick Start Guide

## Running the Application

### Backend (Python/FastAPI)

**⚠️ CRITICAL: Always use `uv run` for all Python commands**

```bash
# Navigate to backend
cd backend

# Start development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Run migrations
uv run alembic upgrade head

# Seed sample data
uv run python scripts/seed_job_postings.py
```

**Backend will run at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Frontend (Next.js/React)

```bash
# Navigate to frontend
cd frontend

# Start development server
pnpm dev
```

**Frontend will run at:** http://localhost:3000

---

## Best Practices

### Backend: Always Use `uv run`

Using `uv run` for all Python commands ensures:
- ✅ Correct virtual environment activation
- ✅ Proper dependency resolution
- ✅ Consistent behavior across environments
- ✅ No PATH or PYTHONPATH conflicts

**Common Mistakes:**

❌ **Don't do this:**
```bash
uvicorn main:app --reload    # Missing uv run
python scripts/seed.py       # Missing uv run
pytest                       # Missing uv run
```

✅ **Do this instead:**
```bash
uv run uvicorn main:app --reload
uv run python scripts/seed.py
uv run pytest
```

### Frontend: Always Use `pnpm`

Use `pnpm` consistently for all frontend package management:
- ✅ `pnpm install` - Install dependencies
- ✅ `pnpm dev` - Start development server
- ✅ `pnpm test` - Run tests
- ✅ `pnpm build` - Build for production

**Why pnpm?**
- 🚀 Up to 2x faster than npm
- 💾 Saves disk space with content-addressable storage
- 🔒 Stricter dependency management (prevents phantom dependencies)
- 📦 Better monorepo support

❌ **Don't use:** `npm` or `yarn` to avoid lock file conflicts and to benefit from pnpm's performance advantages.

---

## First Time Setup

### Prerequisites
- Python 3.11.9 (via pyenv)
- UV package manager
- Node.js 18+
- pnpm (install via: `npm install -g pnpm`)
- PostgreSQL 15+

### Backend Setup
```bash
cd backend
uv sync --dev
cp .env.example .env
# Edit .env with your credentials
uv run alembic upgrade head
uv run python scripts/seed_job_postings.py
```

### Frontend Setup
```bash
cd frontend
pnpm install
cp .env.example .env.development
# Edit if needed
```

---

## Useful Commands

### Backend

```bash
# Code quality
uv run ruff check .
uv run ruff check . --fix
uv run black .
uv run mypy .

# Testing
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest --cov=app --cov-report=html

# Database
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic revision --autogenerate -m "description"
```

### Frontend

```bash
# Development
pnpm dev
pnpm build
pnpm start

# Testing
pnpm test
pnpm test:ui
pnpm test:coverage

# Code quality
pnpm lint
pnpm lint:fix
pnpm format
```

---

## Troubleshooting

### Backend won't start
1. Check if PostgreSQL is running: `brew services start postgresql@15`
2. Verify DATABASE_URL in `.env`
3. Run migrations: `uv run alembic upgrade head`
4. Check if port 8000 is already in use

### Frontend won't connect to backend
1. Verify backend is running at http://localhost:8000
2. Check VITE_API_URL in `.env.development`
3. Check browser console for CORS errors

### Tests failing
1. Ensure test database is set up
2. Run migrations: `uv run alembic upgrade head`
3. Check test configuration in `conftest.py`

### "Command not found: uvicorn"
❌ You forgot `uv run`! All Python commands need the `uv run` prefix.

---

## Need More Help?

- **Complete Documentation:** [docs/COMPLETE-SYSTEM-DOCUMENTATION.md](./COMPLETE-SYSTEM-DOCUMENTATION.md)
- **Architecture:** [docs/architecture/](./architecture/)
- **Setup Guide:** [../SETUP.md](../SETUP.md)
- **README:** [../README.md](../README.md)
