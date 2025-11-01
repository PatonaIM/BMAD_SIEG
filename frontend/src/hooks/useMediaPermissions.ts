import { useState, useCallback, useRef, useEffect } from 'react';

export type PermissionState = 'idle' | 'requesting' | 'granted' | 'denied' | 'error';

export interface VideoResolution {
  width: number;
  height: number;
}

export interface UseMediaPermissionsReturn {
  // Microphone
  microphoneStatus: PermissionState;
  microphoneStream: MediaStream | null;
  microphoneError: string | null;
  requestMicrophone: () => Promise<boolean>;
  releaseMicrophone: () => void;
  
  // Camera
  cameraStatus: PermissionState;
  cameraStream: MediaStream | null;
  cameraError: string | null;
  videoResolution: VideoResolution | null;
  requestCamera: () => Promise<boolean>;
  releaseCamera: () => void;
}

/**
 * Hook for managing media device permissions (microphone and camera)
 * Handles permission requests, error states, and stream management
 */
export function useMediaPermissions(): UseMediaPermissionsReturn {
  // Microphone state
  const [microphoneStatus, setMicrophoneStatus] = useState<PermissionState>('idle');
  const [microphoneStream, setMicrophoneStream] = useState<MediaStream | null>(null);
  const [microphoneError, setMicrophoneError] = useState<string | null>(null);
  const microphoneStreamRef = useRef<MediaStream | null>(null);

  // Camera state
  const [cameraStatus, setCameraStatus] = useState<PermissionState>('idle');
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [videoResolution, setVideoResolution] = useState<VideoResolution | null>(null);
  const cameraStreamRef = useRef<MediaStream | null>(null);

  /**
   * Request microphone permission
   */
  const requestMicrophone = useCallback(async (): Promise<boolean> => {
    try {
      setMicrophoneStatus('requesting');
      setMicrophoneError(null);

      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('NotSupported');
      }

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 48000,
        },
      });

      microphoneStreamRef.current = stream;
      setMicrophoneStream(stream);
      setMicrophoneStatus('granted');
      return true;
    } catch (err) {
      const error = err as DOMException;
      let errorMessage = 'Failed to access microphone';

      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        errorMessage = 'Microphone access denied. Please enable microphone permissions in your browser settings.';
        setMicrophoneStatus('denied');
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        errorMessage = 'No microphone found. Please connect a microphone and try again.';
        setMicrophoneStatus('error');
      } else if (error.name === 'NotReadableError') {
        errorMessage = 'Microphone is already in use by another application.';
        setMicrophoneStatus('error');
      } else if (error.message === 'NotSupported') {
        errorMessage = 'Your browser does not support audio recording. Please use Chrome, Firefox, or Safari.';
        setMicrophoneStatus('error');
      } else {
        errorMessage = `Failed to access microphone: ${error.message}`;
        setMicrophoneStatus('error');
      }

      setMicrophoneError(errorMessage);
      return false;
    }
  }, []);

  /**
   * Release microphone stream
   */
  const releaseMicrophone = useCallback(() => {
    if (microphoneStreamRef.current) {
      microphoneStreamRef.current.getTracks().forEach(track => track.stop());
      microphoneStreamRef.current = null;
      setMicrophoneStream(null);
      setMicrophoneStatus('idle');
    }
  }, []);

  /**
   * Request camera permission with resolution validation
   */
  const requestCamera = useCallback(async (): Promise<boolean> => {
    try {
      setCameraStatus('requesting');
      setCameraError(null);
      setVideoResolution(null);

      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('NotSupported');
      }

      // Request camera access with minimum 480p resolution
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { min: 640, ideal: 1280 },
          height: { min: 480, ideal: 720 },
          facingMode: 'user', // Front camera for mobile
        },
      });

      // Get video track settings to verify resolution
      const videoTrack = stream.getVideoTracks()[0];
      const settings = videoTrack.getSettings();
      
      const resolution: VideoResolution = {
        width: settings.width || 0,
        height: settings.height || 0,
      };

      // Validate minimum resolution (480p)
      if (resolution.width < 640 || resolution.height < 480) {
        stream.getTracks().forEach(track => track.stop());
        throw new Error('ResolutionTooLow');
      }

      cameraStreamRef.current = stream;
      setCameraStream(stream);
      setVideoResolution(resolution);
      setCameraStatus('granted');
      return true;
    } catch (err) {
      const error = err as DOMException;
      let errorMessage = 'Failed to access camera';

      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        errorMessage = 'Camera access denied. Please enable camera permissions in your browser settings.';
        setCameraStatus('denied');
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        errorMessage = 'No camera found. Please connect a camera and try again.';
        setCameraStatus('error');
      } else if (error.name === 'NotReadableError') {
        errorMessage = 'Camera is already in use by another application.';
        setCameraStatus('error');
      } else if (error.name === 'OverconstrainedError') {
        errorMessage = 'Your camera does not support the required resolution (minimum 480p).';
        setCameraStatus('error');
      } else if (error.message === 'NotSupported') {
        errorMessage = 'Your browser does not support video capture. Please use Chrome, Firefox, or Safari.';
        setCameraStatus('error');
      } else if (error.message === 'ResolutionTooLow') {
        errorMessage = 'Camera resolution too low. Minimum 640x480 (480p) required.';
        setCameraStatus('error');
      } else {
        errorMessage = `Failed to access camera: ${error.message}`;
        setCameraStatus('error');
      }

      setCameraError(errorMessage);
      return false;
    }
  }, []);

  /**
   * Release camera stream
   */
  const releaseCamera = useCallback(() => {
    if (cameraStreamRef.current) {
      cameraStreamRef.current.getTracks().forEach(track => track.stop());
      cameraStreamRef.current = null;
      setCameraStream(null);
      setCameraStatus('idle');
      setVideoResolution(null);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      releaseMicrophone();
      releaseCamera();
    };
  }, [releaseMicrophone, releaseCamera]);

  return {
    microphoneStatus,
    microphoneStream,
    microphoneError,
    requestMicrophone,
    releaseMicrophone,
    cameraStatus,
    cameraStream,
    cameraError,
    videoResolution,
    requestCamera,
    releaseCamera,
  };
}
