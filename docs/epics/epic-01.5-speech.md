# Epic 1.5: Speech-to-Speech AI Interview Capability

**Epic Goal:** Transform the text-based interview system into a natural voice-driven experience by integrating OpenAI speech services (Whisper STT + TTS API) for speech-to-text and text-to-speech capabilities. By epic completion, candidates can speak their answers naturally while the AI responds with voice, creating an engaging conversational interview. The system maintains hybrid mode support (speak answers, type code) and gracefully degrades to text-only if speech services fail. The backend processes all audio to secure API keys and enable future provider migration. This epic delivers the "wow factor" that differentiates Teamified from competitors.

## Story 1.5.1: OpenAI Speech Services Integration (Backend-Processed)

**As a** developer,  
**I want** OpenAI Whisper (STT) and TTS API integrated with provider abstraction layer,  
**so that** the system can capture candidate speech, generate AI voice responses, and support future migration to Azure/GCP alternatives.

**Acceptance Criteria:**

1. OpenAI API keys configured in environment variables (backend only, never exposed to frontend)
2. Provider abstraction layer implemented with `SpeechProvider` interface for future Azure/GCP support
3. OpenAI Whisper API integrated for speech-to-text with support for audio file uploads
4. OpenAI TTS API integrated with neural voice selection (`alloy` voice for professional tone)
5. Backend audio processing pipeline ensures API key security and consistent audio quality
6. Audio format handling implemented (support for common formats: WAV, MP3, WebM, Opus)
7. Error handling for OpenAI API failures with fallback to text-only mode
8. Cost tracking implemented for speech service usage ($0.006/min STT, $0.015/1K chars TTS)

## Story 1.5.2: Real-Time Audio Capture - Frontend

**As a** candidate,  
**I want** to speak my answers using my microphone,  
**so that** I can respond naturally without typing.

**Acceptance Criteria:**

1. Microphone permission request implemented with clear explanation to candidate
2. MediaRecorder API integrated for audio capture from browser
3. Real-time audio visualization displays voice level (volume meter)
4. Push-to-talk button implemented (hold to speak, release to submit)
5. Voice-activated mode implemented (automatic speech detection, stops after silence)
6. Audio recording state management (idle, recording, processing, error)
7. Visual feedback shows recording state (microphone icon changes, pulsing animation)
8. Audio chunks streamed to backend for processing (not waiting for complete answer)

## Story 1.5.3: Speech-to-Text Processing Pipeline

**As a** developer,  
**I want** candidate speech converted to text in real-time,  
**so that** the AI can analyze responses and generate follow-up questions.

**Acceptance Criteria:**

1. Backend endpoint accepts audio stream chunks (`POST /api/v1/interviews/{id}/audio`)
2. OpenAI Whisper API processes audio and returns transcribed text
3. Speech processing completes within 2-3 seconds of audio completion (OpenAI API latency)
4. Transcribed text stored in interview_messages table with audio metadata
5. Audio metadata includes Whisper confidence scores and processing timestamps
6. Language detection and validation (English for MVP)
7. Error handling gracefully manages poor audio quality or silence
8. Future: Real-time streaming can be added via Azure/GCP when latency becomes critical

## Story 1.5.4: Text-to-Speech AI Response Generation

**As a** candidate,  
**I want** to hear the AI interviewer's questions spoken aloud,  
**so that** the interview feels like a natural conversation.

**Acceptance Criteria:**

1. AI-generated questions converted to speech using OpenAI TTS API
2. Neural voice (`alloy`) used for natural, engaging speech quality
3. Speech generation completes within 2-3 seconds (OpenAI API processing time)
4. Audio file (MP3) returned to frontend for playback
5. Speech rate optimized for interview context (clear, professional pace)
6. Technical terms and acronyms pronounced correctly by default (React, API, JavaScript)
7. Audio caching implemented for repeated phrases to reduce costs ($0.015/1K chars)
8. Backend endpoint serves generated audio (`GET /api/v1/interviews/{id}/audio/{message_id}`)

## Story 1.5.5: Voice-Based Interview UI Enhancement

**As a** candidate,  
**I want** an intuitive voice interview interface with clear visual feedback,  
**so that** I understand when to speak and when the AI is responding.

**Acceptance Criteria:**

1. Interview screen updated with prominent microphone controls
2. Visual states clearly differentiate: AI Speaking, AI Listening, Candidate Speaking, Processing
3. AI speech plays automatically through browser audio
4. Text transcript displays alongside voice (AI questions and candidate responses shown as text)
5. Volume controls allow candidate to adjust AI voice level
6. Replay button allows candidate to rehear last AI question
7. "Switch to Text Mode" button available for fallback preference
8. Loading/processing indicators show when audio is being transcribed or generated

## Story 1.5.6: Hybrid Input Mode - Voice + Text

**As a** candidate,  
**I want** to speak my answers but type code examples when needed,  
**so that** I can communicate complex technical details effectively.

**Acceptance Criteria:**

1. Text input area remains available during voice interview
2. Mode toggle button switches between voice-only and hybrid mode
3. Candidate can speak answer, then type code snippet before submitting
4. AI recognizes when candidate says "let me type this" or similar phrases
5. Interview flow seamlessly handles mixed voice and text responses
6. Transcript clearly indicates which parts were spoken vs typed
7. Text responses processed through same AI analysis pipeline
8. Hybrid responses stored with clear delineation (speech_part, text_part)

## Story 1.5.7: WebRTC Audio Streaming Setup

**As a** developer,  
**I want** low-latency audio streaming using WebRTC,  
**so that** voice conversations feel natural without noticeable delays.

**Acceptance Criteria:**

1. WebRTC peer connection established between frontend and backend
2. Audio streams transmitted with sub-200ms latency (per NFR18)
3. Audio quality maintains 16kHz sample rate minimum (per NFR19)
4. Network adaptation handles varying bandwidth conditions
5. Reconnection logic implemented for dropped connections
6. Audio buffer management prevents choppy playback
7. Real-time metrics monitor latency and audio quality
8. Fallback to HTTP-based audio transfer if WebRTC fails

## Story 1.5.8: Audio Metadata Analysis for Integrity Monitoring

**As a** developer,  
**I want** to capture audio metadata and timing patterns for integrity analysis,  
**so that** the system can detect hesitation, confidence levels, and potential cheating indicators.

**Acceptance Criteria:**

1. Audio metadata captured from Whisper API (confidence scores, word-level timestamps)
2. Response timing tracked (time from question completion to speech start)
3. Audio duration and processing metrics stored for pattern analysis
4. Speech pattern data stored in JSONB column for later integrity analysis (Epic 3)
5. Unusual patterns flagged (suspiciously fast responses, unusual pauses)
6. Metrics available for Epic 3 integrity monitoring features
7. Privacy-conscious: audio files can be deleted post-transcription per GDPR
8. Future: Advanced prosody analysis (pitch, pace) can be added via Azure/GCP if needed

## Story 1.5.9: Graceful Degradation & Fallback Handling

**As a** candidate,  
**I want** the interview to continue even if speech features fail,  
**so that** technical issues don't prevent me from completing my assessment.

**Acceptance Criteria:**

1. Microphone access denial gracefully switches to text-only mode
2. OpenAI API failures trigger automatic text fallback
3. Poor audio quality detection prompts candidate to switch to text
4. Network latency issues handled without interview disruption
5. Clear messaging explains fallback reasons to candidate
6. Text-only mode fully functional as backup
7. Interview state preserved during mode transitions
8. System logs capture failure reasons for debugging and monitoring
