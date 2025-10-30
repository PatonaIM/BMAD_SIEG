# Error Handling & Logging

## Exception Hierarchy

\`\`\`python
# app/core/exceptions.py

class TeamifiedBaseException(Exception):
    """Base exception for all custom exceptions"""
    pass

class AuthenticationError(TeamifiedBaseException):
    """Raised when authentication fails"""
    pass

class AuthorizationError(TeamifiedBaseException):
    """Raised when user lacks permission"""
    pass

class ResourceNotFoundError(TeamifiedBaseException):
    """Raised when requested resource doesn't exist"""
    pass

class ExternalAPIError(TeamifiedBaseException):
    """Raised when external API call fails"""
    pass

class OpenAIRateLimitError(ExternalAPIError):
    """Raised when OpenAI rate limit hit"""
    pass

class DataValidationError(TeamifiedBaseException):
    """Raised when data validation fails"""
    pass
\`\`\`

## Global Error Handler

\`\`\`python
# app/api/error_handlers.py

from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(TeamifiedBaseException)
async def custom_exception_handler(request: Request, exc: TeamifiedBaseException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(AuthenticationError)
async def auth_exception_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "Unauthorized", "message": str(exc)}
    )
\`\`\`

## Structured Logging

\`\`\`python
# app/core/logging.py

import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage example:
logger.info("interview_started", interview_id=str(interview_id), candidate_id=str(candidate_id))
logger.error("openai_api_failure", error=str(exc), retry_attempt=3)
\`\`\`

---
