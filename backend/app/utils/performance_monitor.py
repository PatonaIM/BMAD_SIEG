"""Performance monitoring utilities for Realtime API WebSocket connections."""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generator
from uuid import UUID

import structlog

logger = structlog.get_logger().bind(service="performance_monitor")


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    
    # WebSocket metrics
    websocket_message_count: int = 0
    websocket_roundtrip_ms: list[float] = field(default_factory=list)
    websocket_errors: int = 0
    
    # Audio processing metrics
    audio_chunks_sent: int = 0
    audio_chunks_received: int = 0
    audio_processing_ms: list[float] = field(default_factory=list)
    audio_bytes_sent: int = 0
    audio_bytes_received: int = 0
    
    # Memory metrics
    peak_memory_mb: float = 0.0
    current_memory_mb: float = 0.0
    
    # Response latency
    ai_response_latencies_ms: list[float] = field(default_factory=list)
    
    # Session metadata
    session_id: UUID | None = None
    start_time: datetime = field(default_factory=datetime.now)
    
    def add_roundtrip_time(self, ms: float) -> None:
        """Record WebSocket roundtrip time."""
        self.websocket_roundtrip_ms.append(ms)
        self.websocket_message_count += 1
    
    def add_audio_processing_time(self, ms: float) -> None:
        """Record audio processing time."""
        self.audio_processing_ms.append(ms)
    
    def add_ai_response_latency(self, ms: float) -> None:
        """Record AI response latency."""
        self.ai_response_latencies_ms.append(ms)
    
    def increment_audio_sent(self, bytes_count: int) -> None:
        """Increment audio sent metrics."""
        self.audio_chunks_sent += 1
        self.audio_bytes_sent += bytes_count
    
    def increment_audio_received(self, bytes_count: int) -> None:
        """Increment audio received metrics."""
        self.audio_chunks_received += 1
        self.audio_bytes_received += bytes_count
    
    def get_average_roundtrip_ms(self) -> float | None:
        """Calculate average WebSocket roundtrip time."""
        if not self.websocket_roundtrip_ms:
            return None
        return sum(self.websocket_roundtrip_ms) / len(self.websocket_roundtrip_ms)
    
    def get_p95_roundtrip_ms(self) -> float | None:
        """Calculate 95th percentile WebSocket roundtrip time."""
        if not self.websocket_roundtrip_ms:
            return None
        sorted_times = sorted(self.websocket_roundtrip_ms)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx]
    
    def get_average_ai_latency_ms(self) -> float | None:
        """Calculate average AI response latency."""
        if not self.ai_response_latencies_ms:
            return None
        return sum(self.ai_response_latencies_ms) / len(self.ai_response_latencies_ms)
    
    def get_p95_ai_latency_ms(self) -> float | None:
        """Calculate 95th percentile AI response latency."""
        if not self.ai_response_latencies_ms:
            return None
        sorted_times = sorted(self.ai_response_latencies_ms)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for logging."""
        return {
            "session_id": str(self.session_id) if self.session_id else None,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "websocket": {
                "message_count": self.websocket_message_count,
                "average_roundtrip_ms": self.get_average_roundtrip_ms(),
                "p95_roundtrip_ms": self.get_p95_roundtrip_ms(),
                "errors": self.websocket_errors,
            },
            "audio": {
                "chunks_sent": self.audio_chunks_sent,
                "chunks_received": self.audio_chunks_received,
                "bytes_sent": self.audio_bytes_sent,
                "bytes_received": self.audio_bytes_received,
                "average_processing_ms": (
                    sum(self.audio_processing_ms) / len(self.audio_processing_ms)
                    if self.audio_processing_ms else None
                ),
            },
            "ai_response": {
                "average_latency_ms": self.get_average_ai_latency_ms(),
                "p95_latency_ms": self.get_p95_ai_latency_ms(),
                "count": len(self.ai_response_latencies_ms),
            },
            "memory": {
                "peak_mb": self.peak_memory_mb,
                "current_mb": self.current_memory_mb,
            },
        }


class PerformanceMonitor:
    """
    Performance monitor for Realtime API WebSocket connections.
    
    Tracks and logs performance metrics including:
    - WebSocket message roundtrip times
    - Audio processing latency
    - AI response latency
    - Memory usage
    - Network bandwidth
    
    Usage:
    ------
    >>> monitor = PerformanceMonitor(session_id=session_id)
    >>> 
    >>> # Track WebSocket roundtrip
    >>> with monitor.track_roundtrip():
    ...     await send_websocket_message()
    >>> 
    >>> # Track audio processing
    >>> with monitor.track_audio_processing():
    ...     process_audio_chunk(data)
    >>> 
    >>> # Log metrics at end of session
    >>> monitor.log_summary()
    """
    
    def __init__(self, session_id: UUID | None = None):
        """Initialize performance monitor."""
        self.metrics = PerformanceMetrics(session_id=session_id)
        self.logger = logger.bind(session_id=str(session_id) if session_id else None)
    
    @contextmanager
    def track_roundtrip(self) -> Generator[None, None, None]:
        """Context manager to track WebSocket roundtrip time."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.add_roundtrip_time(elapsed_ms)
            
            # Log warning if roundtrip is slow
            if elapsed_ms > 500:
                self.logger.warning(
                    "slow_websocket_roundtrip",
                    roundtrip_ms=elapsed_ms,
                    threshold_ms=500,
                )
    
    @contextmanager
    def track_audio_processing(self) -> Generator[None, None, None]:
        """Context manager to track audio processing time."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.add_audio_processing_time(elapsed_ms)
            
            # Log warning if processing is slow
            if elapsed_ms > 100:
                self.logger.warning(
                    "slow_audio_processing",
                    processing_ms=elapsed_ms,
                    threshold_ms=100,
                )
    
    @contextmanager
    def track_ai_response(self) -> Generator[None, None, None]:
        """Context manager to track AI response latency."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.add_ai_response_latency(elapsed_ms)
            
            # Log metrics for monitoring
            avg_latency = self.metrics.get_average_ai_latency_ms()
            p95_latency = self.metrics.get_p95_ai_latency_ms()
            
            self.logger.info(
                "ai_response_received",
                latency_ms=elapsed_ms,
                average_latency_ms=avg_latency,
                p95_latency_ms=p95_latency,
            )
            
            # Alert if latency exceeds target (<1s)
            if elapsed_ms > 1000:
                self.logger.warning(
                    "high_ai_response_latency",
                    latency_ms=elapsed_ms,
                    target_ms=1000,
                    average_ms=avg_latency,
                    p95_ms=p95_latency,
                )
    
    def record_audio_sent(self, bytes_count: int) -> None:
        """Record audio chunk sent to OpenAI."""
        self.metrics.increment_audio_sent(bytes_count)
    
    def record_audio_received(self, bytes_count: int) -> None:
        """Record audio chunk received from OpenAI."""
        self.metrics.increment_audio_received(bytes_count)
    
    def record_websocket_error(self) -> None:
        """Record WebSocket error."""
        self.metrics.websocket_errors += 1
        
        if self.metrics.websocket_errors >= 3:
            self.logger.error(
                "multiple_websocket_errors",
                error_count=self.metrics.websocket_errors,
            )
    
    def check_performance_degradation(self) -> bool:
        """
        Check if performance has degraded below acceptable thresholds.
        
        Returns:
            True if performance is degraded, False otherwise
        """
        avg_latency = self.metrics.get_average_ai_latency_ms()
        p95_latency = self.metrics.get_p95_ai_latency_ms()
        
        # Check AI response latency target (<1s for 95th percentile)
        if p95_latency and p95_latency > 1000:
            self.logger.warning(
                "performance_degradation_detected",
                reason="high_ai_latency",
                p95_latency_ms=p95_latency,
                target_ms=1000,
            )
            return True
        
        # Check WebSocket roundtrip time
        p95_roundtrip = self.metrics.get_p95_roundtrip_ms()
        if p95_roundtrip and p95_roundtrip > 200:
            self.logger.warning(
                "performance_degradation_detected",
                reason="high_roundtrip_time",
                p95_roundtrip_ms=p95_roundtrip,
                target_ms=200,
            )
            return True
        
        # Check error rate
        if self.metrics.websocket_errors >= 5:
            self.logger.warning(
                "performance_degradation_detected",
                reason="high_error_rate",
                errors=self.metrics.websocket_errors,
            )
            return True
        
        return False
    
    def log_summary(self) -> None:
        """Log performance metrics summary."""
        metrics_dict = self.metrics.to_dict()
        
        self.logger.info(
            "realtime_session_performance_summary",
            metrics=metrics_dict,
        )
        
        # Check for performance issues
        if self.check_performance_degradation():
            self.logger.warning(
                "performance_degradation_summary",
                metrics=metrics_dict,
            )
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        return self.metrics
