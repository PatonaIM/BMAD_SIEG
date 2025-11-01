# External APIs & Services

## OpenAI API Integration

### Implementation Status
- ✅ **Whisper API (STT)**: Fully integrated in Story 1.5.1 (November 2025)
- ✅ **TTS API**: Fully integrated in Story 1.5.1 (November 2025)
- ✅ **GPT-4o-mini**: Core interview engine (Story 1.7)
- ⏳ **GPT-4**: Planned for production after MVP validation

---

**1. Whisper API (Speech-to-Text)**

**Status:** ✅ **Implemented** (Story 1.5.1)

**Endpoint:** `https://api.openai.com/v1/audio/transcriptions`

**Authentication:** Bearer token in Authorization header

**Request Format:**
```python
# multipart/form-data
{
    "file": <audio_file>,         # Audio file bytes
    "model": "whisper-1",          # Only model available
    "language": "en",              # MVP: English only, improves accuracy
    "response_format": "verbose_json",  # ✅ Returns confidence scores
    "temperature": 0               # 0 = deterministic (recommended)
}
```

**Response Format (verbose_json):**
```json
{
    "text": "Transcribed text from audio",
    "language": "en",
    "duration": 5.2,
    "segments": [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.5,
            "text": "segment text",
            "tokens": [50364, 1752, ...],
            "temperature": 0.0,
            "avg_logprob": -0.3,
            "compression_ratio": 1.5,
            "no_speech_prob": 0.02,
            "confidence": 0.95  // ✅ Per-segment confidence
        }
    ]
}
```

**Implementation Details:**
- **Provider Class:** `OpenAISpeechProvider` (implements `SpeechProvider` abstract interface)
- **Location:** `backend/app/providers/openai_speech_provider.py`
- **Service Orchestration:** `SpeechService.transcribe_candidate_audio()`
- **HTTP Client:** `httpx.AsyncClient` with 30s timeout
- **Audio Validation:** Sample rate ≥16kHz, file size <25MB, duration >0.1s
- **Metadata Storage:** Stored in `interview_messages.audio_metadata` JSONB field

**Supported Audio Formats:**
- ✅ WAV (`audio/wav`)
- ✅ MP3 (`audio/mpeg`)
- ✅ WebM (`audio/webm`) - Primary format from browser MediaRecorder
- ✅ Opus (`audio/opus`)
- ❌ M4A, MP4, MPEG, MPGA (not used in MVP)

**Rate Limits:**
- **Free tier:** 50 requests per minute (RPM)
- **File size limit:** 25 MB
- **Paid tier:** Contact OpenAI for higher limits

**Error Handling & Retry Logic:**
- **429 (Rate Limit):** Exponential backoff (1s, 2s, 4s), max 3 retries
- **500 (Server Error):** Retry with 2s delay, max 3 attempts
- **408 (Timeout):** Retry once with 5s delay
- **400 (Bad Request):** No retry, raise `AudioValidationError` immediately
  - Log audio metadata (format, size, sample rate) for debugging
- **401 (Auth Error):** No retry, raise `SpeechProviderError`, alert DevOps
- **Logging:** All API calls logged with correlation IDs for debugging

**Cost Tracking:**
- **Price:** $0.006 per minute of audio
- **Calculation:** `(duration_seconds / 60) * 0.006`
- **Storage:** `interviews.speech_cost_usd` field (Decimal, 4 decimals)
- **Utility:** `SpeechCostCalculator.calculate_stt_cost(duration_seconds)`

**Performance:**
- **Target Latency:** <2-3 seconds (OpenAI API processing time)
- **Observed Latency:** 1.5-2.5 seconds for 5-10 second audio clips
- **Future Optimization:** Azure Speech Services for real-time streaming (<500ms)

---

**2. TTS API (Text-to-Speech)**

**Status:** ✅ **Implemented** (Story 1.5.1)

**Endpoint:** `https://api.openai.com/v1/audio/speech`

**Authentication:** Bearer token in Authorization header

**Request Format:**
```python
{
    "model": "tts-1",           # ✅ Faster, sufficient quality for MVP
                                # "tts-1-hd" available for higher quality
    "input": "Text to speak",   # Max 4096 characters
    "voice": "alloy",           # ✅ MVP voice: neutral, professional
    "response_format": "mp3",   # ✅ MP3 for broad browser support
    "speed": 1.0                # ✅ Natural pace (0.25-4.0 range)
}
```

**Voice Options:**
- **alloy** ✅ - Neutral, professional (selected for MVP)
- echo - Warm, friendly
- fable - Expressive, storytelling
- onyx - Deep, authoritative
- nova - Young, energetic
- shimmer - Soft, calming

**Response:** Binary MP3 audio stream

**Implementation Details:**
- **Provider Class:** `OpenAISpeechProvider.synthesize_speech()`
- **Service Orchestration:** `SpeechService.generate_ai_speech()`
- **HTTP Client:** `httpx.AsyncClient` with 15s timeout
- **Text Validation:** Max 4096 characters (OpenAI API limit)
- **Audio Output:** MP3 format (browser-compatible)

**Rate Limits:**
- **All tiers:** 50 requests per minute (RPM)
- **Max input length:** 4096 characters per request
- **Strategy:** Queue requests if rate limit hit, process sequentially

**Error Handling:**
- **429 (Rate Limit):** Queue requests, retry after 1 minute
- **400 (Bad Request):** Truncate text to 4096 chars, log warning
- **500 (Server Error):** Retry up to 3 times with 2s delay
- **Fallback:** Return cached TTS for repeated phrases (future optimization)

**Cost Tracking:**
- **Price:** $0.015 per 1,000 characters (input text)
- **Calculation:** `(len(text) / 1000) * 0.015`
- **Storage:** `interviews.speech_tokens_used` (character count), `speech_cost_usd`
- **Utility:** `SpeechCostCalculator.calculate_tts_cost(text)`

**Performance:**
- **Target Latency:** <2-3 seconds for 100-200 character question
- **Observed Latency:** 1.5-2.5 seconds (consistent across text lengths)

**Per-Interview Cost Estimate:**
- **15 AI questions × 200 chars each:** 3,000 characters = $0.045
- **Total speech cost (STT + TTS):** ~$0.135 per interview

---

**3. GPT-4 / GPT-4o-mini API (Completions)**

**Endpoint:** `https://api.openai.com/v1/chat/completions`

**Authentication:** Bearer token in Authorization header

**Request Format:**
```python
{
    "model": "gpt-4o-mini",           # or "gpt-4" for production
    "messages": [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Previous response"}
    ],
    "temperature": 0.7,               # 0 = deterministic, 2 = creative
    "max_tokens": 1000,               # Response length limit
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

**Response Format:**
```json
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4o-mini",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "AI response text"
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 56,
        "completion_tokens": 31,
        "total_tokens": 87
    }
}
```

**Model Specifications:**

| Model | Context Window | Input Cost | Output Cost | Use Case |
|-------|---------------|------------|-------------|----------|
| GPT-4o-mini | 128K tokens | $0.150/1M | $0.600/1M | Development, MVP interviews |
| GPT-4 | 8K tokens | $30/1M | $60/1M | Production interviews (when revenue-proven) |

**Rate Limits:**
- Free tier: 3 RPM, 40K TPM (tokens per minute)
- Paid tier 1: 500 RPM, 30K TPD (tokens per day)
- Paid tier 2: 5000 RPM, 300K TPD

**Error Handling:**
- 429 (Rate Limit): Exponential backoff, queue interview requests
- 400 (Invalid Request): Log prompt, validate token count
- 401 (Auth Error): Rotate API keys if compromised
- 500 (Server Error): Retry up to 3 times with 5s delay
- Context Length Error: Truncate conversation history, keep system prompt + last 5 messages

**Token Management:**
- Track usage per interview in `Interview.total_tokens_used`
- Alert at 80% of daily token limit
- Implement token budgeting: max 10K tokens per interview

**Cost Optimization:**
- Use GPT-4o-mini for all non-critical tasks (resume parsing, feedback generation)
- Upgrade to GPT-4 only for production interviews after revenue validation
- Cache system prompts to reduce input tokens

---

## Supabase API Integration

**Database Access:** PostgreSQL via asyncpg driver (not REST API)

**Storage API (File Uploads):**

**Endpoint:** `https://{project_id}.supabase.co/storage/v1/object/{bucket_name}/{file_path}`

**Authentication:** Service role key or user JWT

**Bucket Configuration:**
- `resumes` bucket - Private, max 10MB per file, PDF/DOCX only
- `audio` bucket - Private, max 5MB per file, WebM/Opus/MP3 only
- `interview-recordings` bucket - Private, max 100MB per file, MP4/WebM video only (Story 2.8)

**Upload Example:**
```python
import httpx

async def upload_resume(file_data: bytes, candidate_id: str, filename: str):
    url = f"{SUPABASE_URL}/storage/v1/object/resumes/{candidate_id}/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/pdf"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, content=file_data, headers=headers)
        return response.json()
```

**Signed URLs for Frontend Access:**
```python
# Generate temporary download URL (expires in 1 hour)
url = f"{SUPABASE_URL}/storage/v1/object/sign/resumes/{file_path}?expiresIn=3600"
```

---

### Supabase Storage - Video Interview Recordings

**Status:** ✅ **Implemented** (Story 2.8)

**Bucket:** `interview-recordings`

**Purpose:** Store candidate video recordings from interviews for recruiter review

**Bucket Configuration:**
- **Access Type:** Private (not publicly accessible)
- **File Size Limit:** 100MB per file
- **Allowed MIME Types:** `video/mp4`, `video/webm`
- **File Path Structure:** `{organization_id}/{interview_id}/recording.mp4`
- **Encryption:** At-rest encryption enabled (Supabase default)
- **Retention:** 30 days default (configurable per organization)

**Row Level Security (RLS) Policies:**

RLS policies must be configured manually in the Supabase dashboard under Storage > interview-recordings > Policies.

1. **`authenticated_upload` Policy:**
   - **Operation:** INSERT
   - **Target Roles:** authenticated
   - **Condition:** Users can only upload to their own organization's folder
   - **Policy Expression:** `bucket_id = 'interview-recordings' AND (storage.foldername(name))[1] = auth.uid()::text`

2. **`org_member_read` Policy:**
   - **Operation:** SELECT
   - **Target Roles:** authenticated
   - **Condition:** Users can only read videos from interviews in their organization
   - **Policy Expression:** User must belong to the same organization as the interview

3. **`service_role_all` Policy:**
   - **Operation:** ALL
   - **Target Roles:** service_role
   - **Purpose:** Backend service can manage all files for cleanup and admin tasks
   - **Policy Expression:** `bucket_id = 'interview-recordings'`

**Implementation Details:**
- **Utility Class:** `SupabaseStorageClient` in `backend/app/utils/supabase_storage.py`
- **Client Library:** `supabase-py>=2.23.0`
- **Video Upload:** Chunked upload every 30 seconds during interview (HTTP POST)
- **Video Access:** Signed URLs with 24-hour expiration
- **Video Deletion:** Soft delete (mark in DB) + hard delete after 90 days

**Upload Video Example:**
```python
from app.utils.supabase_storage import SupabaseStorageClient

storage_client = SupabaseStorageClient()

# Upload video chunk
storage_path = await storage_client.upload_video_chunk(
    video_data=video_bytes,
    organization_id="org_123",
    interview_id="interview_456",
    chunk_index=0
)
# Returns: "org_123/interview_456/recording.mp4"
```

**Generate Signed URL Example:**
```python
# Generate temporary download URL (expires in 24 hours)
signed_url = await storage_client.generate_signed_url(
    storage_path="org_123/interview_456/recording.mp4",
    expires_in=86400  # 24 hours in seconds
)
# Returns: "https://xxxxx.supabase.co/storage/v1/object/sign/interview-recordings/org_123/interview_456/recording.mp4?token=..."
```

**Delete Video Example:**
```python
# Delete video from storage
success = await storage_client.delete_video(
    storage_path="org_123/interview_456/recording.mp4"
)
# Returns: True if deleted, False if not found
```

**Storage Usage Monitoring:**
```python
# Get bucket usage statistics
usage = await storage_client.get_bucket_usage()
# Returns: {
#   "total_size_bytes": 1073741824,
#   "total_size_gb": 1.0,
#   "file_count": 42
# }
```

**API Endpoints:**
- `DELETE /api/v1/videos/{interview_id}` - Soft delete video (candidate/recruiter)
- `GET /api/v1/admin/storage/usage` - Get storage usage stats (admin only)

**Environment Configuration:**
```bash
# Required in .env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key  # Optional, for RLS testing

# Video retention settings
VIDEO_RETENTION_DAYS=30           # Days before soft delete
HARD_DELETE_AFTER_DAYS=90        # Days after soft delete before permanent removal
VIDEO_STORAGE_THRESHOLD_GB=100   # Alert threshold for storage monitoring
```

**Cost Optimization:**
- **Automated Cleanup:** Daily cron job deletes expired videos (script: `backend/scripts/cleanup_videos.py`)
- **Soft Delete Pattern:** Mark videos as deleted, hard delete after 90 days
- **Storage Cost:** ~$0.021/GB/month (Supabase pricing)
- **Target Cost:** <$0.10 per 20-minute interview (~150MB at 720p)

**Error Handling:**
- **Upload failures:** Retry with exponential backoff (3 attempts)
- **Storage quota exceeded:** Log warning, alert admins
- **RLS policy violations:** Return 403 Forbidden
- **File not found:** Return 404 Not Found

**See Also:**
- Video storage implementation guide: `backend/docs/VIDEO_STORAGE.md`
- Video cleanup service: `backend/app/services/video_cleanup_service.py`
- Database schema: Story 2.0 (video_recordings table)

---

## Circuit Breaker & Retry Configuration

**Circuit Breaker Pattern (for OpenAI APIs):**

```python
class CircuitBreaker:
    failure_threshold = 5       # Open circuit after 5 consecutive failures
    timeout = 60                # Keep circuit open for 60 seconds
    half_open_max_calls = 3     # Allow 3 test calls when half-open
    
    states = ["CLOSED", "OPEN", "HALF_OPEN"]
```

**Retry Logic:**
- **Transient Errors (429, 500, 503):** Exponential backoff with jitter
  - Attempt 1: 1 second
  - Attempt 2: 2 seconds + random(0-0.5s)
  - Attempt 3: 4 seconds + random(0-1s)
  - Max attempts: 3

- **Non-Retryable Errors (400, 401, 403):** Immediate failure, log and alert

**Timeout Configuration:**
- Whisper API: 30 seconds (audio processing)
- TTS API: 20 seconds (voice synthesis)
- GPT-4 API: 45 seconds (conversation generation)
- Database queries: 10 seconds (prevent hanging)

---

## Future External Integrations (Epic 5)

**ATS/HRIS Systems:**
- Greenhouse API (REST)
- Lever API (REST)
- BambooHR API (REST)
- Workable API (REST)

**Email Services:**
- SendGrid API (transactional emails)
- AWS SES (cost-effective alternative)

**Analytics:**
- Segment (event tracking)
- Mixpanel (user behavior analysis)

---

