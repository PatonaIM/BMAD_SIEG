# Coding Standards

## Python Style Guide

**1. Type Hints (Required):**
\`\`\`python
# ✅ Good
async def create_interview(candidate_id: UUID, resume_id: Optional[UUID]) -> Interview:
    pass

# ❌ Bad
async def create_interview(candidate_id, resume_id):
    pass
\`\`\`

**2. Naming Conventions:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

**3. Async Everywhere:**
\`\`\`python
# ✅ All I/O operations must be async
async def get_candidate(candidate_id: UUID) -> Candidate:
    return await candidate_repo.get_by_id(candidate_id)
\`\`\`

**4. Dependency Injection:**
\`\`\`python
# ✅ Use FastAPI dependencies
@router.post("/interviews")
async def create_interview(
    candidate: Candidate = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    pass
\`\`\`

**5. Error Handling:**
\`\`\`python
# ✅ Always handle external API failures
try:
    response = await openai_provider.generate_question(context)
except OpenAIRateLimitError:
    logger.warning("rate_limit_hit", retry_after=60)
    raise HTTPException(status_code=429, detail="Please try again in 1 minute")
\`\`\`

## Critical Rules for AI Code Generation

**🚨 NEVER:**
- Use `console.log()` (Python has no console.log, use `logger.info()`)
- Store passwords in plaintext
- Expose API keys in frontend code
- Skip input validation on API endpoints
- Use `SELECT *` in queries (specify columns)

**✅ ALWAYS:**
- Use structured logging with context: `logger.info("event_name", key=value)`
- Wrap all API responses in standard format: `{"success": true, "data": {...}}`
- Use repository pattern for database access
- Validate request bodies with Pydantic schemas
- Use async/await for I/O operations

---
