# Coding Standards

## Overview
This document defines the coding standards and best practices for the Teamified Candidates Portal, covering both backend (Python/FastAPI) and frontend (React/TypeScript) development.

**Tech Stack Summary:**
- **Backend**: Python 3.11.9, FastAPI, SQLAlchemy 2.0, PostgreSQL, Pydantic
- **Frontend**: React 18, TypeScript 5.0, Vite, MUI 5, Zustand
- **AI Services**: OpenAI (GPT-4/GPT-4o-mini, Whisper, TTS), LangChain

---

## Backend Standards (Python/FastAPI)

### Code Organization

#### Project Structure
```
backend/
├── app/
│   ├── core/              # Core configuration
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── candidate.py
│   │   ├── interview.py
│   │   └── assessment.py
│   ├── schemas/           # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── interview.py
│   │   └── assessment.py
│   ├── repositories/      # Data access layer
│   │   ├── base.py
│   │   ├── candidate.py
│   │   └── interview.py
│   ├── services/          # Business logic layer
│   │   ├── auth_service.py
│   │   ├── interview_engine.py
│   │   └── speech_service.py
│   ├── providers/         # External API abstractions
│   │   ├── openai_provider.py
│   │   └── base_ai_provider.py
│   ├── api/               # API routes
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── interviews.py
│   │       └── assessments.py
│   └── utils/             # Helper functions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
└── main.py
```

#### File Naming Conventions
- **Models**: `{feature}.py` (e.g., `candidate.py`, `interview.py`)
- **Schemas**: `{feature}.py` (e.g., `auth.py`, `interview.py`)
- **Services**: `{feature}_service.py` (e.g., `auth_service.py`)
- **Routers**: `{feature}.py` (e.g., `interviews.py`)
- **Tests**: `test_{feature}.py` (e.g., `test_auth_service.py`)
- **All Python files**: `snake_case.py`

### Naming Conventions

```python
# ✅ Functions and variables: snake_case
def create_interview_session(candidate_id: UUID) -> Interview:
    session_data = {"candidate_id": candidate_id}
    return session_data

# ✅ Classes: PascalCase
class InterviewEngine:
    pass

class CandidateRepository:
    pass

# ✅ Constants: UPPER_SNAKE_CASE
MAX_INTERVIEW_DURATION = 3600
DEFAULT_MODEL = "gpt-4o-mini"
API_VERSION = "v1"

# ✅ Private methods/attributes: _leading_underscore
def _validate_internal_state(self) -> bool:
    pass

# ✅ Type aliases: PascalCase
InterviewDict = dict[str, Any]
```

### Type Hints (Required)

```python
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# ✅ Always include type hints
async def create_interview(
    candidate_id: UUID,
    resume_id: Optional[UUID] = None,
    role_type: str = "fullstack"
) -> Interview:
    """Create a new interview session."""
    pass

# ✅ Return types for all functions
def calculate_score(responses: List[str]) -> float:
    return 0.85

# ✅ Use Optional for nullable values
def get_resume_data(candidate_id: UUID) -> Optional[Dict[str, Any]]:
    return None

# ❌ Never omit type hints
async def create_interview(candidate_id, resume_id):  # Bad!
    pass
```

### SQLAlchemy Models

```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class Candidate(Base):
    """Candidate model representing job seekers."""
    
    __tablename__ = "candidates"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic fields with explicit types
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Status enum
    status = Column(
        SQLEnum("active", "inactive", "deleted", name="candidate_status"),
        default="active",
        nullable=False
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate")
    
    def __repr__(self) -> str:
        return f"<Candidate {self.email}>"

class Interview(Base):
    """Interview session model."""
    
    __tablename__ = "interviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    
    # Interview metadata
    role_type = Column(SQLEnum("react", "python", "javascript", "fullstack", name="role_type"))
    status = Column(
        SQLEnum("scheduled", "in_progress", "completed", "abandoned", name="interview_status"),
        default="scheduled"
    )
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # AI tracking
    ai_model_used = Column(String(50), nullable=True)
    total_tokens_used = Column(Integer, default=0)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    resume = relationship("Resume")
    session = relationship("InterviewSession", uselist=False, back_populates="interview")
```

### Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

# Enums for validation
class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

# Request schemas
class CandidateCreate(BaseModel):
    """Schema for creating a new candidate."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    password: str = Field(..., min_length=8)
    phone: Optional[str] = Field(None, pattern=r"^\+?[\d\s\-()]+$")

class InterviewCreate(BaseModel):
    """Schema for creating an interview."""
    candidate_id: UUID
    resume_id: Optional[UUID] = None
    role_type: str = Field(..., pattern="^(react|python|javascript|fullstack)$")

# Response schemas
class CandidateResponse(BaseModel):
    """Schema for candidate data in responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: EmailStr
    full_name: str
    phone: Optional[str]
    status: str
    created_at: datetime

class InterviewResponse(BaseModel):
    """Schema for interview data in responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    candidate_id: UUID
    role_type: str
    status: InterviewStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]

# Update schemas
class InterviewUpdate(BaseModel):
    """Schema for updating interview."""
    status: Optional[InterviewStatus] = None
    ai_model_used: Optional[str] = None

# Nested schemas
class InterviewWithCandidate(InterviewResponse):
    """Interview with candidate details."""
    candidate: CandidateResponse
```

### FastAPI Routes

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.schemas.interview import InterviewCreate, InterviewResponse
from app.services.interview_engine import InterviewEngine
from app.models.candidate import Candidate

router = APIRouter(prefix="/api/v1/interviews", tags=["interviews"])

@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    data: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Candidate = Depends(get_current_user),
    interview_service: InterviewEngine = Depends()
) -> InterviewResponse:
    """Create a new interview session."""
    try:
        interview = await interview_service.create_interview(
            candidate_id=data.candidate_id,
            resume_id=data.resume_id,
            role_type=data.role_type
        )
        return interview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Candidate = Depends(get_current_user)
) -> InterviewResponse:
    """Get interview by ID."""
    interview = await interview_repo.get_by_id(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.get("/", response_model=List[InterviewResponse])
async def list_interviews(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Candidate = Depends(get_current_user)
) -> List[InterviewResponse]:
    """List all interviews for current user."""
    interviews = await interview_repo.list_by_candidate(
        candidate_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return interviews
```

#### HTTP Status Codes
- `200` - OK (GET, PUT, PATCH)
- `201` - Created (POST)
- `204` - No Content (DELETE)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (Pydantic validation)
- `429` - Too Many Requests (rate limiting)
- `500` - Internal Server Error

### Service Layer

```python
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.repositories.interview import InterviewRepository
from app.providers.openai_provider import OpenAIProvider
from app.models.interview import Interview

logger = structlog.get_logger()

class InterviewEngine:
    """Business logic for managing interviews."""
    
    def __init__(
        self,
        db: AsyncSession,
        ai_provider: OpenAIProvider,
        interview_repo: InterviewRepository
    ):
        self.db = db
        self.ai_provider = ai_provider
        self.interview_repo = interview_repo
        self.logger = logger.bind(service="interview_engine")
    
    async def create_interview(
        self,
        candidate_id: UUID,
        resume_id: Optional[UUID],
        role_type: str
    ) -> Interview:
        """Create a new interview session."""
        self.logger.info(
            "creating_interview",
            candidate_id=str(candidate_id),
            role_type=role_type
        )
        
        try:
            # Business logic here
            interview = await self.interview_repo.create(
                candidate_id=candidate_id,
                resume_id=resume_id,
                role_type=role_type
            )
            
            self.logger.info(
                "interview_created",
                interview_id=str(interview.id)
            )
            return interview
            
        except Exception as e:
            self.logger.error(
                "interview_creation_failed",
                error=str(e),
                candidate_id=str(candidate_id)
            )
            raise
    
    async def generate_question(
        self,
        interview_id: UUID,
        context: dict
    ) -> str:
        """Generate next interview question using AI."""
        try:
            question = await self.ai_provider.generate_question(
                context=context,
                model="gpt-4o-mini"
            )
            
            self.logger.info(
                "question_generated",
                interview_id=str(interview_id),
                tokens=context.get("tokens_used", 0)
            )
            return question
            
        except Exception as e:
            self.logger.error(
                "question_generation_failed",
                interview_id=str(interview_id),
                error=str(e)
            )
            raise
```

### Repository Pattern

```python
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import Interview

class InterviewRepository:
    """Data access layer for Interview model."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        candidate_id: UUID,
        resume_id: Optional[UUID],
        role_type: str
    ) -> Interview:
        """Create a new interview."""
        interview = Interview(
            candidate_id=candidate_id,
            resume_id=resume_id,
            role_type=role_type,
            status="scheduled"
        )
        self.db.add(interview)
        await self.db.commit()
        await self.db.refresh(interview)
        return interview
    
    async def get_by_id(self, interview_id: UUID) -> Optional[Interview]:
        """Get interview by ID."""
        stmt = select(Interview).where(Interview.id == interview_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_by_candidate(
        self,
        candidate_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        """List interviews for a candidate."""
        stmt = (
            select(Interview)
            .where(Interview.candidate_id == candidate_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, interview: Interview) -> Interview:
        """Update interview."""
        await self.db.commit()
        await self.db.refresh(interview)
        return interview
```

### Async/Await (Required)

```python
# ✅ All I/O operations must be async
async def get_candidate(candidate_id: UUID) -> Candidate:
    return await candidate_repo.get_by_id(candidate_id)

# ✅ Database operations
async def save_interview(interview: Interview) -> None:
    await db.commit()

# ✅ External API calls
async def generate_question(context: dict) -> str:
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=context["messages"]
    )
    return response.choices[0].message.content

# ✅ Multiple concurrent operations
async def process_batch():
    results = await asyncio.gather(
        api_call_1(),
        api_call_2(),
        api_call_3()
    )
    return results
```

### Error Handling

```python
from fastapi import HTTPException, status
import structlog

logger = structlog.get_logger()

# ✅ Use FastAPI HTTPException for API errors
async def get_interview(interview_id: UUID) -> Interview:
    interview = await interview_repo.get_by_id(interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found"
        )
    return interview

# ✅ Handle external API failures gracefully
async def call_openai_api(prompt: str) -> str:
    try:
        response = await openai_provider.generate(prompt)
        return response
    except openai.RateLimitError as e:
        logger.warning("openai_rate_limit", retry_after=60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again in 1 minute."
        )
    except openai.APIError as e:
        logger.error("openai_api_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable"
        )

# ✅ Structured logging for debugging
try:
    result = await process_interview(interview_id)
except Exception as e:
    logger.error(
        "interview_processing_failed",
        interview_id=str(interview_id),
        error=str(e),
        error_type=type(e).__name__
    )
    raise
```

### Logging Standards

```python
import structlog

# ✅ Use structured logging with context
logger = structlog.get_logger()

logger.info(
    "interview_started",
    interview_id=str(interview_id),
    candidate_id=str(candidate_id),
    role_type=role_type
)

logger.warning(
    "high_token_usage",
    interview_id=str(interview_id),
    tokens_used=5000,
    threshold=4000
)

logger.error(
    "ai_provider_failure",
    provider="openai",
    error=str(e),
    retry_count=3
)

# ❌ Avoid print statements
print(f"Interview {interview_id} started")  # Bad!

# ❌ Avoid console.log (this is Python, not JavaScript!)
console.log("Something happened")  # This doesn't exist in Python!
```

### Security Standards

```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ✅ JWT token generation
def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ❌ Never store passwords in plaintext
candidate.password = request.password  # Bad!

# ❌ Never expose API keys in responses
return {"openai_key": settings.OPENAI_API_KEY}  # Bad!
```

---

## Frontend Standards (React + TypeScript)

### Component Structure

#### Functional Components with TypeScript
```typescript
import React, { useState, useEffect } from 'react';
import { Button } from '@mui/material';
import type { Interview } from '@/types/interview.types';

interface InterviewCardProps {
  interview: Interview;
  onStart: (id: string) => void;
  isLoading?: boolean;
}

/**
 * InterviewCard displays interview details with action buttons
 */
export const InterviewCard: React.FC<InterviewCardProps> = ({ 
  interview, 
  onStart, 
  isLoading = false 
}) => {
  const [expanded, setExpanded] = useState(false);

  const handleStart = () => {
    onStart(interview.id);
  };

  return (
    <div className="interview-card">
      <h3>{interview.roleType}</h3>
      <p>Status: {interview.status}</p>
      <Button 
        onClick={handleStart} 
        disabled={isLoading}
        variant="contained"
      >
        {isLoading ? 'Starting...' : 'Start Interview'}
      </Button>
    </div>
  );
};

export default InterviewCard;
```

#### File Organization
```
src/
├── components/
│   ├── ui/                    # Reusable UI components
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.test.tsx
│   │   │   └── index.ts
│   │   └── WaveformVisualizer/
│   ├── interview/             # Feature-specific components
│   │   ├── InterviewCard.tsx
│   │   └── InterviewChat.tsx
├── pages/
│   ├── CandidateDashboard/
│   │   ├── CandidateDashboard.tsx
│   │   └── CandidateDashboard.test.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useInterviewSession.ts
│   └── useAudioRecording.ts
├── services/
│   ├── api/
│   │   ├── interviews.ts
│   │   └── auth.ts
├── stores/
│   ├── authStore.ts
│   └── interviewStore.ts
├── types/
│   ├── interview.types.ts
│   └── auth.types.ts
└── utils/
    ├── formatters.ts
    └── validators.ts
```

### Naming Conventions

```typescript
// ✅ Components: PascalCase
const InterviewCard: React.FC = () => <div />;
const WaveformVisualizer: React.FC = () => <canvas />;

// ✅ Files: Match component names
// InterviewCard.tsx, WaveformVisualizer.tsx

// ✅ Hooks: camelCase with 'use' prefix
const useAuth = () => { };
const useInterviewSession = () => { };

// ✅ Functions: camelCase
function formatDate(date: Date): string { }
function validateEmail(email: string): boolean { }

// ✅ Constants: UPPER_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';
const MAX_FILE_SIZE = 10485760; // 10MB

// ✅ Types/Interfaces: PascalCase
interface InterviewProps { }
type InterviewStatus = 'scheduled' | 'in_progress' | 'completed';

// ✅ Boolean props: is/has/should prefix
interface ButtonProps {
  isLoading?: boolean;
  hasError?: boolean;
  shouldAutoFocus?: boolean;
}

// ✅ Event handlers: on prefix
interface FormProps {
  onSubmit: (data: FormData) => void;
  onChange: (field: string, value: any) => void;
  onError: (error: Error) => void;
}
```

### State Management with Zustand

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import type { User } from '@/types/auth.types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  
  // Actions
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  setUser: (user) => set({ user, isAuthenticated: true }),
  setToken: (token) => set({ token }),
  logout: () => set({ user: null, token: null, isAuthenticated: false }),
}));

// Usage in component
import { useAuthStore } from '@/stores/authStore';

const user = useAuthStore((state) => state.user);
const { logout } = useAuthStore();
```

### Data Fetching with TanStack Query

```typescript
// services/api/interviews.ts
import { apiClient } from './client';
import type { Interview, InterviewCreate } from '@/types/interview.types';

export const interviewKeys = {
  all: ['interviews'] as const,
  lists: () => [...interviewKeys.all, 'list'] as const,
  list: (filters: string) => [...interviewKeys.lists(), { filters }] as const,
  details: () => [...interviewKeys.all, 'detail'] as const,
  detail: (id: string) => [...interviewKeys.details(), id] as const,
};

export const fetchInterviews = async (): Promise<Interview[]> => {
  const response = await apiClient.get('/api/v1/interviews');
  return response.data;
};

export const fetchInterview = async (id: string): Promise<Interview> => {
  const response = await apiClient.get(`/api/v1/interviews/${id}`);
  return response.data;
};

export const createInterview = async (data: InterviewCreate): Promise<Interview> => {
  const response = await apiClient.post('/api/v1/interviews', data);
  return response.data;
};

// hooks/useInterviews.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchInterviews, createInterview, interviewKeys } from '@/services/api/interviews';

export const useInterviews = () => {
  return useQuery({
    queryKey: interviewKeys.lists(),
    queryFn: fetchInterviews,
  });
};

export const useInterview = (id: string) => {
  return useQuery({
    queryKey: interviewKeys.detail(id),
    queryFn: () => fetchInterview(id),
    enabled: !!id,
  });
};

export const useCreateInterview = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createInterview,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: interviewKeys.lists() });
    },
  });
};

// Usage in component
const { data: interviews, isLoading, error } = useInterviews();
const { mutate: createNewInterview, isPending } = useCreateInterview();
```

### Form Handling with React Hook Form + Zod

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// Define validation schema
const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await loginUser(data);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input
          {...register('email')}
          type="email"
          placeholder="Email"
        />
        {errors.email && <span>{errors.email.message}</span>}
      </div>
      
      <div>
        <input
          {...register('password')}
          type="password"
          placeholder="Password"
        />
        {errors.password && <span>{errors.password.message}</span>}
      </div>
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

### MUI Theming

```typescript
// theme/theme.ts
import { createTheme } from '@mui/material/styles';

export const teamifiedTheme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
  },
});

// Use in component with sx prop
<Box
  sx={{
    backgroundColor: 'primary.main',
    color: 'primary.contrastText',
    padding: (theme) => theme.spacing(2),
    borderRadius: (theme) => theme.shape.borderRadius,
  }}
>
  Content
</Box>
```

### Error Handling

```typescript
// ✅ Use try-catch for async operations
const handleStartInterview = async () => {
  try {
    setIsLoading(true);
    const interview = await startInterview(interviewId);
    navigate(`/interview/${interview.id}`);
  } catch (error) {
    console.error('Failed to start interview:', error);
    setError('Failed to start interview. Please try again.');
  } finally {
    setIsLoading(false);
  }
};

// ✅ Display error messages to users
{error && (
  <div role="alert" className="error-message">
    {error}
  </div>
)}

// ✅ Handle API errors with TanStack Query
const { data, error, isError } = useInterviews();

if (isError) {
  return <div>Error loading interviews: {error.message}</div>;
}
```

### TypeScript Best Practices

```typescript
// ✅ Define proper types
interface Interview {
  id: string;
  candidateId: string;
  roleType: 'react' | 'python' | 'javascript' | 'fullstack';
  status: InterviewStatus;
  startedAt: Date | null;
}

// ✅ Use type inference
const interviews = useInterviews(); // Type is inferred

// ✅ Avoid 'any' - use 'unknown' if type is truly unknown
const parseResponse = (data: unknown): Interview => {
  // Type guard
  if (isInterview(data)) {
    return data;
  }
  throw new Error('Invalid interview data');
};

// ❌ Avoid 'any'
const badFunction = (data: any) => { }; // Bad!

// ✅ Use optional chaining
const email = user?.profile?.email;

// ✅ Use nullish coalescing
const displayName = user?.fullName ?? 'Guest';
```

---

## Testing Standards

### Backend Testing (pytest)

#### Test Structure
```python
# tests/unit/test_interview_engine.py
import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock
from app.services.interview_engine import InterviewEngine
from app.models.interview import Interview

@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()

@pytest.fixture
def mock_ai_provider():
    """Mock AI provider."""
    provider = Mock()
    provider.generate_question = AsyncMock(return_value="What is React?")
    return provider

@pytest.fixture
def interview_engine(mock_db, mock_ai_provider):
    """Create InterviewEngine with mocked dependencies."""
    repo = Mock()
    return InterviewEngine(
        db=mock_db,
        ai_provider=mock_ai_provider,
        interview_repo=repo
    )

class TestInterviewEngine:
    """Test suite for InterviewEngine service."""
    
    @pytest.mark.asyncio
    async def test_create_interview_success(self, interview_engine):
        """Test successful interview creation."""
        candidate_id = uuid4()
        role_type = "react"
        
        interview = await interview_engine.create_interview(
            candidate_id=candidate_id,
            resume_id=None,
            role_type=role_type
        )
        
        assert interview is not None
        assert interview.role_type == role_type
    
    @pytest.mark.asyncio
    async def test_generate_question_calls_ai_provider(self, interview_engine, mock_ai_provider):
        """Test that generate_question calls AI provider correctly."""
        interview_id = uuid4()
        context = {"messages": []}
        
        question = await interview_engine.generate_question(interview_id, context)
        
        assert question == "What is React?"
        mock_ai_provider.generate_question.assert_called_once_with(
            context=context,
            model="gpt-4o-mini"
        )
    
    @pytest.mark.asyncio
    async def test_create_interview_with_invalid_role_raises_error(self, interview_engine):
        """Test that invalid role_type raises ValueError."""
        candidate_id = uuid4()
        
        with pytest.raises(ValueError, match="Invalid role type"):
            await interview_engine.create_interview(
                candidate_id=candidate_id,
                resume_id=None,
                role_type="invalid"
            )
```

#### Integration Tests
```python
# tests/integration/test_interview_flow.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db
from tests.utils import create_test_candidate, create_test_token

@pytest.mark.asyncio
async def test_complete_interview_flow(db: AsyncSession, client: AsyncClient):
    """Test complete interview flow from creation to completion."""
    # Setup
    candidate = await create_test_candidate(db)
    token = create_test_token(candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create interview
    create_response = await client.post(
        "/api/v1/interviews",
        json={
            "candidate_id": str(candidate.id),
            "role_type": "react"
        },
        headers=headers
    )
    assert create_response.status_code == 201
    interview_id = create_response.json()["id"]
    
    # Start interview
    start_response = await client.post(
        f"/api/v1/interviews/{interview_id}/start",
        headers=headers
    )
    assert start_response.status_code == 200
    
    # Submit answer
    answer_response = await client.post(
        f"/api/v1/interviews/{interview_id}/answer",
        json={"answer": "React is a JavaScript library for building UIs"},
        headers=headers
    )
    assert answer_response.status_code == 200
    
    # Complete interview
    complete_response = await client.post(
        f"/api/v1/interviews/{interview_id}/complete",
        headers=headers
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"
```

### Frontend Testing (Vitest + React Testing Library)

#### Component Tests
```typescript
// components/interview/InterviewCard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { InterviewCard } from './InterviewCard';
import type { Interview } from '@/types/interview.types';

const mockInterview: Interview = {
  id: '123',
  candidateId: '456',
  roleType: 'react',
  status: 'scheduled',
  startedAt: null,
  completedAt: null,
  durationSeconds: null,
};

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('InterviewCard', () => {
  const mockOnStart = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders interview details', () => {
    render(
      <InterviewCard 
        interview={mockInterview} 
        onStart={mockOnStart} 
      />,
      { wrapper: createWrapper() }
    );
    
    expect(screen.getByText('react')).toBeInTheDocument();
    expect(screen.getByText(/Status: scheduled/i)).toBeInTheDocument();
  });

  it('calls onStart when button is clicked', async () => {
    render(
      <InterviewCard 
        interview={mockInterview} 
        onStart={mockOnStart} 
      />,
      { wrapper: createWrapper() }
    );
    
    const startButton = screen.getByRole('button', { name: /start interview/i });
    fireEvent.click(startButton);
    
    await waitFor(() => {
      expect(mockOnStart).toHaveBeenCalledWith('123');
    });
  });

  it('disables button when loading', () => {
    render(
      <InterviewCard 
        interview={mockInterview} 
        onStart={mockOnStart}
        isLoading={true}
      />,
      { wrapper: createWrapper() }
    );
    
    const startButton = screen.getByRole('button');
    expect(startButton).toBeDisabled();
    expect(screen.getByText(/starting/i)).toBeInTheDocument();
  });
});
```

#### Hook Tests
```typescript
// hooks/useInterviews.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useInterviews } from './useInterviews';
import * as interviewsApi from '@/services/api/interviews';

vi.mock('@/services/api/interviews');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useInterviews', () => {
  it('fetches interviews successfully', async () => {
    const mockInterviews = [
      { id: '1', roleType: 'react', status: 'scheduled' },
      { id: '2', roleType: 'python', status: 'completed' },
    ];
    
    vi.spyOn(interviewsApi, 'fetchInterviews').mockResolvedValue(mockInterviews);
    
    const { result } = renderHook(() => useInterviews(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    
    expect(result.current.data).toEqual(mockInterviews);
  });

  it('handles fetch error', async () => {
    vi.spyOn(interviewsApi, 'fetchInterviews').mockRejectedValue(
      new Error('API Error')
    );
    
    const { result } = renderHook(() => useInterviews(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
    
    expect(result.current.error).toBeDefined();
  });
});
```

---

## Commit Message Standards

### Format Structure (Conventional Commits)

All commit messages must follow this structure:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Character Limits (50/72 Rule)

- **Subject line**: 50 characters maximum (including type and scope)
- **Body lines**: 72 characters maximum per line
- **Why**: Ensures readability in git logs, GitHub UI, and terminal displays

### Required Types

- `feat`: New feature for the user
- `fix`: Bug fix for the user
- `docs`: Documentation changes
- `style`: Code formatting, missing semicolons, etc. (no production code change)
- `refactor`: Code refactoring (no functional changes)
- `test`: Adding missing tests or correcting existing tests
- `chore`: Build process, dependency updates, tooling changes
- `perf`: Performance improvements
- `ci`: Continuous integration changes
- `build`: Build system or external dependencies
- `revert`: Reverts a previous commit

### Optional Scope

Use scope to specify the area of change:
- `(api)`: Backend API changes
- `(ui)`: Frontend/UI changes
- `(auth)`: Authentication related
- `(db)`: Database changes
- `(config)`: Configuration changes
- `(deps)`: Dependency updates
- `(interview)`: Interview feature changes
- `(speech)`: Speech processing changes

### Description Guidelines

- Use imperative mood ("add" not "added" or "adds")
- Start with lowercase letter
- No period at the end
- Be specific but concise
- Focus on WHAT and WHY, not HOW

### Examples

**Simple commits:**
```
feat(auth): add password reset functionality
fix(api): resolve race condition in user registration
docs: update API authentication guide
refactor(ui): restructure component hierarchy
test(interview): add tests for question generation
```

**With body:**
```
fix(api): resolve race condition in user registration

Introduce request ID tracking to dismiss incoming responses
other than from latest request. This prevents duplicate user
creation when users double-click the register button.

Fixes #234
```

**Breaking change:**
```
feat(api)!: change authentication endpoint structure

BREAKING CHANGE: /auth/login now requires email instead of username.
Update all client applications to use email field for authentication.

Closes #456
```

### Anti-patterns to Avoid

❌ **Don't:**
- `Updated stuff`
- `Fixed bug`
- `feat: Added new feature for users to be able to login`
- `WIP` or `temp commit`
- Mixing multiple unrelated changes

✅ **Do:**
- `fix(auth): handle invalid token error`
- `feat(ui): add dark mode toggle`
- `docs: update API authentication guide`
- `refactor(db): optimize user query performance`

---

## Code Quality Tools

### Backend (Python)

**Linting & Formatting:**
```bash
# Format code with black
black app/ tests/

# Lint with ruff (replaces flake8, isort, pylint)
ruff check app/ tests/

# Auto-fix issues
ruff check --fix app/ tests/

# Type checking with mypy
mypy app/

# Security scanning with bandit
bandit -r app/
```

**Testing:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_interview_engine.py

# Run with verbose output
pytest -v

# Run async tests
pytest -v -k "async"
```

### Frontend (TypeScript/React)

**Linting & Formatting:**
```bash
# Lint TypeScript/React code
npm run lint

# Auto-fix linting issues
npm run lint:fix

# Format with Prettier (if separate)
npm run format

# Type checking
npm run type-check
```

**Testing:**
```bash
# Run all tests
npm run test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test -- InterviewCard.test.tsx

# Watch mode
npm run test:watch
```

---

## Critical Rules for AI Code Generation

### Backend (Python)

**🚨 NEVER:**
- Use `console.log()` (Python has no console.log, use `logger.info()`)
- Store passwords in plaintext
- Expose API keys in responses or frontend code
- Skip input validation on API endpoints
- Use `SELECT *` in queries (specify columns)
- Use synchronous I/O operations (always use async/await)
- Import unused dependencies

**✅ ALWAYS:**
- Use structured logging with context: `logger.info("event_name", key=value)`
- Use type hints for all function parameters and returns
- Wrap external API calls in try-except with proper error handling
- Use Pydantic schemas for request/response validation
- Use async/await for all I/O operations (DB, API calls)
- Use the repository pattern for database access
- Hash passwords with bcrypt before storing
- Validate and sanitize all user inputs

### Frontend (React/TypeScript)

**🚨 NEVER:**
- Use `any` type without justification
- Store sensitive data (tokens, passwords) in localStorage without encryption
- Make API calls directly from components (use services/hooks)
- Skip error boundaries for component error handling
- Hardcode API URLs (use environment variables)
- Forget to cleanup effects (return cleanup function)

**✅ ALWAYS:**
- Define proper TypeScript interfaces for props and state
- Use TanStack Query for server state management
- Implement proper loading and error states
- Use React Hook Form + Zod for form validation
- Include accessibility attributes (ARIA labels, roles)
- Use MUI theme values instead of hardcoded colors/spacing
- Implement proper error handling with try-catch
- Clean up subscriptions and timers in useEffect

---

## Performance Standards

### Backend
- Database queries should use indexes for frequently queried fields
- Implement pagination for endpoints returning large datasets (default: 100 items)
- Use async operations to handle concurrent requests efficiently
- Cache frequently accessed data (resume parsing results, candidate profiles)
- Monitor token usage for AI API calls to control costs
- Use connection pooling for database connections

### Frontend
- Lazy load routes and large components
- Use React.memo for expensive component renders
- Implement virtualization for long lists (react-window)
- Optimize images and assets
- Use TanStack Query's caching to minimize API calls
- Debounce search inputs and API-triggered events
- Code-split by route to reduce initial bundle size

---

## Security Standards

### Backend
- All passwords must be hashed with bcrypt (12+ rounds)
- JWT tokens with appropriate expiration (15 min access, 7 day refresh)
- Rate limiting on all public endpoints (configurable via slowapi)
- SQL injection prevention via SQLAlchemy ORM (no raw SQL)
- Input validation and sanitization on all endpoints (Pydantic)
- CORS configuration restricted to known frontend origins
- API keys stored in environment variables, never in code
- Audit logging for sensitive operations (user creation, interview completion)

### Frontend
- Store JWT tokens in httpOnly cookies (not localStorage)
- Validate all user inputs on client side (Zod schemas)
- Implement CSRF protection for state-changing operations
- Use HTTPS in production
- Content Security Policy headers
- Sanitize user-generated content before rendering
- Implement proper authentication checks on protected routes

---

## Documentation Standards

### Python Docstrings
```python
def create_interview(
    candidate_id: UUID,
    resume_id: Optional[UUID],
    role_type: str
) -> Interview:
    """
    Create a new interview session for a candidate.
    
    Args:
        candidate_id: UUID of the candidate
        resume_id: Optional UUID of the resume to use for customization
        role_type: Type of role to interview for ('react', 'python', 'javascript', 'fullstack')
    
    Returns:
        Interview: The created interview instance
    
    Raises:
        ValueError: If role_type is invalid
        HTTPException: If candidate not found (404)
    
    Example:
        >>> interview = await create_interview(
        ...     candidate_id=uuid4(),
        ...     resume_id=None,
        ...     role_type="react"
        ... )
    """
    pass
```

### TypeScript JSDoc
```typescript
/**
 * Fetch all interviews for the current user
 * 
 * @returns Promise resolving to array of interviews
 * @throws {Error} If API request fails
 * 
 * @example
 * ```typescript
 * const interviews = await fetchInterviews();
 * console.log(interviews.length);
 * ```
 */
export const fetchInterviews = async (): Promise<Interview[]> => {
  const response = await apiClient.get('/api/v1/interviews');
  return response.data;
};
```

### API Documentation
- Use FastAPI's automatic OpenAPI documentation
- Include request/response examples for all endpoints
- Document all error responses with status codes
- Provide authentication requirements

---

**Last Updated**: 2025-10-28  
**Version**: 2.0  
**Authors**: PM Agent (John), Winston (Architect)  
**Tech Stack**: Python 3.11.9 + FastAPI + React 18 + TypeScript 5.0
