/**
 * Example component demonstrating audio capture integration
 * This shows how to use useAudioCapture, PushToTalkButton, and audioService together
 * 
 * This is a reference implementation for Task 5 (Interview Page Integration)
 */

import React, { useState } from 'react';
import { useAudioCapture } from '../hooks/useAudioCapture';
import { PushToTalkButton } from './PushToTalkButton';
import { MicrophonePermissionDialog } from './MicrophonePermissionDialog';
import { audioService } from '../services/audioService';

interface AudioCaptureExampleProps {
  interviewId: string;
  onTranscriptionReceived?: (transcription: string, aiResponse: string) => void;
}

export function AudioCaptureExample({ 
  interviewId,
  onTranscriptionReceived 
}: AudioCaptureExampleProps) {
  const {
    state,
    error,
    permissionGranted,
    startRecording,
    stopRecording,
  } = useAudioCapture();

  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showPermissionDialog, setShowPermissionDialog] = useState(!permissionGranted);

  /**
   * Handle mouse down - start recording
   */
  const handleMouseDown = async () => {
    setUploadError(null);
    await startRecording();
  };

  /**
   * Handle mouse up - stop recording and upload
   */
  const handleMouseUp = async () => {
    try {
      const audioBlob = await stopRecording();
      
      if (!audioBlob) {
        setUploadError('No audio recorded');
        return;
      }

      // Upload to backend
      const response = await audioService.uploadAudio(interviewId, audioBlob);
      
      // Notify parent component
      onTranscriptionReceived?.(response.transcription, response.ai_response);
    } catch (err) {
      const error = err as Error;
      setUploadError(error.message);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 p-6">
      {/* Permission Dialog */}
      <MicrophonePermissionDialog
        show={showPermissionDialog}
        onPermissionGranted={() => setShowPermissionDialog(false)}
        onPermissionDenied={() => setShowPermissionDialog(false)}
      />

      {/* Push-to-Talk Button */}
      <PushToTalkButton
        state={state}
        error={error || uploadError}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onTouchStart={handleMouseDown}
        onTouchEnd={handleMouseUp}
        disabled={!permissionGranted}
      />

      {/* Fallback Text Input Hint */}
      {!permissionGranted && (
        <p className="text-sm text-gray-600">
          Microphone not available. Please use text input below.
        </p>
      )}
    </div>
  );
}
