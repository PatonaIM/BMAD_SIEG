/**
 * Response from video chunk upload endpoint
 */
export interface VideoChunkUploadResponse {
  success: boolean;
  chunk_index: number;
  uploaded_at: string;
}

/**
 * Error response from API
 */
export interface VideoErrorResponse {
  detail: string;
}

/**
 * Video upload service for backend communication
 * Handles chunked video upload during interview recording
 */
export const videoUploadService = {
  /**
   * Upload a video chunk to backend storage
   * Implements retry logic with exponential backoff
   * 
   * @param interviewId - The interview session ID
   * @param chunk - Video chunk blob (WebM/MP4 format)
   * @param chunkIndex - Zero-indexed chunk number
   * @param isFinal - Whether this is the final chunk
   * @param retryCount - Internal retry counter
   * @returns Promise with upload confirmation
   */
  async uploadVideoChunk(
    interviewId: string,
    chunk: Blob,
    chunkIndex: number,
    isFinal: boolean = false,
    retryCount: number = 0
  ): Promise<VideoChunkUploadResponse> {
    const maxRetries = 3;
    
    try {
      // Create FormData for multipart/form-data upload
      const formData = new FormData();
      formData.append('chunk', chunk, `chunk_${chunkIndex}.webm`);
      formData.append('chunk_index', String(chunkIndex));
      formData.append('is_final', String(isFinal));

      // Get auth token
      const token = localStorage.getItem('auth_token');
      
      // Build URL
      const endpoint = `/api/v1/interviews/${interviewId}/video/upload`;
      const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${endpoint}`;

      // Send request with 60 second timeout (larger chunks than audio)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);

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
        // Handle storage quota exceeded (507)
        if (response.status === 507) {
          throw new Error('Storage quota exceeded. Please contact support.');
        }

        const errorData: VideoErrorResponse = await response.json();
        throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
      }

      // Parse and return response
      const data: VideoChunkUploadResponse = await response.json();
      return data;
    } catch (error) {
      // Handle timeout
      if (error instanceof Error && error.name === 'AbortError') {
        if (retryCount < maxRetries) {
          // Exponential backoff: 1s, 2s, 4s
          const delay = Math.pow(2, retryCount) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.uploadVideoChunk(interviewId, chunk, chunkIndex, isFinal, retryCount + 1);
        }
        throw new Error('Video upload timed out after multiple retries. Continuing with audio-only mode.');
      }

      // Handle network errors with retry
      if (error instanceof TypeError) {
        if (retryCount < maxRetries) {
          // Exponential backoff
          const delay = Math.pow(2, retryCount) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.uploadVideoChunk(interviewId, chunk, chunkIndex, isFinal, retryCount + 1);
        }
        throw new Error('Network error. Video upload failed after multiple retries.');
      }

      // Storage quota errors should not retry
      if (error instanceof Error && error.message.includes('Storage quota')) {
        throw error;
      }

      // Retry other errors
      if (retryCount < maxRetries) {
        const delay = Math.pow(2, retryCount) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.uploadVideoChunk(interviewId, chunk, chunkIndex, isFinal, retryCount + 1);
      }

      // All retries exhausted
      throw error;
    }
  },

  /**
   * Track upload progress for monitoring
   * Returns percentage of chunks uploaded successfully
   */
  calculateUploadProgress(uploadedChunks: number, totalChunks: number): number {
    if (totalChunks === 0) return 0;
    return Math.round((uploadedChunks / totalChunks) * 100);
  },
};
