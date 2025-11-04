# Realtime Interview Architecture - Developer Guide

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Data Flow](#data-flow)
- [Performance Optimization](#performance-optimization)
- [Debugging Tips](#debugging-tips)
- [Cost Optimization](#cost-optimization)
- [Testing Strategies](#testing-strategies)

---

## Architecture Overview

The Realtime Interview system provides low-latency voice conversations using OpenAI's Realtime API. The architecture consists of three layers:

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                        │
│  • Audio capture (MediaRecorder)                             │
│  • PCM16 conversion (AudioContext)                           │
│  • WebSocket client                                          │
│  • Audio playback (Web Audio API)                            │
└──────────────────────────────────────────────────────────────┘
                            ↕ WebSocket
┌──────────────────────────────────────────────────────────────┐
│                 Backend (FastAPI/Python)                      │
│  • WebSocket handler (JWT auth)                              │
│  • RealtimeInterviewService (session management)             │
│  • OpenAIRealtimeProvider (OpenAI WebSocket client)          │
│  • Performance monitoring                                    │
│  • Database persistence (transcripts, costs)                 │
└──────────────────────────────────────────────────────────────┘
                            ↕ WebSocket
┌──────────────────────────────────────────────────────────────┐
│              OpenAI Realtime API (External)                   │
│  • Speech-to-speech processing                               │
│  • Conversation management                                   │
│  • Function calling (answer evaluation)                      │
│  • Server VAD (voice activity detection)                     │
└──────────────────────────────────────────────────────────────┘
```

**Key Design Principles:**
1. **Low Latency:** Minimize buffering and processing delays (<1s target)
2. **Fault Tolerance:** Graceful degradation with fallback to text mode
3. **Scalability:** Stateless backend, horizontal scaling via load balancer
4. **Security:** JWT authentication, rate limiting, PII sanitization
5. **Observability:** Comprehensive logging and performance monitoring

---

## Backend Architecture

### Component Overview

```
backend/app/
├── api/v1/realtime.py                      # WebSocket endpoint
├── services/
│   ├── realtime_interview_service.py       # Session orchestration
│   └── interview_engine.py                 # Interview logic + prompts
├── providers/
│   └── openai_realtime_provider.py         # OpenAI WebSocket client
├── utils/
│   ├── realtime_cost.py                    # Cost calculation
│   └── performance_monitor.py              # Performance tracking
├── models/
│   └── interview.py                        # Database models
└── repositories/
    ├── interview.py                        # Interview data access
    ├── interview_session.py                # Session data access
    └── interview_message.py                # Message data access
```

### Key Components

#### 1. WebSocket Endpoint (`api/v1/realtime.py`)

**Responsibilities:**
- Accept WebSocket connections
- Authenticate via JWT token (query parameter)
- Rate limiting (1 connection per interview)
- Message routing (client ↔ service)
- Error handling and connection lifecycle

**Code Structure:**
```python
@router.websocket("/{interview_id}/realtime/connect")
async def realtime_connect(
    websocket: WebSocket,
    interview_id: UUID,
    token: str = Query(...),
):
    # 1. Authenticate
    user = await verify_token(token)
    
    # 2. Check permissions
    if not await has_interview_access(user, interview_id):
        await websocket.close(code=1008, reason="POLICY_VIOLATION")
        return
    
    # 3. Rate limiting
    if await is_connection_active(interview_id):
        await websocket.close(code=1008, reason="RATE_LIMIT_EXCEEDED")
        return
    
    # 4. Accept connection
    await websocket.accept()
    
    # 5. Message loop
    try:
        while True:
            message = await websocket.receive_json()
            await handle_message(message, interview_id)
    except WebSocketDisconnect:
        logger.info("connection_closed")
    finally:
        await cleanup(interview_id)
```

#### 2. RealtimeInterviewService (`services/realtime_interview_service.py`)

**Responsibilities:**
- Initialize OpenAI Realtime API session
- Manage conversation state and context
- Handle function calls from OpenAI
- Persist transcripts to database
- Track costs and usage

**Key Methods:**
```python
class RealtimeInterviewService:
    async def initialize_session(
        self,
        interview_id: UUID,
        session_id: UUID
    ) -> dict:
        """Initialize Realtime API session configuration."""
        # Load interview context (job, rubric, questions)
        # Generate system prompt
        # Return OpenAI session config
    
    async def handle_function_call(
        self,
        function_name: str,
        arguments: dict,
        interview_id: UUID
    ) -> dict:
        """Process answer evaluation function call."""
        # Evaluate candidate answer
        # Determine next question
        # Return result to OpenAI
    
    async def track_usage_and_cost(
        self,
        interview_id: UUID,
        usage: dict
    ):
        """Update interview cost based on API usage."""
        # Calculate cost from audio + text tokens
        # Update interview.realtime_cost_usd
        # Log if cost exceeds threshold
```

#### 3. OpenAIRealtimeProvider (`providers/openai_realtime_provider.py`)

**Responsibilities:**
- Establish WebSocket connection to OpenAI
- Send/receive audio chunks
- Handle OpenAI events (audio, transcript, function_call)
- Reconnection logic
- Error handling

**Key Methods:**
```python
class OpenAIRealtimeProvider:
    async def connect(self, session_config: dict):
        """Connect to OpenAI Realtime API."""
        # Create WebSocket connection
        # Send session.create event with config
    
    async def send_audio(self, audio_base64: str):
        """Send audio chunk to OpenAI."""
        # Send input_audio_buffer.append event
    
    async def commit_audio(self):
        """Signal end of audio input."""
        # Send input_audio_buffer.commit event
    
    async def listen(self, callback: Callable):
        """Listen for OpenAI events."""
        # Receive events from OpenAI
        # Parse and forward to callback
```

#### 4. PerformanceMonitor (`utils/performance_monitor.py`)

**Responsibilities:**
- Track WebSocket roundtrip times
- Monitor audio processing latency
- Track AI response latencies
- Detect performance degradation
- Log performance summaries

**Usage:**
```python
monitor = PerformanceMonitor(session_id=session_id)

# Track roundtrip time
with monitor.track_roundtrip():
    await send_websocket_message()

# Track AI response
with monitor.track_ai_response():
    await wait_for_ai_response()

# Log summary at end
monitor.log_summary()
```

### Database Schema

**interview table:**
```sql
CREATE TABLE interview (
    id UUID PRIMARY KEY,
    candidate_id UUID NOT NULL,
    job_posting_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    realtime_cost_usd NUMERIC(10, 4) DEFAULT 0.0000,  -- NEW
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

**interview_message table:**
```sql
CREATE TABLE interview_message (
    id UUID PRIMARY KEY,
    interview_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'candidate' or 'ai'
    content TEXT NOT NULL,
    message_type VARCHAR(50),  -- 'audio_transcript' for realtime
    created_at TIMESTAMP NOT NULL
);
```

---

## Frontend Architecture

### Component Overview

```
frontend/src/features/interview/
├── hooks/
│   ├── useRealtimeInterview.ts           # WebSocket hook
│   ├── useAudioCapture.ts                # Microphone capture
│   └── useAudioPlayback.ts               # Audio playback
├── utils/
│   ├── audioProcessing.ts                # PCM16 conversion
│   └── audioOptimization.ts              # Performance monitoring
├── components/
│   ├── LatencyIndicator/                 # Latency visualization
│   ├── ConnectionLostBanner/             # Error UI
│   └── AudioNotSupportedMessage/         # Browser fallback
├── store/
│   └── interviewStore.ts                 # State management
└── types/
    └── interview.types.ts                # TypeScript types
```

### Key Components

#### 1. useRealtimeInterview Hook

**Responsibilities:**
- Establish WebSocket connection
- Handle connection state
- Send/receive messages
- Reconnection with exponential backoff

**Usage:**
```typescript
const realtime = useRealtimeInterview(interviewId, authToken)

// Send audio chunk
realtime.sendAudioChunk(audioBuffer)

// Commit audio
realtime.commitAudio()

// Connection state
const { connectionState } = realtime  // 'disconnected' | 'connecting' | 'connected'
```

#### 2. useAudioCapture Hook

**Responsibilities:**
- Request microphone permission
- Capture audio via MediaRecorder
- Stream audio chunks (100ms intervals)
- Convert to PCM16 at 24kHz
- Provide audio level for visualization

**Usage:**
```typescript
const audioCapture = useAudioCapture()

// Start recording with streaming callback
await audioCapture.startRecording((chunk: ArrayBuffer) => {
  realtime.sendAudioChunk(chunk)
})

// Stop recording
audioCapture.stopRecording()

// Get audio level for visualization
const level = audioCapture.audioLevel  // 0-100
```

#### 3. Audio Processing Utilities

**PCM16 Conversion:**
```typescript
// Resample browser audio to 24kHz PCM16
const pcm16 = await resampleToPCM16(audioBuffer, 24000)

// Encode to Base64 for WebSocket
const base64Audio = encodeToBase64(pcm16)

// Decode Base64 to PCM16
const pcm16 = decodeFromBase64(base64Audio)

// Convert PCM16 to Float32 for playback
const float32 = pcm16ToFloat32(pcm16)
```

**Audio Playback Queue:**
```typescript
const queue = new AudioPlaybackQueue(24000)

// Initialize (required for mobile)
await queue.init()

// Enqueue audio chunk
await queue.enqueue(pcm16Data)

// Enqueue Base64-encoded chunk
await queue.enqueueBase64(base64Audio)

// Clear queue
queue.clear()
```

#### 4. Performance Monitoring

**Frontend Performance Monitor:**
```typescript
const monitor = new PerformanceMonitor()

// Track audio sent
monitor.recordAudioSent(audioBuffer.byteLength)

// Track AI response latency
monitor.recordAIResponse(latencyMs)

// Get performance summary
const summary = monitor.getSummary()
console.info('Performance:', summary)

// Log detailed summary
monitor.logSummary()
```

**Adaptive Buffer Management:**
```typescript
const bufferManager = new AudioBufferManager()

// Report audio glitch (buffer underrun)
bufferManager.reportGlitch()

// Report stable playback
bufferManager.reportStable()

// Get recommended buffer size
const size = bufferManager.getBufferSize()  // 2-10 chunks
```

---

## Data Flow

### Candidate Speaks → AI Responds

```
1. Frontend: Microphone → MediaRecorder (100ms chunks)
     ↓
2. Frontend: AudioContext → Resample to 24kHz → Convert to PCM16
     ↓
3. Frontend: Encode Base64 → WebSocket.send()
     ↓
4. Backend: WebSocket receives → Forward to OpenAI
     ↓
5. OpenAI: Speech-to-text → LLM reasoning → Text-to-speech
     ↓
6. Backend: Receive AI audio chunks → Forward to frontend
     ↓
7. Frontend: Decode Base64 → Convert to Float32 → AudioContext playback
     ↓
8. Frontend: Update transcript UI
```

**Latency Breakdown:**
- Audio capture + processing: ~50ms
- WebSocket roundtrip (frontend ↔ backend): ~20-50ms
- OpenAI processing: ~300-800ms (target)
- Audio playback queue: ~50-100ms
- **Total: <1000ms (1 second target)**

---

## Performance Optimization

### 1. Minimize Audio Buffering

**Problem:** Large audio buffers increase latency but prevent glitches.

**Solution:** Adaptive buffer sizing based on network conditions.

```typescript
const bufferManager = new AudioBufferManager()

// Start with 5 chunks (~500ms)
let bufferSize = bufferManager.getBufferSize()

// On audio glitch, increase buffer
audioContext.onstatechange = () => {
  if (audioContext.state === 'suspended') {
    bufferManager.reportGlitch()
  }
}

// On stable playback, decrease buffer
setInterval(() => {
  if (isPlaybackStable()) {
    bufferManager.reportStable()
  }
}, 5000)
```

### 2. Optimize Audio Resampling

**Problem:** Audio resampling can be CPU-intensive.

**Solution:** Use OfflineAudioContext for efficient resampling.

```typescript
async function resampleToPCM16(audioBuffer: AudioBuffer, targetSampleRate: number) {
  // Use OfflineAudioContext for hardware-accelerated resampling
  const offlineContext = new OfflineAudioContext(
    1, // mono
    Math.ceil(audioBuffer.duration * targetSampleRate),
    targetSampleRate
  )
  
  const source = offlineContext.createBufferSource()
  source.buffer = audioBuffer
  source.connect(offlineContext.destination)
  source.start(0)
  
  const resampledBuffer = await offlineContext.startRendering()
  return float32ToPCM16(resampledBuffer.getChannelData(0))
}
```

### 3. Backend Connection Pooling

**Problem:** Creating new OpenAI WebSocket connections is slow.

**Solution:** Maintain connection pool for faster session initialization (future optimization).

```python
# Future: Connection pool for OpenAI WebSockets
class RealtimeConnectionPool:
    def __init__(self, size: int = 10):
        self.pool: list[OpenAIRealtimeProvider] = []
        self.size = size
    
    async def acquire(self) -> OpenAIRealtimeProvider:
        if self.pool:
            return self.pool.pop()
        return OpenAIRealtimeProvider()
    
    async def release(self, provider: OpenAIRealtimeProvider):
        if len(self.pool) < self.size:
            self.pool.append(provider)
        else:
            await provider.close()
```

### 4. Bandwidth Optimization

**Monitor bandwidth usage:**
```typescript
const bandwidthMonitor = new BandwidthMonitor()

// Track uploads
bandwidthMonitor.recordSent(audioBuffer.byteLength)

// Check if bandwidth is constrained
const stats = bandwidthMonitor.getStats()
if (stats.uploadKbps < 50) {
  console.warn('Low bandwidth detected:', stats.uploadKbps, 'Kbps')
  // Consider reducing audio quality or chunk frequency
}
```

---

## Debugging Tips

### Backend Debugging

**1. Enable Debug Logging:**
```python
import structlog
logger = structlog.get_logger().bind(service="realtime_debug")

logger.debug(
    "websocket_message",
    message_type=message["type"],
    size=len(json.dumps(message)),
    latency_ms=latency
)
```

**2. Monitor WebSocket Messages:**
```python
# Log all WebSocket messages
@router.websocket("/{interview_id}/realtime/connect")
async def realtime_connect(websocket: WebSocket, interview_id: UUID):
    await websocket.accept()
    
    async for message in websocket.iter_json():
        logger.debug("ws_received", message=message)
        # Process message
        response = await process_message(message)
        logger.debug("ws_sending", response=response)
        await websocket.send_json(response)
```

**3. Check OpenAI API Status:**
```bash
# Check OpenAI API status
curl https://status.openai.com/api/v2/status.json
```

### Frontend Debugging

**1. Log WebSocket Messages:**
```typescript
const ws = new WebSocket(wsUrl)

ws.addEventListener('message', (event) => {
  const message = JSON.parse(event.data)
  console.debug('[WS Received]', message.type, message)
})

ws.addEventListener('send', (event) => {
  console.debug('[WS Sent]', JSON.parse(event.data))
})
```

**2. Visualize Audio Levels:**
```typescript
const monitor = new AudioLevelMonitor()

monitor.start(mediaStream, (level) => {
  console.debug('Audio level:', level.toFixed(1), '%')
  // Update UI with level indicator
})
```

**3. Track Performance:**
```typescript
const monitor = new PerformanceMonitor()

// Log summary every 30 seconds
setInterval(() => {
  monitor.logSummary()
}, 30000)
```

**4. Browser DevTools:**
- **Network Tab:** Check WebSocket connection status and messages
- **Performance Tab:** Profile audio processing CPU usage
- **Console:** Enable verbose logging with `localStorage.debug = '*'`

### Common Issues

**Issue: High Latency (>2 seconds)**

**Diagnosis:**
```typescript
const summary = performanceMonitor.getSummary()

if (summary.latency.p95AIMs > 2000) {
  console.error('High AI latency:', summary.latency.p95AIMs, 'ms')
  
  // Check network
  console.log('Upload bandwidth:', summary.bandwidth.uploadKbps, 'Kbps')
  console.log('Download bandwidth:', summary.bandwidth.downloadKbps, 'Kbps')
}
```

**Solutions:**
1. Check network connection quality
2. Verify OpenAI API status
3. Reduce `max_response_output_tokens` to 500
4. Check backend logs for slow processing

**Issue: Audio Glitches**

**Diagnosis:**
```typescript
const bufferManager = new AudioBufferManager()

// Track glitch count
let glitchCount = 0

audioContext.onstatechange = () => {
  if (audioContext.state === 'suspended') {
    glitchCount++
    console.warn('Audio glitch detected:', glitchCount)
    bufferManager.reportGlitch()
  }
}
```

**Solutions:**
1. Increase buffer size: `bufferManager.reportGlitch()`
2. Check CPU usage (close other tabs)
3. Verify audio format (PCM16 at 24kHz)
4. Check for network packet loss

---

## Cost Optimization

### Understanding Costs

**Realtime API Pricing:**
- Input audio: $0.06 per minute
- Output audio: $0.24 per minute
- Input text tokens: $0.01 per 1K tokens
- Output text tokens: $0.03 per 1K tokens

**Example (20-min interview):**
```
Candidate speaks 10 min: 10 × $0.06 = $0.60
AI speaks 10 min: 10 × $0.24 = $2.40
Text tokens ~20K: $0.80
Total: $3.80
```

### Optimization Strategies

**1. Reduce Max Response Tokens:**
```python
# In session config
session_config = {
    "max_response_output_tokens": 500,  # Default: 1000
    # More concise AI responses = lower cost
}
```

**2. Limit Interview Duration:**
```python
# Set maximum interview duration
MAX_INTERVIEW_DURATION = 30 * 60  # 30 minutes

if interview.duration_seconds > MAX_INTERVIEW_DURATION:
    await realtime_service.end_session(interview_id)
    logger.warning("interview_duration_exceeded", duration=interview.duration_seconds)
```

**3. Monitor Costs Per Interview:**
```python
from app.utils.realtime_cost import check_cost_threshold

# Alert if cost exceeds $5
if check_cost_threshold(realtime_cost_usd, threshold=5.0):
    logger.warning(
        "high_interview_cost",
        cost_usd=realtime_cost_usd,
        interview_id=interview_id
    )
```

**4. Optimize System Prompts:**
```python
# Keep system prompts concise
system_prompt = """You are a technical interviewer. Ask questions, 
evaluate answers, and determine next steps. Be concise."""

# Avoid verbose instructions that increase token usage
```

### Cost Tracking

**Backend Cost Calculation:**
```python
from app.utils.realtime_cost import calculate_realtime_cost

cost_usd = calculate_realtime_cost(
    input_audio_minutes=10.0,
    output_audio_minutes=10.0,
    input_tokens=8000,
    output_tokens=12000
)

# Update database
interview.realtime_cost_usd += cost_usd
await interview_repo.update(interview)
```

**Frontend Cost Estimation:**
```typescript
// Estimate cost before starting interview
const estimatedCost = estimateInterviewCost(durationMinutes=20)
console.info('Estimated cost:', estimatedCost.toFixed(2), 'USD')

// Show warning if user approaching budget limit
if (estimatedCost > remainingBudget) {
  showWarning('Estimated cost exceeds remaining budget')
}
```

---

## Testing Strategies

### Unit Testing

**Backend (pytest):**
```python
# tests/unit/test_realtime_cost.py
def test_calculate_realtime_cost_audio_only():
    """Test cost calculation with audio only."""
    cost = calculate_realtime_cost(
        input_audio_minutes=10.0,
        output_audio_minutes=10.0,
        input_tokens=0,
        output_tokens=0
    )
    
    expected = (10.0 * 0.06) + (10.0 * 0.24)
    assert cost == Decimal(str(expected))
```

**Frontend (Vitest):**
```typescript
// tests/unit/audioProcessing.test.ts
describe('resampleToPCM16', () => {
  it('resamples audio to 24kHz', async () => {
    const audioBuffer = createTestAudioBuffer(48000, 1.0)
    const pcm16 = await resampleToPCM16(audioBuffer, 24000)
    
    expect(pcm16).toBeInstanceOf(Int16Array)
    expect(pcm16.length).toBe(24000)
  })
})
```

### Integration Testing

**Backend WebSocket Testing:**
```python
# tests/integration/test_realtime_websocket.py
async def test_websocket_connection(test_client, auth_token):
    """Test WebSocket connection flow."""
    with test_client.websocket_connect(
        f"/api/v1/interviews/{interview_id}/realtime/connect?token={auth_token}"
    ) as websocket:
        # Send audio chunk
        audio_message = {
            "type": "audio_chunk",
            "audio": base64_audio,
            "timestamp": 1699999999
        }
        websocket.send_json(audio_message)
        
        # Receive response
        response = websocket.receive_json()
        assert response["type"] == "ai_audio_chunk"
```

**Frontend Integration Testing:**
```typescript
// tests/integration/realtime.test.tsx
describe('Realtime Interview', () => {
  it('connects and streams audio', async () => {
    const { result } = renderHook(() => 
      useRealtimeInterview(interviewId, authToken)
    )
    
    // Wait for connection
    await waitFor(() => {
      expect(result.current.connectionState).toBe('connected')
    })
    
    // Send audio
    const audioBuffer = new ArrayBuffer(4800)
    result.current.sendAudioChunk(audioBuffer)
    
    // Verify message sent
    expect(mockWebSocket.send).toHaveBeenCalled()
  })
})
```

### E2E Testing

**Cypress E2E Test:**
```javascript
// cypress/e2e/realtime-interview.cy.js
describe('Realtime Interview E2E', () => {
  it('completes voice interview', () => {
    cy.login('candidate@example.com', 'password')
    cy.visit('/interview/session-123')
    
    // Enable voice mode
    cy.contains('Voice Mode').click()
    
    // Wait for connection
    cy.contains('Connected', { timeout: 10000 })
    
    // Simulate speaking (mock audio input)
    cy.window().then((win) => {
      win.simulateMicrophoneInput()
    })
    
    // Verify AI response
    cy.contains('AI is speaking...', { timeout: 5000 })
    
    // Complete interview
    cy.contains('End Interview').click()
    cy.contains('Interview Complete')
  })
})
```

---

## Related Resources

**Documentation:**
- [API Reference](./REALTIME_API.md)
- [Migration Guide](./REALTIME_MIGRATION.md)
- [Story 1.5.6](./stories/1.5.6.gpt4-realtime-voice-integration.md)

**External:**
- [OpenAI Realtime API Docs](https://platform.openai.com/docs/guides/realtime)
- [WebSocket Protocol RFC](https://datatracker.ietf.org/doc/html/rfc6455)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

**Tools:**
- Backend logging: `structlog`
- Frontend monitoring: Browser DevTools
- Load testing: `locust` or `k6`
- WebSocket debugging: `wscat` CLI tool

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Maintained By:** Engineering Team