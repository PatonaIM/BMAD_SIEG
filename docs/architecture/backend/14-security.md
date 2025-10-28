# Security

## Input Validation

**1. Pydantic at API Boundary:**
```python
class CreateInterviewRequest(BaseModel):
    role_type: Literal["react", "python", "javascript", "fullstack"]
    resume_id: Optional[UUID] = None
    
    @validator("role_type")
    def validate_role_type(cls, v):
        if v not in ["react", "python", "javascript", "fullstack"]:
            raise ValueError("Invalid role type")
        return v
```

**2. SQL Injection Prevention:**
```python
# ✅ SQLAlchemy ORM automatically parameterizes
result = await session.execute(
    select(Candidate).where(Candidate.email == email)
)
```

## Authentication & Authorization

**JWT Implementation:**
```python
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(user_id: UUID) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return UUID(payload["sub"])
    except JWTError:
        raise AuthenticationError("Invalid token")
```

## API Security

**1. Rate Limiting:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.client.host)

@router.post("/interviews")
@limiter.limit("10/hour")  # Max 10 interview starts per hour
async def start_interview(...):
    pass
```

**2. CORS Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://teamified.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**3. Security Headers:**
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## Data Protection

**1. Encryption at Rest:** Supabase PostgreSQL encrypts data at rest by default

**2. Encryption in Transit:** HTTPS enforced in production (nginx reverse proxy)

**3. PII Handling:**
```python
# ✅ Never log PII
logger.info("candidate_registered", candidate_id=str(candidate_id))  # ✅

# ❌ Don't log sensitive data
logger.info("candidate_registered", email=email, password=password)  # ❌
```

**4. Secrets Management:**
```python
# ✅ Load from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ❌ Never hardcode
OPENAI_API_KEY = "sk-abc123..."  # ❌ NEVER DO THIS
```

---
