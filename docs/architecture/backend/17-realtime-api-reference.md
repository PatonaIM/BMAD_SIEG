# Realtime API Documentation

## Overview

The Realtime API provides WebSocket-based voice interview functionality using OpenAI's Realtime API for low-latency, natural conversation between candidates and the AI interviewer.

**Key Features:**
- Sub-1 second response latency (target)
- Bidirectional audio streaming
- Real-time transcription
- Natural conversation flow with interruption support
- Function calling for answer evaluation

**Base URL:** `ws://localhost:8000/api/v1` (development)  
**Production URL:** `wss://api.yourapp.com/api/v1` (production)

---

## Authentication

All WebSocket connections require JWT authentication passed as a query parameter:

```
ws://localhost:8000/api/v1/interviews/{interview_id}/realtime/connect?token={jwt_token}
```

**Token Requirements:**
- Must be valid JWT token from authentication endpoint
- Token must have `candidate` role
- Token must not be expired
- Candidate must own the interview session

---

## Endpoints

### WebSocket: Realtime Interview Connection

**Endpoint:** `GET /api/v1/interviews/{interview_id}/realtime/connect`

**Protocol:** WebSocket

**Authentication:** JWT token in query parameter

**Description:** Establishes bidirectional WebSocket connection for real-time voice interview with OpenAI Realtime API.

#### Connection Request

```javascript
// JavaScript/TypeScript example
const token = localStorage.getItem('authToken')
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/interviews/${interviewId}/realtime/connect?token=${encodeURIComponent(token)}`
)

ws.onopen = () => {
  console.log('WebSocket connected')
}

ws.onmessage = (event) => {
  const message = JSON.parse(event.data)
  handleRealtimeMessage(message)
}

ws.onerror = (error) => {
  console.error('WebSocket error:', error)
}

ws.onclose = (event) => {
  console.log('WebSocket closed:', event.code, event.reason)
}
```

```python
# Python example (websockets library)
import asyncio
import websockets
import json

async def connect_realtime(interview_id: str, token: str):
    uri = f"ws://localhost:8000/api/v1/interviews/{interview_id}/realtime/connect?token={token}"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to Realtime API")
        
        # Send audio chunk
        audio_data = {
            "type": "audio_chunk",
            "audio": base64_encoded_pcm16,
            "timestamp": 1699999999
        }
        await websocket.send(json.dumps(audio_data))
        
        # Receive messages
        async for message in websocket:
            data = json.loads(message)
            handle_message(data)

asyncio.run(connect_realtime("interview-uuid", "jwt-token"))
```

#### Connection Response

**Success:**
- WebSocket upgrade successful (HTTP 101 Switching Protocols)
- Connection established

**Errors:**

| Code | Reason | Description |
|------|--------|-------------|
| 1008 | POLICY_VIOLATION | JWT token invalid or missing |
| 1008 | POLICY_VIOLATION | Candidate does not have access to interview |
| 1008 | POLICY_VIOLATION | Interview not found or not active |
| 1008 | POLICY_VIOLATION | Rate limit exceeded (max 1 connection per interview) |
| 1011 | INTERNAL_ERROR | Server error during connection |

---

## Message Protocol

### Client → Server Messages

#### 1. Audio Chunk

Send audio data to OpenAI for processing.

```json
{
  "type": "audio_chunk",
  "audio": "base64_encoded_pcm16_audio_data",
  "timestamp": 1699999999
}
```

**Fields:**
- `type`: Message type (always "audio_chunk")
- `audio`: Base64-encoded PCM16 audio at 24kHz, mono
- `timestamp`: Unix timestamp in seconds (for latency tracking)

**Audio Format:**
- Encoding: PCM16 (16-bit signed integer)
- Sample rate: 24000 Hz (24kHz)
- Channels: 1 (mono)
- Endianness: Little-endian

**Example:**
```javascript
// Convert browser audio to PCM16 and send
async function sendAudioChunk(audioBuffer) {
  const pcm16 = await resampleToPCM16(audioBuffer, 24000)
  const base64Audio = encodeToBase64(pcm16)
  
  const message = {
    type: 'audio_chunk',
    audio: base64Audio,
    timestamp: Math.floor(Date.now() / 1000)
  }
  
  ws.send(JSON.stringify(message))
}
```

#### 2. Commit Audio

Signal end of audio input (candidate finished speaking).

```json
{
  "type": "commit_audio"
}
```

**Fields:**
- `type`: Message type (always "commit_audio")

**Usage:**
```javascript
// Commit audio when candidate releases microphone button
function commitAudio() {
  const message = { type: 'commit_audio' }
  ws.send(JSON.stringify(message))
}
```

#### 3. Cancel Response

Cancel ongoing AI response (interruption).

```json
{
  "type": "cancel_response"
}
```

**Fields:**
- `type`: Message type (always "cancel_response")

---

### Server → Client Messages

#### 1. AI Audio Chunk

AI-generated audio response chunk.

```json
{
  "type": "ai_audio_chunk",
  "audio": "base64_encoded_pcm16_audio_data",
  "transcript": "partial transcript text...",
  "is_final": false
}
```

**Fields:**
- `type`: Message type (always "ai_audio_chunk")
- `audio`: Base64-encoded PCM16 audio at 24kHz, mono
- `transcript`: Partial transcript of AI speech (optional)
- `is_final`: Whether this is the final chunk of the response

**Example:**
```javascript
// Handle AI audio chunk
function handleAudioChunk(message) {
  // Decode and play audio
  const pcm16 = decodeFromBase64(message.audio)
  audioPlaybackQueue.enqueue(pcm16)
  
  // Display transcript
  if (message.transcript) {
    updateTranscript(message.transcript, message.is_final)
  }
}
```

#### 2. Transcript Update

Updated transcript of conversation.

```json
{
  "type": "transcript",
  "speaker": "candidate",
  "text": "Complete transcribed text",
  "timestamp": 1699999999
}
```

**Fields:**
- `type`: Message type (always "transcript")
- `speaker`: Speaker identifier ("candidate" or "ai")
- `text`: Complete transcribed text
- `timestamp`: Unix timestamp in seconds

#### 3. Function Call Response

Result of answer evaluation function call.

```json
{
  "type": "function_result",
  "function_name": "evaluate_candidate_answer",
  "result": {
    "answer_quality": "good",
    "next_action": "continue",
    "follow_up_needed": false,
    "score": 8
  }
}
```

**Fields:**
- `type`: Message type (always "function_result")
- `function_name`: Name of the function called
- `result`: Function execution result (structure varies by function)

#### 4. Error Message

Error occurred during processing.

```json
{
  "type": "error",
  "code": "AUDIO_PROCESSING_ERROR",
  "message": "Failed to process audio chunk",
  "details": {
    "chunk_size": 4800,
    "expected_size": 4800
  }
}
```

**Fields:**
- `type`: Message type (always "error")
- `code`: Error code (see Error Codes below)
- `message`: Human-readable error message
- `details`: Additional error context (optional)

#### 5. Session Status

Connection status update.

```json
{
  "type": "status",
  "status": "connected",
  "message": "Realtime session initialized"
}
```

**Fields:**
- `type`: Message type (always "status")
- `status`: Status code ("connecting", "connected", "disconnected")
- `message`: Human-readable status message

---

## Error Codes

### WebSocket Close Codes

| Code | Name | Description | Recovery |
|------|------|-------------|----------|
| 1000 | NORMAL_CLOSURE | Normal connection closure | No action needed |
| 1008 | POLICY_VIOLATION | Authentication or permission error | Re-authenticate and retry |
| 1011 | INTERNAL_ERROR | Server error | Retry with exponential backoff |
| 1012 | SERVICE_RESTART | Server restarting | Retry after 5 seconds |

### Message Error Codes

| Code | Description | Common Causes | Resolution |
|------|-------------|---------------|------------|
| `AUDIO_PROCESSING_ERROR` | Failed to process audio | Invalid PCM16 format, incorrect sample rate | Check audio encoding |
| `OPENAI_API_ERROR` | OpenAI API error | API outage, rate limit | Retry or fallback to text mode |
| `INVALID_MESSAGE_FORMAT` | Message format invalid | Missing required fields, wrong type | Check message schema |
| `SESSION_NOT_FOUND` | Interview session not found | Invalid interview ID | Verify interview exists |
| `RATE_LIMIT_EXCEEDED` | Too many connections | Multiple tabs open | Close other connections |

---

## Audio Format Specifications

### Input Audio (Client → Server)

**Format:** PCM16 (Linear PCM, 16-bit signed integer)  
**Sample Rate:** 24000 Hz (24kHz)  
**Channels:** 1 (mono)  
**Byte Order:** Little-endian  
**Encoding:** Base64 (for JSON transmission)

**Conversion Example (JavaScript):**
```javascript
/**
 * Convert browser AudioBuffer to PCM16 at 24kHz
 */
async function convertToPCM16(audioBuffer) {
  // Resample to 24kHz
  const offlineContext = new OfflineAudioContext(
    1, // mono
    Math.ceil(audioBuffer.duration * 24000),
    24000 // target sample rate
  )
  
  const source = offlineContext.createBufferSource()
  source.buffer = audioBuffer
  source.connect(offlineContext.destination)
  source.start(0)
  
  const resampledBuffer = await offlineContext.startRendering()
  const float32Data = resampledBuffer.getChannelData(0)
  
  // Convert Float32 to Int16 (PCM16)
  const pcm16 = new Int16Array(float32Data.length)
  for (let i = 0; i < float32Data.length; i++) {
    const sample = Math.max(-1, Math.min(1, float32Data[i]))
    pcm16[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF
  }
  
  // Encode to Base64
  const uint8Array = new Uint8Array(pcm16.buffer)
  let binary = ''
  for (let i = 0; i < uint8Array.length; i++) {
    binary += String.fromCharCode(uint8Array[i])
  }
  return btoa(binary)
}
```

### Output Audio (Server → Client)

**Format:** PCM16 (same as input)  
**Sample Rate:** 24000 Hz (24kHz)  
**Channels:** 1 (mono)  
**Encoding:** Base64

**Playback Example (JavaScript):**
```javascript
/**
 * Decode Base64 PCM16 and play using Web Audio API
 */
async function playPCM16Audio(base64Audio, audioContext) {
  // Decode Base64
  const binaryString = atob(base64Audio)
  const uint8Array = new Uint8Array(binaryString.length)
  for (let i = 0; i < binaryString.length; i++) {
    uint8Array[i] = binaryString.charCodeAt(i)
  }
  const pcm16 = new Int16Array(uint8Array.buffer)
  
  // Convert PCM16 to Float32
  const float32 = new Float32Array(pcm16.length)
  for (let i = 0; i < pcm16.length; i++) {
    float32[i] = pcm16[i] / (pcm16[i] < 0 ? 0x8000 : 0x7FFF)
  }
  
  // Create AudioBuffer and play
  const audioBuffer = audioContext.createBuffer(1, float32.length, 24000)
  audioBuffer.copyToChannel(float32, 0)
  
  const source = audioContext.createBufferSource()
  source.buffer = audioBuffer
  source.connect(audioContext.destination)
  source.start(0)
}
```

---

## Rate Limiting

**Connections:** Max 1 WebSocket connection per interview per candidate  
**Audio Chunks:** No explicit limit, but recommended max 10 chunks/second  
**Message Size:** Max 1MB per message (audio chunks should be ~100-200ms)

**Exceeded Limits:**
- Additional connections will be rejected with code 1008
- Large messages may be dropped or cause connection termination

---

## Performance Targets

| Metric | Target | Acceptable | Degraded |
|--------|--------|------------|----------|
| AI Response Latency (P95) | <500ms | <1000ms | >1000ms |
| WebSocket Roundtrip | <50ms | <200ms | >200ms |
| Audio Processing Delay | <50ms | <100ms | >100ms |
| Connection Success Rate | >99% | >95% | <95% |

**Monitoring:**
All metrics are automatically tracked and logged by the backend performance monitor. Check application logs for performance summaries.

---

## Code Examples

### Complete Client Example (TypeScript/React)

```typescript
import { useEffect, useRef, useState } from 'react'

export function useRealtimeInterview(interviewId: string, token: string) {
  const [connectionState, setConnectionState] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected')
  const ws = useRef<WebSocket | null>(null)
  const audioQueue = useRef<AudioPlaybackQueue>(new AudioPlaybackQueue())
  
  useEffect(() => {
    // Connect to WebSocket
    const wsUrl = `ws://localhost:8000/api/v1/interviews/${interviewId}/realtime/connect?token=${encodeURIComponent(token)}`
    ws.current = new WebSocket(wsUrl)
    setConnectionState('connecting')
    
    ws.current.onopen = () => {
      console.log('Realtime connection established')
      setConnectionState('connected')
    }
    
    ws.current.onmessage = async (event) => {
      const message = JSON.parse(event.data)
      
      if (message.type === 'ai_audio_chunk') {
        // Play AI audio
        await audioQueue.current.enqueueBase64(message.audio)
        
        // Update transcript
        if (message.transcript) {
          updateTranscript('ai', message.transcript, message.is_final)
        }
      } else if (message.type === 'transcript') {
        updateTranscript(message.speaker, message.text, true)
      } else if (message.type === 'error') {
        console.error('Realtime error:', message.message)
      }
    }
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    ws.current.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      setConnectionState('disconnected')
    }
    
    // Cleanup
    return () => {
      ws.current?.close()
      audioQueue.current.close()
    }
  }, [interviewId, token])
  
  const sendAudioChunk = (audioData: ArrayBuffer) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      const base64Audio = arrayBufferToBase64(audioData)
      const message = {
        type: 'audio_chunk',
        audio: base64Audio,
        timestamp: Math.floor(Date.now() / 1000)
      }
      ws.current.send(JSON.stringify(message))
    }
  }
  
  const commitAudio = () => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'commit_audio' }))
    }
  }
  
  return {
    connectionState,
    sendAudioChunk,
    commitAudio,
  }
}
```

### Complete Server Example (Python/FastAPI)

```python
from fastapi import WebSocket, WebSocketDisconnect, Depends
from uuid import UUID

@router.websocket("/{interview_id}/realtime/connect")
async def realtime_connect(
    websocket: WebSocket,
    interview_id: UUID,
    token: str = Query(...),
    realtime_service: RealtimeInterviewService = Depends(get_realtime_service),
):
    """
    WebSocket endpoint for OpenAI Realtime API voice interviews.
    """
    try:
        # Authenticate
        user = await verify_token(token)
        if user.role != "candidate":
            await websocket.close(code=1008, reason="POLICY_VIOLATION")
            return
        
        # Accept connection
        await websocket.accept()
        logger.info("realtime_websocket_connected", interview_id=interview_id)
        
        # Initialize session
        config = await realtime_service.initialize_session(interview_id, session_id)
        
        # Message loop
        while True:
            message = await websocket.receive_json()
            
            if message["type"] == "audio_chunk":
                # Forward audio to OpenAI
                await realtime_service.process_audio_chunk(
                    interview_id,
                    message["audio"]
                )
            elif message["type"] == "commit_audio":
                # Signal end of input
                await realtime_service.commit_audio(interview_id)
                
    except WebSocketDisconnect:
        logger.info("realtime_websocket_disconnected", interview_id=interview_id)
    except Exception as e:
        logger.error("realtime_websocket_error", error=str(e))
        await websocket.close(code=1011, reason="INTERNAL_ERROR")
```

---

## Debugging

### Common Issues

**1. Audio Not Playing**
- **Check:** Browser autoplay policy - call `audioContext.resume()` after user interaction
- **Check:** Audio format is PCM16 at 24kHz
- **Check:** Base64 decoding is correct

**2. High Latency**
- **Check:** Network connection quality (use browser DevTools)
- **Check:** OpenAI API status page
- **Check:** Backend performance logs for slow processing
- **Solution:** Reduce `max_response_output_tokens` in session config

**3. Connection Drops**
- **Check:** JWT token expiration
- **Check:** Network stability
- **Check:** Multiple tabs/windows open (rate limit)
- **Solution:** Implement reconnection logic with exponential backoff

**4. Poor Audio Quality**
- **Check:** Microphone input level (too low or clipping)
- **Check:** Audio resampling quality
- **Check:** Network packet loss
- **Solution:** Adjust microphone gain, use higher quality resampling

### Debug Logging

**Backend:**
```python
import structlog
logger = structlog.get_logger().bind(service="realtime")

# Enable debug logging
logger.debug("audio_chunk_received", size=len(audio_data), format="pcm16")
```

**Frontend:**
```javascript
// Log WebSocket messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data)
  console.debug('[Realtime WS]', message.type, message)
  handleMessage(message)
}
```

---

## Related Documentation

- **Migration Guide:** `docs/REALTIME_MIGRATION.md`
- **Backend Architecture:** `docs/architecture/backend/realtime-api.md`
- **Frontend Integration:** `frontend/src/features/interview/README.md`
- **OpenAI Realtime API:** https://platform.openai.com/docs/guides/realtime
- **WebSocket Protocol:** https://datatracker.ietf.org/doc/html/rfc6455

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Story:** 1.5.6