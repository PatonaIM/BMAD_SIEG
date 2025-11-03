import { apiClient } from '@/src/services/api/client';

/**
 * Tech Check API Service
 * Handles tech check results submission
 */

export interface TechCheckRequest {
  audio_test_passed: boolean;
  camera_test_passed: boolean;
  audio_metadata: {
    device_name?: string;
    level?: number;
    duration?: number;
  };
  camera_metadata: {
    device_name?: string;
    resolution?: string;
    format?: string;
  };
  browser_info: string;
}

export interface TechCheckResponse {
  success: boolean;
  message: string;
}

/**
 * Submit tech check results to the backend
 */
export async function submitTechCheckResults(
  interviewId: string,
  results: TechCheckRequest
): Promise<TechCheckResponse> {
  try {
    const response = await apiClient.post<TechCheckResponse>(
      `/interviews/${interviewId}/tech-check`,
      results
    );
    return response;
  } catch (error) {
    console.error('Failed to submit tech check results:', error);
    // Don't block interview start if logging fails
    return {
      success: false,
      message: 'Failed to save tech check results, but you can still proceed',
    };
  }
}

/**
 * Get browser user agent string
 */
export function getBrowserInfo(): string {
  return navigator.userAgent;
}

/**
 * Get device name from media stream (best effort)
 */
export async function getDeviceName(
  deviceType: 'audioinput' | 'videoinput',
  stream: MediaStream
): Promise<string> {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const track = deviceType === 'audioinput' 
      ? stream.getAudioTracks()[0] 
      : stream.getVideoTracks()[0];
    
    if (!track) return 'Unknown Device';
    
    const deviceId = track.getSettings().deviceId;
    const device = devices.find(d => d.deviceId === deviceId);
    
    return device?.label || 'Unknown Device';
  } catch (error) {
    console.error('Failed to get device name:', error);
    return 'Unknown Device';
  }
}
