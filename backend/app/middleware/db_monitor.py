"""Database connection monitoring middleware."""
import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import get_pool_status

logger = structlog.get_logger()


class DatabaseMonitorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor database connection pool usage.
    
    Logs warnings when pool utilization is high and tracks connection patterns.
    """
    
    def __init__(self, app, check_interval: int = 10):
        """
        Initialize middleware.
        
        Args:
            app: FastAPI application instance
            check_interval: Number of requests between pool checks
        """
        super().__init__(app)
        self.request_count = 0
        self.check_interval = check_interval
        self.last_warning_time = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and monitor pool status."""
        start_time = time.time()
        
        # Check pool status periodically
        self.request_count += 1
        if self.request_count % self.check_interval == 0:
            try:
                pool_stats = await get_pool_status()
                max_conn = pool_stats["size"] + pool_stats["overflow"]
                utilization = pool_stats["checked_out"] / max_conn if max_conn > 0 else 0
                
                # Warn if utilization is high (>80%)
                if utilization > 0.8:
                    current_time = time.time()
                    # Only log warning once per minute to avoid spam
                    if current_time - self.last_warning_time > 60:
                        logger.warning(
                            "high_db_pool_utilization",
                            utilization=f"{utilization*100:.1f}%",
                            checked_out=pool_stats["checked_out"],
                            max_connections=max_conn,
                            message="Database connection pool is near capacity"
                        )
                        self.last_warning_time = current_time
            except Exception as e:
                logger.error("pool_monitoring_error", error=str(e))
        
        # Process request
        response = await call_next(request)
        
        # Log slow requests that might be holding connections
        request_time = time.time() - start_time
        if request_time > 5.0:  # More than 5 seconds
            logger.warning(
                "slow_request",
                path=request.url.path,
                method=request.method,
                duration_seconds=round(request_time, 2),
                message="Long-running request may be holding database connection"
            )
        
        return response
