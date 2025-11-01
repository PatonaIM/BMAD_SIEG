# Voice Interview MVP - Realtime API Plan

**Goal**: Implement GPT-4 Realtime API for natural voice conversations with <1 second latency

## Status: ⚠️ ARCHITECTURAL PIVOT - Realtime API Approach

### Why the Change?
**Problem with Original Plan (Stories 1.5.3 + 1.5.4):**
- 26 second response latency (STT → LLM → TTS pipeline)
- Unusable for real-time conversations
- Disjointed, robotic experience

**New Solution (Story 1.5.6):**
- GPT-4 Realtime API: Direct speech-to-speech
- <1 second latency (13x faster)
- Natural conversation flow with interruption support

## What's Already Complete ✅

### Backend (Partial - Will Use as Fallback)
- ✅ Story 1.5.1: OpenAI Whisper (STT) + TTS integration
- ✅ Story 1.5.3: Audio processing endpoint (`POST /interviews/{id}/audio`)
- ✅ Story 1.5.4: TTS generation endpoint (`GET /interviews/{id}/audio/{message_id}`)
- **Note**: These remain as fallback for text mode

### Frontend Audio Capture (Completed)
- ✅ Story 1.5.2: Frontend audio capture with push-to-talk
- ✅ Story 1.5.5: Voice interview UI with state indicators

### Foundation (100% Done)
- ✅ Stories 1.1-1.4: Infrastructure, database, auth, OpenAI
- ✅ Stories 1.6-1.8: Text-based interview UI and completion flow

## What We Need to Build 🚧 (Story 1.5.6)

### Phase 1: Backend WebSocket & Realtime API (Days 1-2)
**File**: `docs/stories/1.5.6.gpt4-realtime-voice-integration.md`

**Backend Tasks**:
1. Create `RealtimeInterviewService` - WebSocket lifecycle management
2. Implement `OpenAIRealtimeProvider` - WebSocket client to OpenAI
3. Define function schema for `evaluate_candidate_answer`
4. Create WebSocket API endpoint (`/api/v1/interviews/{id}/realtime/connect`)
5. Implement transcript storage with real-time updates
6. Add cost tracking for Realtime API usage
7. Backend integration tests

**Key Files**:
- `backend/app/services/realtime_interview_service.py`
- `backend/app/providers/openai_realtime_provider.py`
- `backend/app/api/v1/realtime.py`

**Effort**: 16-20 hours

---

### Phase 2: Frontend WebSocket & Audio Processing (Days 3-4)
**File**: `docs/stories/1.5.6.gpt4-realtime-voice-integration.md`

**Frontend Tasks**:
1. Create `useRealtimeInterview` hook - WebSocket connection management
2. Implement audio processing utilities (PCM16 conversion at 24kHz)
3. Update interview store for realtime state management
4. Update interview page UI with realtime integration
5. Add latency visualization component
6. Frontend integration tests

**Key Files**:
- `frontend/src/features/interview/hooks/useRealtimeInterview.ts`
- `frontend/src/features/interview/utils/audioProcessing.ts`
- `frontend/src/features/interview/components/LatencyIndicator.tsx`

**Effort**: 16-20 hours

---

### Phase 3: Integration, Testing & Optimization (Days 5-6)
**Tasks**:
1. Update `InterviewEngine.start_interview()` for realtime mode
2. Implement migration strategy (keep STT/TTS as fallback)
3. End-to-end testing of complete realtime flow
4. Multi-device testing (desktop + mobile)
5. Performance optimization (audio buffering, latency)
6. Documentation & deployment prep

**Effort**: 16-20 hours

**Total Estimated Effort**: 5-6 days (40-48 hours)

---

## Architecture Overview (GPT-4 Realtime API)

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
├─────────────────────────────────────────────────────────────┤
│  Browser Microphone → MediaRecorder (PCM16 @ 24kHz)        │
│         ↓                                                    │
│  WebSocket Client ←→ Backend WebSocket Handler              │
│         ↓                                                    │
│  Audio Playback ← Streaming AI Audio (<1s latency)         │
└─────────────────────────────────────────────────────────────┘
                            ↕ WebSocket
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  WebSocket Handler → RealtimeInterviewService               │
│         ↓                                                    │
│  OpenAI Realtime API ←→ Function Calls (Answer Eval)        │
│         ↓                                                    │
│  Transcript Storage → Database                               │
└─────────────────────────────────────────────────────────────┘
                            ↕ WebSocket
┌─────────────────────────────────────────────────────────────┐
│                  OpenAI Realtime API                         │
│  • Speech-to-speech processing                               │
│  • GPT-4 conversation management                             │
│  • Function calling for answer evaluation                    │
└─────────────────────────────────────────────────────────────┘
```

**Key Differences from Original Plan:**
- ❌ Removed: Separate STT → LLM → TTS pipeline
- ✅ Added: Single WebSocket connection for bidirectional audio
- ✅ Added: Function calling for real-time answer evaluation
- ✅ Result: 26s → <1s latency (13x improvement)

## Performance Comparison

| Metric | Original (STT+LLM+TTS) | Realtime API |
|--------|------------------------|--------------|
| Response Latency | 26 seconds | <1 second |
| API Calls per Exchange | 3 (STT, LLM, TTS) | 1 (WebSocket) |
| Conversation Feel | Robotic, disjointed | Natural, flowing |
| Interruption Support | ❌ No | ✅ Yes |
| Cost per 20-min Interview | ~$1.50 | ~$3.80 |

**Trade-off**: 2.5x cost increase for 13x speed improvement - worth it for production-quality UX.

## Technical Decisions Made

### Audio Format
- **Format**: PCM16 at 24kHz (OpenAI Realtime API requirement)
- **Transport**: Base64-encoded over WebSocket
- **Fallback**: Text-only mode via Stories 1.5.3/1.5.4

### UX Pattern
- **Continuous streaming** (not push-to-talk for realtime mode)
- **Voice Activity Detection** (server-side VAD by OpenAI)
- **Text transcript** always visible (accessibility + trust)
- **Mode toggle** for safety valve (voice ↔ text)

### State Management
- Simple state machine: 4 states, clear transitions
- Zustand store for client state
- React Query for server state

## Success Criteria

### MVP is "Done" When:
- [ ] Candidate can start interview in voice mode
- [ ] Candidate can record answer via push-to-talk button
- [ ] Audio transcribed to text via backend
- [ ] AI generates response with audio
- [ ] AI audio plays automatically
- [ ] Interview completes successfully
- [ ] Works in Chrome, Safari, Firefox
- [ ] Works on mobile (iOS Safari, Android Chrome)

### Quality Bar:
- Audio capture → transcription: < 3 seconds
- TTS generation → playback: < 3 seconds  
- 95%+ success rate (excluding denied permissions)
- Zero unhandled errors

## Features Explicitly Deferred

These are intentionally skipped for MVP speed:

### Audio Features
- ❌ Volume controls
- ❌ Replay button
- ❌ Audio visualization (waveform, volume meter)
- ❌ Voice-activated mode (auto-detect speech)
- ❌ Real-time audio streaming
- ❌ Noise cancellation

### UI Polish
- ❌ AI avatar or animation
- ❌ Sound effects
- ❌ Advanced animations
- ❌ Progress bars during audio playback

### Advanced Features
- ❌ Hybrid mode (voice + text for code)
- ❌ Multi-language support
- ❌ Audio quality analysis
- ❌ WebRTC streaming

**Rationale**: Get basic voice working FAST, then iterate based on user feedback

## Next Steps

1. **Today**: Review stories 1.5.2 and 1.5.5 with team
2. **Tomorrow**: Start Story 1.5.2 (audio capture)
3. **Day 2**: Complete Story 1.5.5 (voice UI)
4. **Day 3**: Integration testing + demo
5. **Day 4+**: User testing + iteration

## Questions to Resolve

- [ ] Do we need audio visualization? (Deferred for now)
- [ ] Should we support Safari on older iOS versions? (14+ only for MVP)
- [ ] What's the fallback if TTS fails? (Show text-only, log error)
- [ ] Should candidates be able to edit transcription? (Yes, before submit)

---

**Created**: November 1, 2025  
**Status**: Ready for Development  
**Estimated Completion**: November 4, 2025 (3 days)
