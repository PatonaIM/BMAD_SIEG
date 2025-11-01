import { apiClient } from '../../../services/api/client';

/**
 * Response from audio upload endpoint
 * Includes transcription and AI response
 */
export interface AudioUploadResponse {
  transcription: string;
  confidence: number;
  processing_time_ms: number;
  audio_metadata: {
    provider: string;
    model: string;
    duration_seconds: number;
    language: string;
  };
  ai_response: string;
  question_number: number;
}

/**
 * Error response from API
 */
export interface AudioErrorResponse {
  detail: string;
}

/**
 * Audio service for backend communication
 * Handles audio upload and processing
 */
export const audioService = {
  /**
   * Upload audio recording to backend for transcription
   * 
   * @param interviewId - The interview session ID
   * @param audioBlob - The recorded audio blob (WebM/Opus format)
   * @param messageSequence - Optional message sequence number
   * @returns Promise with transcription and AI response
   */
  async uploadAudio(
    interviewId: string,
    audioBlob: Blob,
    messageSequence?: number
  ): Promise<AudioUploadResponse> {
    try {
      // Create FormData for multipart/form-data upload
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'audio.webm');
      
      if (messageSequence !== undefined) {
        formData.append('message_sequence', String(messageSequence));
      }

      // Get auth token
      const token = localStorage.getItem('auth_token');
      
      // Build URL
      const endpoint = `/api/v1/interviews/${interviewId}/audio`;
      const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${endpoint}`;

      // Send request with 30 second timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle error responses
      if (!response.ok) {
        const errorData: AudioErrorResponse = await response.json();
        throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
      }

      // Parse and return response
      const data: AudioUploadResponse = await response.json();
      return data;
    } catch (error) {
      // Handle timeout
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Audio upload timed out. Please check your connection and try again.');
      }

      // Handle network errors
      if (error instanceof TypeError) {
        throw new Error('Network error. Please check your internet connection.');
      }

      // Re-throw other errors
      throw error;
    }
  },
};
