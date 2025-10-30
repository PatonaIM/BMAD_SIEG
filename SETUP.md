# Development Setup

Quick guide to set up the Teamified Candidates Portal locally.

## Prerequisites

Install these tools before starting:

1. **Python 3.11.9** via pyenv:
   \`\`\`bash
   # Install pyenv (if not installed)
   # macOS: brew install pyenv
   # Linux: curl https://pyenv.run | bash
   
   pyenv install 3.11.9
   pyenv local 3.11.9
   \`\`\`

2. **UV Package Manager**:
   \`\`\`bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or via pip
   pip install uv
   \`\`\`

3. **Node.js 18+** (currently using v24.6.0):
   \`\`\`bash
   # macOS: brew install node
   # Or download from: https://nodejs.org/
   \`\`\`

4. **PostgreSQL** (for local development):
   \`\`\`bash
   # macOS: brew install postgresql@15
   # Linux: apt-get install postgresql-15
   \`\`\`

## Backend Setup

\`\`\`bash
cd backend

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials and OpenAI API key

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

## Frontend Setup

\`\`\`bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.development
# Edit .env.development if needed (API URL defaults to http://localhost:8000/api/v1)

# Start the development server
npm run dev
\`\`\`

Frontend will be available at: http://localhost:5173

## Running Tests

### Backend Tests
\`\`\`bash
cd backend
pytest
\`\`\`

### Frontend Tests
\`\`\`bash
cd frontend
npm test
\`\`\`

## IDE Setup (Optional)

### VS Code Recommended Extensions
- Python (ms-python.python)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Playwright Test (ms-playwright.playwright)

Install with:
\`\`\`bash
code --install-extension ms-python.python
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension ms-playwright.playwright
\`\`\`

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
