# Architectural Pivot: GPT-4 Realtime API

**Date**: November 1, 2025  
**Decision**: Pivot from STT+LLM+TTS pipeline to GPT-4 Realtime API for voice interviews

## Problem Statement

The original approach (Stories 1.5.3 + 1.5.4) demonstrated unacceptable latency:

```
Candidate speaks → [26 seconds] → AI responds
  ↓
  STT (1-2s) → LLM (20-24s) → TTS (2-3s)
```

**Issues:**
- 26-second response time makes real interviews impossible
- Disjointed, robotic conversation experience
- No natural interruption handling
- Complex orchestration of 3 separate API calls

## Solution: GPT-4 Realtime API

OpenAI's Realtime API provides direct speech-to-speech processing:

```
Candidate speaks → [<1 second] → AI responds
  ↓
  WebSocket bidirectional audio streaming
```

**Benefits:**
- ✅ **13x faster**: 26s → <1s latency
- ✅ **Natural flow**: Single API, continuous streaming
- ✅ **Interruption support**: True conversational turn-taking
- ✅ **Function calling**: Real-time answer evaluation
- ✅ **Simpler architecture**: 1 WebSocket vs. 3 REST calls

**Trade-offs:**
- ⚠️ **Cost**: $3.80 vs. $1.50 per 20-min interview (2.5x increase)
- ⚠️ **Beta API**: Still in preview, potential breaking changes
- ⚠️ **Complexity**: WebSocket + Web Audio API expertise required

## Impact on Stories

### Completed Stories (Remain as Fallback)
- ✅ **Story 1.5.1**: OpenAI provider abstraction (reused)
- ✅ **Story 1.5.2**: Frontend audio capture (reused for realtime)
- ✅ **Story 1.5.3**: STT pipeline → **Fallback for text mode**
- ✅ **Story 1.5.4**: TTS pipeline → **Fallback for text mode**
- ✅ **Story 1.5.5**: Voice UI components (adapted for realtime)

### New Story
- 🆕 **Story 1.5.6**: GPT-4 Realtime API Voice Integration
  - WebSocket connection management
  - Bidirectional audio streaming (PCM16 @ 24kHz)
  - Function calling for answer evaluation
  - Transcript storage alongside voice
  - Error handling and fallback to text mode
  - Mobile compatibility (iOS Safari, Android Chrome)

### Deprecated Stories
- ❌ **Story 1.5.7**: WebRTC Audio Streaming → **Not needed** (OpenAI handles streaming)

### Future Stories (Unchanged)
- **Story 1.5.8**: Audio metadata analysis
- **Story 1.5.9**: Graceful degradation (updated to include Realtime API fallback)

## Migration Strategy

### Backward Compatibility
1. **Existing code preserved**: Stories 1.5.3 & 1.5.4 code remains functional
2. **Text mode uses old pipeline**: STT → LLM → TTS for text-based interviews
3. **Feature flag**: `ENABLE_REALTIME_API=true` for gradual rollout
4. **In-progress interviews**: Continue with existing approach

### Implementation Phases

**Phase 1 (Days 1-2): Backend WebSocket**
- Create `RealtimeInterviewService`
- Implement `OpenAIRealtimeProvider`
- Create WebSocket endpoint `/api/v1/interviews/{id}/realtime/connect`
- Function calling for answer evaluation
- Transcript storage

**Phase 2 (Days 3-4): Frontend Integration**
- Create `useRealtimeInterview` hook
- Audio processing utilities (PCM16 conversion)
- Update interview store and UI
- Latency visualization

**Phase 3 (Days 5-6): Testing & Optimization**
- Interview initialization updates
- Multi-device testing
- Performance optimization
- Documentation

## Success Metrics

| Metric | Target | Current (STT+LLM+TTS) |
|--------|--------|----------------------|
| Response Latency (95th percentile) | <1s | 26s |
| Connection Stability | <1% disconnection | N/A |
| Audio Quality (transcription accuracy) | >95% | 72% (low confidence) |
| User Satisfaction | >90% prefer voice | Not measured |
| Cost per Interview | <$5 | $1.50 |

## Risk Mitigation

### HIGH RISK
- **OpenAI Beta API**: May have breaking changes
  - **Mitigation**: Keep STT/TTS fallback, monitor changelog
  
- **Mobile Audio**: WebSocket + Web Audio quirks on iOS
  - **Mitigation**: Extensive mobile testing, fallback to text

- **Latency Variability**: Network conditions impact UX
  - **Mitigation**: Performance monitoring, adaptive quality

### MEDIUM RISK
- **Cost Overrun**: 2.5x more expensive
  - **Mitigation**: Cost tracking, usage alerts, per-user limits

- **Browser Compatibility**: Older browsers may not support APIs
  - **Mitigation**: Feature detection, text mode fallback

## Decision Rationale

**Why now?**
1. Current 26s latency makes production launch impossible
2. OpenAI Realtime API solves exact problem we're facing
3. Cost increase justified by 13x speed improvement
4. Risk manageable with fallback strategy

**Why not alternatives?**
- **Streaming LLM + cached TTS**: Still 8-10s latency (not good enough)
- **WebRTC custom solution**: Too complex, doesn't solve LLM latency
- **Different LLM provider**: Same latency issues, more complexity

**Conclusion**: GPT-4 Realtime API is the right architectural choice for production-quality voice interviews.

---

**Next Steps:**
1. ✅ Story 1.5.6 document created
2. ✅ Epic 01.5 updated with new story
3. ✅ VOICE-MVP-PLAN.md updated with realtime approach
4. 📋 Begin Story 1.5.6 implementation (Backend Phase 1)

---

**References:**
- [Story 1.5.6: GPT-4 Realtime API Voice Integration](./1.5.6.gpt4-realtime-voice-integration.md)
- [Epic 01.5: Speech-to-Speech AI Interview](../epics/epic-01.5-speech.md)
- [OpenAI Realtime API Docs](https://platform.openai.com/docs/guides/realtime)
