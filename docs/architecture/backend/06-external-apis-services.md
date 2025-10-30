# External APIs & Services

## OpenAI API Integration

**1. Whisper API (Speech-to-Text)**

**Endpoint:** `https://api.openai.com/v1/audio/transcriptions`

**Authentication:** Bearer token in Authorization header

**Request Format:**
\`\`\`python
{
    "file": <audio_file>,         # multipart/form-data
    "model": "whisper-1",
    "language": "en",             # Optional, improves accuracy
    "response_format": "json",    # json, text, srt, verbose_json, vtt
    "temperature": 0              # 0 = deterministic, 0-1 = creative
}
\`\`\`

**Response Format:**
\`\`\`json
{
    "text": "Transcribed text from audio"
}
\`\`\`

**Rate Limits:**
- 50 requests per minute (RPM) for free tier
- File size limit: 25 MB
- Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm

**Error Handling:**
- 429 (Rate Limit): Exponential backoff with 1s, 2s, 4s retries
- 400 (Bad Request): Log audio metadata, alert for codec issues
- 500 (Server Error): Retry up to 3 times with 2s delay

**Cost:** $0.006 per minute of audio

---

**2. TTS API (Text-to-Speech)**

**Endpoint:** `https://api.openai.com/v1/audio/speech`

**Authentication:** Bearer token in Authorization header

**Request Format:**
\`\`\`python
{
    "model": "tts-1",           # tts-1 (faster) or tts-1-hd (higher quality)
    "input": "Text to speak",   # Max 4096 characters
    "voice": "alloy",           # alloy, echo, fable, onyx, nova, shimmer
    "response_format": "mp3",   # mp3, opus, aac, flac
    "speed": 1.0                # 0.25 to 4.0
}
\`\`\`

**Response:** Binary audio file stream

**Voice Selection for MVP:** `alloy` (neutral, professional)

**Rate Limits:**
- 50 requests per minute (RPM)
- Max input length: 4096 characters per request

**Error Handling:**
- 429 (Rate Limit): Queue requests, process sequentially
- 400 (Bad Request): Truncate text if >4096 chars
- 500 (Server Error): Return cached TTS if available, else retry

**Cost:** $0.015 per 1,000 characters (input text)

---

**3. GPT-4 / GPT-4o-mini API (Completions)**

**Endpoint:** `https://api.openai.com/v1/chat/completions`

**Authentication:** Bearer token in Authorization header

**Request Format:**
\`\`\`python
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
\`\`\`

**Response Format:**
\`\`\`json
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
\`\`\`

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

**Upload Example:**
\`\`\`python
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
\`\`\`

**Signed URLs for Frontend Access:**
\`\`\`python
# Generate temporary download URL (expires in 1 hour)
url = f"{SUPABASE_URL}/storage/v1/object/sign/resumes/{file_path}?expiresIn=3600"
\`\`\`

---

## Circuit Breaker & Retry Configuration

**Circuit Breaker Pattern (for OpenAI APIs):**

\`\`\`python
class CircuitBreaker:
    failure_threshold = 5       # Open circuit after 5 consecutive failures
    timeout = 60                # Keep circuit open for 60 seconds
    half_open_max_calls = 3     # Allow 3 test calls when half-open
    
    states = ["CLOSED", "OPEN", "HALF_OPEN"]
\`\`\`

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
