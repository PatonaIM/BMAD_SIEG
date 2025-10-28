# Teamified Pre-Interview System Check

A comprehensive system validation screen that tests microphone permissions, audio quality, and network connectivity before candidates begin their AI-driven technical interview.

## Features

- **Microphone Permission Check**: Requests and validates browser microphone access
- **Audio Test with Waveform**: Records 3+ seconds of audio with real-time waveform visualization and playback
- **Connection Test**: Verifies network latency and connection quality
- **Error Handling**: Comprehensive error states with troubleshooting tips
- **Accessibility**: Full ARIA support, keyboard navigation, and screen reader compatibility
- **Responsive Design**: Mobile-first design that works on all screen sizes

## Components

### Pages
- `app/pre-interview-check/page.tsx` - Main system check page

### Components
- `components/teamified/SystemCheckStep.tsx` - Individual step component with status indicators
- `components/teamified/WaveformVisualizer.tsx` - Real-time audio waveform visualization

### Hooks
- `hooks/useMicrophonePermission.ts` - Manages microphone permission requests
- `hooks/useAudioRecording.ts` - Handles audio recording, playback, and visualization

## Usage

Navigate to `/pre-interview-check` to access the system check screen.

The flow automatically progresses through three steps:
1. Microphone permission request
2. Audio recording and playback test
3. Network connection verification

## Testing

### Test Microphone Permission Denial
The browser will show a permission dialog. Click "Block" to test the error state.

### Test Audio Recording
Speak clearly for 3 seconds when prompted. The waveform will visualize your audio input.

### Test Connection
The connection test simulates network latency. Refresh the page to get different latency results.

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (requires HTTPS or localhost)

## Accessibility

- All interactive elements are keyboard accessible
- ARIA live regions announce status changes
- Clear focus indicators on all buttons
- Screen reader support for all step states
- Proper heading hierarchy

## Dependencies

- React 18+
- Material-UI v3
- TypeScript
- Web Audio API
- MediaRecorder API
