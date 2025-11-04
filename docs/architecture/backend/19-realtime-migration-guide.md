# OpenAI Realtime API Migration Guide

## Overview

This guide documents the migration from separate STT/TTS pipelines (Stories 1.5.3/1.5.4) to the unified OpenAI Realtime API for voice interviews.

**Migration Date:** November 2025 (Story 1.5.6)  
**Status:** Production-ready with fallback support  
**Feature Flag:** `ENABLE_REALTIME_API` (default: `true`)

---

## Architecture Comparison

### Legacy Approach (Stories 1.5.3 + 1.5.4)
```
Candidate Speech → Frontend Audio Upload → Backend STT (Whisper)
  ↓
Transcription → LLM (GPT-4) → AI Response Text
  ↓
TTS (OpenAI TTS) → Audio Playback → Candidate Hears Response

Total Latency: ~10-15 seconds
Cost per 20-min interview: ~$1.50
```

### New Approach (Story 1.5.6 - Realtime API)
```
Candidate Speech → WebSocket Audio Stream → OpenAI Realtime API
  ↓
Real-time Speech-to-Speech Processing
  ↓
AI Audio Response Stream → Candidate Hears Response

Total Latency: <1 second (target)
Cost per 20-min interview: ~$3.80
```

---

## Feature Flag Configuration

### Environment Variable

Add to your `.env` file:

```bash
# Enable/disable Realtime API (default: true)
ENABLE_REALTIME_API=true

# Realtime API Configuration
REALTIME_API_MODEL=gpt-4o-realtime-preview-2024-10-01
REALTIME_VOICE=alloy
REALTIME_TEMPERATURE=0.7
REALTIME_MAX_RESPONSE_TOKENS=1000
```

### Runtime Configuration

The feature flag is checked in:
- **Frontend:** Interview page detects `useRealtimeMode` from store
- **Backend:** `InterviewEngine.start_interview(use_realtime=True)` parameter
- **WebSocket:** Only available when `settings.enable_realtime_api == True`

---

## Migration Strategy

### Phase 1: Gradual Rollout (Recommended)

1. **Enable for New Interviews Only**
   ```python
   # In interview initialization
   use_realtime = settings.enable_realtime_api and interview.created_at > datetime(2025, 11, 1)
   ```

2. **Monitor Metrics**
   - Track realtime connection success rate
   - Measure actual latency (target: <1s for 95th percentile)
   - Monitor cost per interview
   - Log user feedback on voice quality

3. **Expand Gradually**
   - Week 1: 10% of users
   - Week 2: 25% of users
   - Week 3: 50% of users
   - Week 4: 100% of users (if metrics acceptable)

### Phase 2: Complete Migration

Once Realtime API is stable:
1. Set `ENABLE_REALTIME_API=true` globally
2. Keep legacy STT/TTS as fallback for errors
3. Monitor for 2 weeks
4. Consider deprecating legacy pipeline (after 6 months)

---

## Fallback Behavior

### Automatic Fallback

The system automatically falls back to STT/TTS when:
1. `ENABLE_REALTIME_API=false` in environment
2. WebSocket connection fails repeatedly (3+ attempts)
3. Browser doesn't support WebSocket or Web Audio API
4. User explicitly switches to "Text Mode" via UI

### Manual Fallback

Users can switch modes at any time:
- **Voice Mode (Realtime):** Low latency, natural conversation
- **Text Mode (Legacy):** Keyboard input, audio upload option

---

## API Endpoints

### Realtime API (New)
```
WebSocket: ws://api.yourapp.com/api/v1/interviews/{id}/realtime/connect?token={jwt}
```

**Authentication:** JWT token in query parameter  
**Protocol:** WebSocket with JSON messages  
**Audio Format:** PCM16 at 24kHz  

**Status:** Production-ready (Story 1.5.6)

### Legacy Audio Upload (Maintained)
```
POST /api/v1/interviews/{id}/audio
Content-Type: multipart/form-data
```

**Authentication:** JWT token in `Authorization` header  
**Audio Format:** WebM, MP3, WAV, etc.  
**Max File Size:** 25MB  

**Status:** Maintained as fallback

---

## Backward Compatibility

### Interview Sessions Created Before Migration

- **In-progress interviews:** Continue using legacy STT/TTS
- **Session state preserved:** `progression_state.use_realtime` flag determines mode
- **No breaking changes:** Existing audio upload endpoints unchanged

### Database Schema

New field added (non-breaking):
```sql
-- interviews table
ALTER TABLE interviews 
ADD COLUMN realtime_cost_usd NUMERIC(10, 4) DEFAULT 0.0000;
```

Existing interviews will have `realtime_cost_usd = 0.0000`.

---

## Cost Analysis

### Per-Interview Cost Comparison

| Metric | Legacy (STT/TTS) | Realtime API | Difference |
|--------|------------------|--------------|------------|
| **20-min interview** | $1.50 | $3.80 | +$2.30 (2.5x) |
| **Candidate audio** | $0.12 (STT) | $0.60 | +$0.48 |
| **AI audio** | $0.36 (TTS) | $2.40 | +$2.04 |
| **Text tokens** | $1.02 (LLM) | $0.80 | -$0.22 |

### Cost Breakdown (Realtime API)

**Formula:**
```
Cost = (Input Audio Minutes × $0.06) +
       (Output Audio Minutes × $0.24) +
       (Input Tokens / 1000 × $0.01) +
       (Output Tokens / 1000 × $0.03)
```

**Example (20-min interview):**
- Candidate speaks 10 min: 10 × $0.06 = $0.60
- AI speaks 10 min: 10 × $0.24 = $2.40
- Text tokens: ~20K = $0.80
- **Total: $3.80**

### Cost Optimization Tips

1. **Set shorter max response tokens** (default: 1000)
   ```bash
   REALTIME_MAX_RESPONSE_TOKENS=500  # More concise responses
   ```

2. **Target shorter interviews** (15-min instead of 20-min)
   ```
   15-min interview: ~$2.85 (vs. $3.80 for 20-min)
   ```

3. **Monitor per-interview alerts**
   ```python
   # Logs warning if cost exceeds $5
   if realtime_cost_usd > 5.0:
       logger.warning("high_cost_interview", cost=realtime_cost_usd)
   ```

---

## Testing & Validation

### Pre-Deployment Checklist

- [ ] Feature flag configurable via environment variable
- [ ] Existing audio upload tests still pass
- [ ] WebSocket authentication working with JWT
- [ ] Audio streaming works on desktop browsers (Chrome, Firefox, Safari)
- [ ] Audio streaming works on mobile browsers (iOS Safari, Android Chrome)
- [ ] Fallback to text mode works when WebSocket fails
- [ ] Cost tracking accurately records realtime API usage
- [ ] Session state preserved across page reloads

### Monitoring Metrics

Track these metrics in production:
- **Connection Success Rate:** Target >99%
- **Average Latency:** Target <1s for 95th percentile
- **Cost per Interview:** Target <$5 average
- **User Satisfaction:** Track feedback on voice quality
- **Fallback Rate:** Target <1% fallback to legacy mode

---

## Troubleshooting

### Issue: High Latency (>2 seconds)

**Possible Causes:**
- Network congestion
- OpenAI API performance degradation
- Audio processing bottleneck

**Solutions:**
1. Check OpenAI API status page
2. Reduce `realtime_max_response_tokens` to 500
3. Verify WebSocket connection is stable
4. Consider fallback to legacy mode temporarily

### Issue: WebSocket Connection Fails

**Possible Causes:**
- JWT token expired
- CORS configuration incorrect
- Load balancer doesn't support WebSocket
- Firewall blocking WebSocket connections

**Solutions:**
1. Verify token is valid and passed in query param
2. Check CORS allows WebSocket upgrade
3. Ensure load balancer has WebSocket support enabled
4. Test with browser developer console network tab

### Issue: High Cost Alerts

**Possible Causes:**
- Interviews running longer than expected
- AI generating verbose responses

**Solutions:**
1. Set `REALTIME_MAX_RESPONSE_TOKENS=500` (more concise)
2. Review system prompt to encourage brevity
3. Implement interview duration caps (30-min max)
4. Monitor per-question cost breakdown

---

## Deprecation Timeline

### Legacy STT/TTS Pipeline

**Current Status:** Maintained as fallback  
**Deprecation Plan:**
- **Month 0-6:** Both systems active, Realtime API default
- **Month 6-12:** Monitor Realtime API stability, prepare deprecation notice
- **Month 12+:** Deprecate legacy pipeline if Realtime API stable

**Breaking Change Notice:**
If legacy pipeline is deprecated, API clients using `POST /audio` will receive:
```json
{
  "error": "DEPRECATED",
  "message": "Please upgrade to Realtime API WebSocket connection",
  "migration_guide": "https://docs.yourapp.com/realtime-migration"
}
```

---

## Support & Resources

### Documentation
- **OpenAI Realtime API:** https://platform.openai.com/docs/guides/realtime
- **Story 1.5.6:** See `docs/stories/1.5.6.gpt4-realtime-voice-integration.md`
- **Technical Architecture:** See `docs/architecture/backend/realtime-api.md`

### Feature Flag Reference
- **Config file:** `backend/app/core/config.py`
- **Environment variable:** `ENABLE_REALTIME_API`
- **Default value:** `true` (as of Story 1.5.6)

### Contact
For questions or issues:
- **Development Team:** #eng-voice-interviews
- **OpenAI Beta Support:** https://platform.openai.com/support

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Story:** 1.5.6