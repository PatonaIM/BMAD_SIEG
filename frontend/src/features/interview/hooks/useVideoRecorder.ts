import { useState, useRef, useCallback } from 'react';

export type VideoRecorderState = 'idle' | 'recording' | 'paused' | 'error';

export interface UseVideoRecorderReturn {
  recordingState: VideoRecorderState;
  error: string | null;
  videoChunks: Blob[];
  startRecording: (stream: MediaStream) => Promise<void>;
  stopRecording: () => Promise<void>;
  reconnectCamera: () => Promise<boolean>;
}

/**
 * Custom hook for video recording using MediaRecorder API
 * Records at 720p, 30fps with WebM/MP4 format based on browser support
 * Implements chunked recording for upload optimization (30-second intervals)
 * 
 * @returns Video recording controls and state
 */
export function useVideoRecorder(): UseVideoRecorderReturn {
  const [recordingState, setRecordingState] = useState<VideoRecorderState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [videoChunks, setVideoChunks] = useState<Blob[]>([]);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  /**
   * Attempt to reconnect camera if disconnected
   */
  const reconnectCamera = useCallback(async (): Promise<boolean> => {
    try {
      // Request camera access again
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          frameRate: { ideal: 30 },
        },
      });

      streamRef.current = stream;
      
      // If we were recording, restart with new stream
      if (recordingState === 'recording' && mediaRecorderRef.current) {
        await startRecording(stream);
      }
      
      setError(null);
      return true;
    } catch (err) {
      const error = err as Error;
      setError(`Failed to reconnect camera: ${error.message}`);
      setRecordingState('error');
      return false;
    }
  }, [recordingState]);

  /**
   * Start recording video from provided MediaStream
   * 
   * @param stream - MediaStream from getUserMedia with video track
   */
  const startRecording = useCallback(async (stream: MediaStream): Promise<void> => {
    try {
      // Validate stream has video track
      const videoTracks = stream.getVideoTracks();
      if (videoTracks.length === 0) {
        setError('No video track found in stream');
        setRecordingState('error');
        return;
      }

      // Store stream reference
      streamRef.current = stream;

      // Check MediaRecorder support
      if (typeof MediaRecorder === 'undefined') {
        setError('Video recording is not supported in your browser.');
        setRecordingState('error');
        return;
      }

      // Find supported MIME type (prefer VP9, fallback to VP8, H.264)
      const mimeTypes = [
        'video/webm;codecs=vp9',
        'video/webm;codecs=vp8',
        'video/webm',
        'video/mp4',
      ];

      const supportedMimeType = mimeTypes.find(
        (mimeType) => MediaRecorder.isTypeSupported?.(mimeType)
      );

      if (!supportedMimeType) {
        setError('No supported video format found for your browser.');
        setRecordingState('error');
        return;
      }

      // Initialize MediaRecorder
      chunksRef.current = [];
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: supportedMimeType,
        videoBitsPerSecond: 500000, // 500 kbps for balance between quality and size
      });

      // Handle data available event (30-second chunks)
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
          // Update state with new chunks for upload
          setVideoChunks([...chunksRef.current]);
        }
      };

      // Handle recording errors
      mediaRecorderRef.current.onerror = (event: Event) => {
        const errorEvent = event as ErrorEvent;
        setError(`Recording error: ${errorEvent.message || 'Unknown error'}`);
        setRecordingState('error');
      };

      // Listen for video track ending (camera disconnect)
      const videoTrack = videoTracks[0];
      videoTrack.onended = async () => {
        setError('Camera disconnected. Attempting to reconnect...');
        await reconnectCamera();
      };

      // Start recording with 30-second timeslice for chunked upload
      mediaRecorderRef.current.start(30000); // 30 seconds = 30000ms
      
      setRecordingState('recording');
      setError(null);
    } catch (err) {
      const error = err as Error;
      setError(`Failed to start recording: ${error.message}`);
      setRecordingState('error');
    }
  }, [reconnectCamera]);

  /**
   * Stop recording and clean up resources
   */
  const stopRecording = useCallback(async (): Promise<void> => {
    return new Promise((resolve) => {
      if (!mediaRecorderRef.current || recordingState !== 'recording') {
        resolve();
        return;
      }

      mediaRecorderRef.current.onstop = () => {
        // Final chunks already captured in ondataavailable
        setRecordingState('idle');
        
        // Stop all tracks to release camera
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
        
        resolve();
      };

      mediaRecorderRef.current.stop();
    });
  }, [recordingState]);

  return {
    recordingState,
    error,
    videoChunks,
    startRecording,
    stopRecording,
    reconnectCamera,
  };
}
