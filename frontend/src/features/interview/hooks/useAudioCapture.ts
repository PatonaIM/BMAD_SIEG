import { useState, useRef, useCallback } from 'react';

export type AudioCaptureState = 'idle' | 'recording' | 'processing' | 'error';

export interface UseAudioCaptureReturn {
  state: AudioCaptureState;
  error: string | null;
  permissionGranted: boolean;
  startRecording: (onChunk?: (chunk: ArrayBuffer) => void) => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  requestPermission: () => Promise<boolean>;
  getMediaStream: () => MediaStream | null;
}

export interface UseAudioCaptureOptions {
  externalStream?: MediaStream | null;
}

/**
 * Custom hook for audio capture using MediaRecorder API
 * Supports WebM format with Opus codec for wide browser compatibility
 * 
 * @param options - Optional configuration including external stream
 * @returns Audio capture controls and state
 */
export function useAudioCapture(options?: UseAudioCaptureOptions): UseAudioCaptureReturn {
  const [state, setState] = useState<AudioCaptureState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [permissionGranted, setPermissionGranted] = useState<boolean>(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const externalStreamRef = useRef<MediaStream | null>(options?.externalStream || null);

  // Update external stream ref when it changes
  externalStreamRef.current = options?.externalStream || null;

  /**
   * Request microphone permission from user
   */
  const requestPermission = useCallback(async (): Promise<boolean> => {
    try {
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('Your browser does not support audio recording. Please use Chrome, Firefox, or Safari.');
        setState('error');
        return false;
      }

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 48000,
        },
      });

      streamRef.current = stream;
      setPermissionGranted(true);
      setError(null);
      return true;
    } catch (err) {
      const error = err as Error;
      
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        setError('Microphone access denied. Please enable microphone permissions in your browser settings.');
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        setError('No microphone found. Please connect a microphone and try again.');
      } else {
        setError(`Failed to access microphone: ${error.message}`);
      }
      
      setState('error');
      setPermissionGranted(false);
      return false;
    }
  }, []);

  /**
   * Start recording audio
   * 
   * @param onChunk - Optional callback for streaming audio chunks (for realtime mode)
   */
  const startRecording = useCallback(async (onChunk?: (chunk: ArrayBuffer) => void): Promise<void> => {
    try {
      // Use external stream if provided, otherwise get our own
      let activeStream: MediaStream | null = externalStreamRef.current;
      
      if (!activeStream) {
        // Request permission if not already granted
        if (!permissionGranted || !streamRef.current) {
          const granted = await requestPermission();
          if (!granted) {
            return;
          }
        }
        activeStream = streamRef.current;
      }

      if (!activeStream) {
        setError('No audio stream available');
        setState('error');
        return;
      }

      // Check MediaRecorder support
      if (typeof MediaRecorder === 'undefined') {
        setError('Audio recording is not supported in your browser.');
        setState('error');
        return;
      }

      // Find supported MIME type
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
      ];

      const supportedMimeType = mimeTypes.find(
        (mimeType) => MediaRecorder.isTypeSupported?.(mimeType)
      );

      if (!supportedMimeType) {
        setError('No supported audio format found for your browser.');
        setState('error');
        return;
      }

      // Initialize MediaRecorder
      audioChunksRef.current = [];
      mediaRecorderRef.current = new MediaRecorder(activeStream, {
        mimeType: supportedMimeType,
        audioBitsPerSecond: 32000,
      });

      // Handle data available event
      mediaRecorderRef.current.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          
          // If streaming callback provided, send chunk immediately
          if (onChunk) {
            try {
              const arrayBuffer = await event.data.arrayBuffer();
              onChunk(arrayBuffer);
            } catch (err) {
              console.error('Error processing audio chunk:', err);
            }
          }
        }
      };

      // Start recording with timeslice for streaming (100ms chunks)
      if (onChunk) {
        mediaRecorderRef.current.start(100); // Request data every 100ms
      } else {
        // For non-streaming mode, request data periodically to ensure chunks are captured
        mediaRecorderRef.current.start(1000); // Request data every 1 second
      }
      
      setState('recording');
      setError(null);
    } catch (err) {
      const error = err as Error;
      setError(`Failed to start recording: ${error.message}`);
      setState('error');
    }
  }, [permissionGranted, requestPermission]);

  /**
   * Get the current media stream
   */
  const getMediaStream = useCallback((): MediaStream | null => {
    return streamRef.current;
  }, []);

  /**
   * Stop recording and return audio Blob
   */
  const stopRecording = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (!mediaRecorderRef.current) {
        resolve(null);
        return;
      }

      // Check recorder state instead of hook state
      if (mediaRecorderRef.current.state !== 'recording') {
        resolve(null);
        return;
      }

      setState('processing');

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, {
          type: mediaRecorderRef.current?.mimeType || 'audio/webm',
        });
        
        audioChunksRef.current = [];
        setState('idle');
        resolve(blob);
      };

      mediaRecorderRef.current.stop();
    });
  }, []); // Remove state dependency

  return {
    state,
    error,
    permissionGranted,
    startRecording,
    stopRecording,
    requestPermission,
    getMediaStream,
  };
}
