# Audio Capture Integration Guide

## Overview
This guide explains how to integrate the audio capture components into the interview page.

## Completed Components

### 1. `useAudioCapture` Hook
**Location:** `src/features/interview/hooks/useAudioCapture.ts`

Provides audio recording functionality using MediaRecorder API.

**Usage:**
```typescript
const {
  state,              // 'idle' | 'recording' | 'processing' | 'error'
  error,              // Error message (if any)
  permissionGranted,  // Boolean
  startRecording,     // Async function
  stopRecording,      // Async function, returns Blob
  requestPermission,  // Async function
} = useAudioCapture();
```

### 2. `audioService`
**Location:** `src/features/interview/services/audioService.ts`

Handles audio upload to backend with multipart/form-data.

**Usage:**
```typescript
const response = await audioService.uploadAudio(
  interviewId,    // string
  audioBlob,      // Blob from stopRecording()
  messageSequence // optional number
);

// Response type: AudioUploadResponse
// {
//   transcription: string,
//   confidence: number,
//   ai_response: string,
//   question_number: number,
//   ...
// }
```

### 3. `PushToTalkButton` Component
**Location:** `src/features/interview/components/PushToTalkButton/`

Visual button for recording audio.

**Usage:**
```typescript
<PushToTalkButton
  state={audioCaptureState}
  error={errorMessage}
  onMouseDown={handleStartRecording}
  onMouseUp={handleStopRecording}
  onTouchStart={handleStartRecording}  // Mobile support
  onTouchEnd={handleStopRecording}     // Mobile support
  disabled={!permissionGranted}
/>
```

### 4. `MicrophonePermissionDialog` Component
**Location:** `src/features/interview/components/MicrophonePermissionDialog/`

Modal dialog for requesting microphone permissions.

**Usage:**
```typescript
<MicrophonePermissionDialog
  show={!permissionGranted}
  onPermissionGranted={() => setShowDialog(false)}
  onPermissionDenied={() => setShowDialog(false)}
/>
```

### 5. Interview Store Updates
**Location:** `src/features/interview/store/interviewStore.ts`

Added audio recording state fields:
- `isRecording: boolean`
- `audioPermissionGranted: boolean`
- `recordingError: string | null`

Added actions:
- `setRecording(isRecording: boolean)`
- `setAudioPermission(granted: boolean)`
- `setRecordingError(error: string | null)`

## Integration Steps for Interview Page

### Step 1: Import Components
```typescript
import { useAudioCapture } from '@/features/interview/hooks/useAudioCapture';
import { PushToTalkButton } from '@/features/interview/components/PushToTalkButton';
import { MicrophonePermissionDialog } from '@/features/interview/components/MicrophonePermissionDialog';
import { audioService } from '@/features/interview/services/audioService';
import { useInterviewStore } from '@/features/interview/store/interviewStore';
```

### Step 2: Setup Audio Capture Hook
```typescript
const {
  state: audioState,
  error: audioError,
  permissionGranted,
  startRecording,
  stopRecording,
} = useAudioCapture();

const [showPermissionDialog, setShowPermissionDialog] = useState(!permissionGranted);
const [uploadError, setUploadError] = useState<string | null>(null);
```

### Step 3: Implement Recording Handlers
```typescript
const handleStartRecording = async () => {
  setUploadError(null);
  await startRecording();
};

const handleStopRecording = async () => {
  try {
    const audioBlob = await stopRecording();
    
    if (!audioBlob) {
      setUploadError('No audio recorded');
      return;
    }

    // Upload to backend
    const response = await audioService.uploadAudio(
      sessionId,  // Interview session ID
      audioBlob
    );
    
    // Add candidate message with transcription
    addMessage({
      role: 'candidate',
      content: response.transcription,
    });
    
    // Add AI response
    addMessage({
      role: 'ai',
      content: response.ai_response,
    });
    
  } catch (err) {
    setUploadError((err as Error).message);
  }
};
```

### Step 4: Add to JSX
```typescript
return (
  <div className="interview-page">
    {/* Permission Dialog */}
    <MicrophonePermissionDialog
      show={showPermissionDialog}
      onPermissionGranted={() => setShowPermissionDialog(false)}
      onPermissionDenied={() => setShowPermissionDialog(false)}
    />

    {/* Existing interview content */}
    <div className="messages">
      {/* Message list */}
    </div>

    {/* Input Area */}
    <div className="input-area">
      {/* Text input (existing) */}
      <input type="text" placeholder="Type your answer..." />
      
      {/* Audio input (NEW) */}
      <PushToTalkButton
        state={audioState}
        error={audioError || uploadError}
        onMouseDown={handleStartRecording}
        onMouseUp={handleStopRecording}
        onTouchStart={handleStartRecording}
        onTouchEnd={handleStopRecording}
        disabled={!permissionGranted}
      />
    </div>
  </div>
);
```

## Reference Implementation
See `AudioCaptureExample.tsx` for a complete working example.

## Testing
All components have comprehensive unit tests:
- `PushToTalkButton.test.tsx` - 11 tests
- `MicrophonePermissionDialog.test.tsx` - 10 tests

Run tests:
```bash
npm test -- PushToTalkButton
npm test -- MicrophonePermissionDialog
```

## Browser Support
- ✅ Chrome 47+
- ✅ Firefox 25+
- ✅ Safari 14+
- ✅ Edge 79+

The hook automatically detects browser support and shows appropriate error messages.

## Error Handling
The components handle these errors automatically:
- Microphone permission denied
- No microphone device found
- MediaRecorder not supported
- Audio codec not supported
- Network timeout (30s)
- Server errors (400, 500)

## Next Steps
1. Integrate components into `app/interview/[sessionId]/page.tsx`
2. Test end-to-end flow with backend
3. Manual testing across browsers
4. Mobile device testing (iOS/Android)

## Questions?
Refer to the story file: `docs/stories/1.5.2.frontend-audio-capture-mvp.md`
