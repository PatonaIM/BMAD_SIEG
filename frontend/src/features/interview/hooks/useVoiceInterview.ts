import { useCallback } from 'react';
import { useInterviewStore } from '../store/interviewStore';
import { useAudioCapture } from './useAudioCapture';
import { apiClient } from '@/services/api/client';

/**
 * Voice Interview Workflow Hook
 * Orchestrates the complete voice interview flow:
 * 1. AI asks question → Play audio → State: "AI Speaking"
 * 2. Audio ends → State: "AI Listening" → Enable microphone
 * 3. Candidate presses button → State: "Candidate Speaking" → Start recording
 * 4. Candidate releases button → Stop recording → State: "Processing" → Upload audio
 * 5. Transcription received → Process with AI → Back to step 1
 */
export function useVoiceInterview() {
  const {
    setInterviewState,
    setCurrentAudioUrl,
    currentAudioUrl,
  } = useInterviewStore();

  const audioCapture = useAudioCapture();

  /**
   * Handle AI question with audio
   * Sets audio URL and transitions to AI speaking state
   */
  const handleAIQuestionWithAudio = useCallback(
    (audioUrl: string) => {
      setCurrentAudioUrl(audioUrl);
      setInterviewState('ai_speaking');
    },
    [setCurrentAudioUrl, setInterviewState]
  );

  /**
   * Handle audio playback end
   * Transitions to listening state
   */
  const handleAudioPlaybackEnd = useCallback(() => {
    setInterviewState('ai_listening');
  }, [setInterviewState]);

  /**
   * Handle audio playback error
   * Falls back to listening state (text-only)
   */
  const handleAudioPlaybackError = useCallback(() => {
    console.warn('Audio playback failed, falling back to text-only');
    setInterviewState('ai_listening');
    setCurrentAudioUrl(null);
  }, [setInterviewState, setCurrentAudioUrl]);

  /**
   * Start recording audio (candidate speaking)
   */
  const startRecording = useCallback(async () => {
    if (!audioCapture.permissionGranted) {
      console.error('Microphone permission not granted');
      return;
    }
    setInterviewState('candidate_speaking');
    await audioCapture.startRecording();
  }, [audioCapture, setInterviewState]);

  /**
   * Stop recording and upload audio
   */
  const stopRecording = useCallback(
    async (sessionId: string): Promise<Blob | null> => {
      const audioBlob = await audioCapture.stopRecording();
      if (!audioBlob) {
        setInterviewState('ai_listening');
        return null;
      }

      setInterviewState('processing');
      return audioBlob;
    },
    [audioCapture, setInterviewState]
  );

  /**
   * Upload audio to speech-to-text endpoint
   * Returns transcribed text
   */
  const uploadAudio = useCallback(
    async (sessionId: string, audioBlob: Blob): Promise<string | null> => {
      try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        const response = await apiClient.post<{ transcription: string }>(
          `/interviews/${sessionId}/speech-to-text`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        );

        return response.transcription;
      } catch (error) {
        console.error('Failed to upload audio:', error);
        setInterviewState('ai_listening');
        return null;
      }
    },
    [setInterviewState]
  );

  return {
    audioCapture,
    currentAudioUrl,
    handleAIQuestionWithAudio,
    handleAudioPlaybackEnd,
    handleAudioPlaybackError,
    startRecording,
    stopRecording,
    uploadAudio,
  };
}
