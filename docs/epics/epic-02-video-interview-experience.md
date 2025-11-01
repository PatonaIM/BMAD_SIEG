# Epic 02: Professional Video Interview Experience

**Epic Goal:** Transform the voice-based interview into a professional video interview platform by adding camera capture, visual AI presence, and polished UX. Candidates experience a tech check before starting, see themselves on camera (with privacy controls), interact with an animated AI presence (orb/circle visualization), and view AI responses as captions for clarity. This epic elevates the interview from "voice chat" to "professional video conversation," creating a premium experience that distinguishes Teamified from competitors while maintaining the natural flow established in Epic 1.5.

## Story 2.0: Video Interview Database Schema Extensions ⭐ PREREQUISITE

**As a** developer,  
**I want** database schema extensions to support video interview features,  
**so that** tech check results, video recordings, and privacy consent can be persisted.

**Acceptance Criteria:**

1. Alembic migration created to extend `interviews` table with video-related fields
2. New `video_recordings` table created for video metadata tracking
3. Migration tested: can upgrade and rollback successfully
4. All new fields properly indexed for query performance
5. JSONB columns support flexible metadata storage
6. Database changes backward compatible (nullable fields, no breaking changes)
7. Migration documented with rationale for each field

**Database Schema Additions:**

**Interviews Table Extensions:**
- `tech_check_metadata` JSONB (stores audio/camera test results)
- `video_recording_url` TEXT (Supabase Storage path)
- `video_recording_consent` BOOLEAN (GDPR consent flag)
- `video_recording_status` VARCHAR(20) (recording lifecycle state)

**New Table - video_recordings:**
- Core fields: id, interview_id, storage_path, file_size_bytes, duration_seconds
- Quality metadata: resolution, bitrate_kbps, codec
- Upload tracking: upload_started_at, upload_completed_at
- Soft delete: deleted_at (GDPR compliance)
- Flexible metadata: recording_metadata JSONB (chunk info, quality metrics)

**Technical Notes:**
- All new fields nullable (backward compatible)
- GIN indexes on JSONB columns for efficient querying
- One video per interview (UNIQUE constraint on interview_id)
- Soft delete support (deleted_at timestamp)
- SQLAlchemy models: `VideoRecording` with relationship to `Interview`

**Why This Story is First:**
Stories 2.1, 2.2, 2.5, and 2.8 all reference database fields that don't exist yet. This story creates the foundation.

**Story File:** `docs/stories/2.0.video-interview-database-schema.md`

---

## Story 2.1: Pre-Interview Tech Check Page

**As a** candidate,  
**I want** to verify my audio and camera are working before the interview starts,  
**so that** I can ensure technical issues don't disrupt my assessment.

**Acceptance Criteria:**

1. Tech check page loads before interview start (new route: `/interview/{id}/tech-check`)
2. Audio test implemented:
   - Microphone permission request with clear explanation
   - Audio level meter shows voice input (visual feedback)
   - "Test Audio" button plays recorded audio back to candidate
   - Pass/fail indicator based on audio level detection
3. Camera test implemented:
   - Camera permission request with clear explanation
   - Live video preview displays candidate's camera feed
   - Resolution check validates minimum quality (480p)
   - Pass/fail indicator based on camera detection
4. Permission handling:
   - Clear error messages if permissions denied
   - Instructions to enable permissions in browser settings
   - Hard block: Cannot proceed to interview until tech check passes (no skip option)
5. "Start Interview" button enabled only after successful tech check (both audio AND camera must pass)
6. "Test Equipment" link available from settings page for pre-check before interview
7. Mobile responsive design (works on iOS Safari, Android Chrome)
8. Tech check results logged for troubleshooting support tickets

**Technical Notes:**
- Use MediaDevices.getUserMedia() for permissions
- Store tech check results in `interviews.tech_check_metadata` JSONB field
- Integrate with existing authentication flow (Story 1.3)
- Tech check runs every interview (no skip functionality)

## Story 2.2: Candidate Video Capture & Recording

**As a** recruiter,  
**I want** candidate video recorded during the interview,  
**so that** I can review body language, professionalism, and presentation skills.

**Acceptance Criteria:**

1. Video capture starts automatically when interview begins
2. Camera feed recorded at 720p, 30fps (balance quality vs cost)
3. Video encoding optimized for web (H.264, MP4 container)
4. Video chunks uploaded via HTTP POST every 30 seconds (separate from WebSocket audio stream)
5. Backend stores video in Supabase Storage (leverages existing infrastructure)
6. Video metadata stored in `interviews.video_recording_url` field
7. Recording indicator visible to candidate (red dot or "Recording" badge)
8. Video recording continues even if candidate hides their own view
9. Continuous recording from interview start to completion (entire session captured)
10. Graceful handling if camera disconnects mid-interview:
    - Show warning to candidate
    - Attempt to reconnect automatically
    - Continue with audio-only if camera can't reconnect
11. GDPR compliance:
    - Candidate informed of video recording before interview
    - Video retention policy enforced (30 days default, configurable)
    - Deletion API endpoint implemented for privacy requests

**Performance Targets:**
- Video upload latency <500ms per chunk
- Storage cost <$0.10 per 20-min interview (Supabase Storage pricing)

**Technical Notes:**
- Use MediaRecorder API for video capture
- Set up Supabase Storage bucket: `interview-recordings` (private, RLS enabled)
- Video upload via HTTP POST (separate from WebSocket audio stream):
  - Endpoint: `POST /api/v1/interviews/{id}/video/upload`
  - Backend uploads chunks to Supabase Storage
  - Uses Supabase client's optimized upload
- Add `video_recordings` table for metadata tracking
- Leverage Supabase RLS (Row Level Security) for access control
- Signed URLs for video access (expire after 24 hours)

## Story 2.3: AI Presence Visualization - Animated Orb

**As a** candidate,  
**I want** to see a visual representation of the AI interviewer,  
**so that** the conversation feels more natural and engaging.

**Acceptance Criteria:**

1. AI presence rendered as animated circular orb (Siri/Gemini style)
2. Orb states clearly indicate AI activity:
   - **Idle**: Subtle pulsing animation (slow breathing effect)
   - **Listening**: Ripple animation expands outward (candidate is speaking)
   - **Thinking**: Circular progress indicator (AI processing response)
   - **Speaking**: Audio waveform visualization synced to AI voice
3. Orb positioned prominently in UI (center-top or left panel)
4. Smooth state transitions without jarring jumps
5. Orb color palette matches brand design system:
   - Primary brand color for main orb
   - Gradient effects for depth
   - Accessibility: sufficient contrast for low-vision users
6. Orb animation performance optimized:
   - 60fps on desktop
   - 30fps minimum on mobile
   - CSS animations preferred over JavaScript (better performance)
7. Animation synced to audio level from Realtime API
8. Fallback to static logo if animations cause performance issues

**Design Reference:**
- Inspiration: Siri orb, Google Gemini logo, Alexa ring
- Simple, elegant, professional (not playful/cartoon)

**Technical Notes:**
- Implement using CSS animations + Canvas or SVG
- Create reusable component: `AIPresenceOrb.tsx`
- Sync with `useRealtimeInterview` hook state

## Story 2.4: Interview Page UI Redesign - Video Layout

**As a** candidate,  
**I want** a clean, professional video interview interface,  
**so that** I can focus on the conversation without distraction.

**Acceptance Criteria:**

1. **Layout Structure** (Google Meet-style grid):
   - AI Orb: Large square tile (left/top, ~60% of screen width)
   - Candidate Camera: Smaller square tile (lower-right, ~30% of screen width)
   - Grid layout maintains aspect ratio (16:9 preferred)
   - AI Captions: Overlay on bottom third of AI tile
   - Controls: Minimal overlay on bottom (mute, camera toggle, end interview)

2. **Candidate Camera Behavior**:
   - Self-view shown by default (help candidates see framing)
   - Toggle button to hide self-view (reduces self-consciousness)
   - Camera still records when self-view hidden
   - Icon indicator shows camera is active even when hidden

3. **AI Captions**:
   - Display AI speech as real-time captions (sync with Realtime API transcription)
   - Caption style: Sans-serif font, high contrast, ~18-20px size
   - Hybrid behavior: Persist while AI speaking, fade-out 3 seconds after AI finishes
   - Next caption immediately replaces previous caption
   - Option to disable captions (accessibility toggle)

4. **Candidate Transcription Hidden**:
   - Candidate's own speech NOT shown as captions (reduce distraction)
   - Transcript available in post-interview review only

5. **State Indicators**:
   - Connection status badge (subtle, top-right corner)
   - Recording indicator (red dot, always visible)
   - Audio/video mute icons (when active)

6. **Responsive Design**:
   - Desktop: Google Meet grid (AI tile prominent, candidate tile lower-right)
   - Tablet: Same grid scaled down (maintain proportions)
   - Mobile: AI tile full-screen, candidate tile mini floating overlay (bottom-right)

7. **Accessibility**:
   - Keyboard shortcuts (Space to mute, C to toggle camera)
   - Screen reader announcements for state changes
   - High contrast mode support

**Technical Notes:**
- Refactor `interview/[sessionId]/page.tsx`
- Create new components: 
  - `VideoGridLayout.tsx` (Google Meet-style grid container)
  - `AITile.tsx` (large tile with orb + captions)
  - `CandidateTile.tsx` (smaller tile with video preview)
  - `CaptionDisplay.tsx` (caption overlay)
- Use CSS Grid for responsive tile layout
- Integrate with existing `useRealtimeInterview` hook

## Story 2.5: Candidate Video Privacy Controls

**As a** candidate,  
**I want** control over my video visibility and recording,  
**so that** I feel comfortable and respect my privacy preferences.

**Acceptance Criteria:**

1. **Camera Toggle Control**:
   - Button to hide/show self-view (doesn't stop recording)
   - Button to disable camera entirely (stops recording, audio-only mode)
   - Clear visual feedback for each state (icon changes)

2. **Privacy Consent Flow**:
   - Before interview, candidate explicitly consents to video recording
   - Consent modal explains:
     - Video will be recorded and stored
     - Only recruiters can view the video
     - Video retention period (30 days)
     - Right to request deletion
   - Candidate can decline video and proceed audio-only

3. **Audio-Only Fallback**:
   - If candidate declines video, interview continues with audio
   - UI adapts: No camera preview, larger AI orb
   - Recording metadata marks interview as "audio_only"

4. **Privacy Indicators**:
   - Recording indicator always visible when video active
   - Initial warning when recording starts (first 5 seconds of interview)
   - Tooltip explains "Video is being recorded for recruiter review"
   - Clear messaging in tech check about recording
   - No pause/break functionality (continuous recording)

5. **Post-Interview Controls**:
   - Candidate can request video deletion via profile settings
   - Deletion request logged and processed within 7 days (GDPR compliance)

**Technical Notes:**
- Add `video_recording_consent` field to `interviews` table
- Implement deletion API: `DELETE /api/v1/interviews/{id}/video`
- Update privacy policy documentation

## Story 2.6: Caption Sync & Timing Optimization

**As a** candidate,  
**I want** AI captions to appear in sync with the AI's speech,  
**so that** I can follow along without confusion.

**Acceptance Criteria:**

1. Captions display text as AI speaks (real-time sync)
2. Caption timing matches audio playback (latency <100ms)
3. Long responses broken into readable chunks:
   - Max 2 lines per caption segment
   - Auto-segment at natural sentence breaks
4. Caption animation smooth with hybrid behavior:
   - Fade-in: 200ms
   - Display: Persists while AI is speaking
   - Fade-out: 300ms, triggered 3 seconds after AI finishes speaking
   - Next caption immediately replaces previous caption (no fade delay)
5. Caption positioning avoids overlapping controls
6. Caption text sanitized (no markdown formatting, clean punctuation)
7. Caption history accessible via keyboard shortcut (H key shows last 3 captions)
8. Caption performance optimized (no dropped frames during animation)

**Technical Notes:**
- Sync with Realtime API transcript events
- Implement caption queue system for smooth transitions
- Use CSS transitions for performance

## Story 2.7: Video Interview E2E Testing & Performance Validation

**As a** developer,  
**I want** comprehensive E2E tests for the video interview flow,  
**so that** we catch regressions and validate performance targets.

**Acceptance Criteria:**

1. **E2E Test Suite**:
   - Tech check flow (audio + camera tests)
   - Full interview with video recording
   - Privacy controls (hide camera, audio-only fallback)
   - Caption display and sync
   - Error scenarios (camera disconnect, permission denied)

2. **Performance Validation**:
   - Video upload latency <500ms per chunk
   - AI orb animation 60fps on desktop (measure with Performance API)
   - Caption sync latency <100ms
   - Page load time <2s on 3G network

3. **Browser Compatibility Testing**:
   - Chrome, Firefox, Safari (desktop)
   - iOS Safari, Android Chrome (mobile)
   - Document known issues and workarounds

4. **Mock Infrastructure**:
   - Mock Supabase Storage upload for video chunks
   - Mock camera/microphone APIs
   - Test fixtures for various screen sizes

**Technical Notes:**
- Use Playwright for E2E tests
- Add performance monitoring to CI/CD pipeline
- Create test fixtures in `frontend/tests/fixtures/video/`

## Story 2.8: Video Storage & Cleanup Infrastructure

**As a** system administrator,  
**I want** automated video storage management,  
**so that** we control costs and comply with data retention policies.

**Acceptance Criteria:**

1. Set up Supabase Storage bucket `interview-recordings`:
   - Bucket type: Private (not public)
   - RLS policies configured (only authorized org members can access)
   - File path structure: `{organization_id}/{interview_id}/recording.mp4`
   - Auto-delete policy after 30 days (configurable per organization, deferred to post-MVP)
2. Video metadata stored in `video_recordings` table:
   - interview_id, storage_path, duration, size_mb, uploaded_at
   - Recording quality metadata (resolution, bitrate)
3. Background job runs daily to clean up expired videos:
   - Query videos older than retention period
   - Delete from Supabase Storage
   - Mark as deleted in database
4. Video deletion API respects GDPR:
   - Soft delete (mark as deleted, keep metadata)
   - Hard delete after 90 days (permanent removal from storage)
5. Cost monitoring:
   - Track storage usage per month
   - Alert if storage exceeds quota (100GB threshold)
6. Video access URLs use Supabase signed URLs (expire after 24 hours)
7. Video encryption at rest (handled by Supabase)

**Technical Notes:**
- Create Supabase Storage bucket: `interview-recordings` (private, RLS enabled)
- Configure RLS policies:
  - Only authenticated users can upload to their own org's interviews
  - Only org members can read videos from their org
- Create `video_recordings` table migration
- Implement background job: `VideoCleanupJob` (runs via cron or Supabase Edge Function)
- Use Supabase client for upload/download operations
- Generate signed URLs for time-limited video access (24-hour expiry)
- Video compression/retention policies deferred to post-MVP
- Integrate with existing cost tracking (Story 1.5.6 Task 6)

## Epic Success Metrics

1. **Tech Check Completion Rate**: >95% of candidates pass tech check on first attempt
2. **Video Recording Success Rate**: >98% of interviews have complete video recording
3. **Performance**:
   - AI orb animation: 60fps on desktop, 30fps on mobile
   - Caption sync latency: <100ms
   - Video upload latency: <500ms per chunk
4. **User Experience**:
   - Candidate satisfaction: >4.5/5 for video interview experience
   - Recruiter feedback: "Video adds value" >80% positive
5. **Cost Management**: Video storage costs <$0.15 per interview

## Dependencies

**Prerequisites (Must Complete First):**
- **Story 2.0** (Database Schema Extensions): CRITICAL - All other stories depend on database fields created here
- **Epic 1.5** (Speech-to-Speech): Must be complete for AI audio/transcript integration
- **Story 1.5.6** (Realtime API): Required for caption sync and AI presence animation
- **Story 1.3** (Authentication): Required for tech check permission flow

**Story Sequencing Within Epic 02:**
1. **Story 2.0** (Database) - FIRST - Creates schema foundation
2. **Story 2.8** (Storage Infrastructure) - SECOND - Sets up Supabase Storage bucket
3. Stories 2.1-2.7 can proceed in parallel after 2.0 and 2.8 complete

## Deferred Features (Post-MVP)

- ❌ Multiple AI avatar options (orb styles, colors)
- ❌ Virtual backgrounds for candidate camera
- ❌ Picture-in-picture mode for multi-tasking
- ❌ Interview recording playback for candidates
- ❌ Screen sharing for technical assessments (deferred to Epic 2.x)
- ❌ Multi-camera support (front/rear on mobile)

---

**Epic Owner**: PM + Frontend Lead  
**Target Completion**: Q1 2026  
**Estimated Effort**: 6-8 weeks (parallel development with backend/frontend teams)
