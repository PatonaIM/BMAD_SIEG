# Development Setup

Quick guide to set up the Teamified Candidates Portal locally.

## Prerequisites

Install these tools before starting:

1. **Python 3.11.9** via pyenv:
   ```bash
   # Install pyenv (if not installed)
   # macOS: brew install pyenv
   # Linux: curl https://pyenv.run | bash
   
   pyenv install 3.11.9
   pyenv local 3.11.9
   ```

2. **UV Package Manager**:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or via pip
   pip install uv
   ```

3. **Node.js 18+** (currently using v24.6.0):
   ```bash
   # macOS: brew install node
   # Or download from: https://nodejs.org/
   ```

4. **pnpm** (faster than npm):
   ```bash
   npm install -g pnpm
   ```

5. **PostgreSQL** (for local development):
   ```bash
   # macOS: brew install postgresql@15
   # Linux: apt-get install postgresql-15
   ```

## Backend Setup

```bash
cd backend

# Install all dependencies (creates .venv automatically)
uv sync --dev

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials and OpenAI API key

# Run database migrations
uv run alembic upgrade head

# Seed sample job postings (optional, for development)
uv run python scripts/seed_job_postings.py
# This populates the database with 20+ realistic job postings for testing the application flow

# Start the backend server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> **⚠️ Critical:** Always prefix Python commands with `uv run` to ensure proper dependency resolution and virtual environment activation.

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Important: Always Use `uv run`

**All Python commands in the backend must be prefixed with `uv run`:**

```bash
# ✅ Correct
uv run uvicorn main:app --reload
uv run python scripts/seed_job_postings.py
uv run pytest
uv run alembic upgrade head

# ❌ Wrong - These will fail or use wrong dependencies
uvicorn main:app --reload
python scripts/seed_job_postings.py
pytest
```

**Modern UV workflow eliminates manual venv management:**

```bash
# ❌ Old way (no longer needed)
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# ✅ New way (UV handles everything)
uv sync --dev                    # Creates .venv + installs all deps
uv run <command>                 # Runs in correct environment automatically
```

**All frontend commands must use `pnpm`:**

```bash
# ✅ Correct
pnpm install
pnpm dev
pnpm test

# ❌ Wrong - Use pnpm instead
npm install
yarn dev
```

This ensures proper virtual environment activation and dependency resolution.

## Frontend Setup

```bash
cd frontend

# Install dependencies (pnpm is faster and more efficient than npm)
pnpm install

# Copy environment file
cp .env.example .env.development
# Edit .env.development if needed (API URL defaults to http://localhost:8000/api/v1)

# Start the development server
pnpm dev
```

> **⚠️ Important:** Always use `pnpm` for frontend package management. Do not use `npm` or `yarn` to avoid lock file conflicts and to benefit from pnpm's performance advantages.

Frontend will be available at: http://localhost:5173

## Running Tests

### Backend Tests
```bash
cd backend
uv run pytest
```

### Frontend Tests
```bash
cd frontend
pnpm test
```

## IDE Setup (Optional)

### VS Code Recommended Extensions
- Python (ms-python.python)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Playwright Test (ms-playwright.playwright)

Install with:
```bash
code --install-extension ms-python.python
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension ms-playwright.playwright
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `brew services start postgresql@15`
- Check DATABASE_URL in backend/.env

### Port Already in Use
- Backend: Change port in uvicorn command
- Frontend: Vite will auto-detect and suggest alternative port

### OpenAI API Issues
- Verify OPENAI_API_KEY in backend/.env
- Check API key has sufficient credits at platform.openai.com
