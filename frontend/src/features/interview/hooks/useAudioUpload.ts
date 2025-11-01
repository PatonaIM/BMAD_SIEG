import { useMutation, useQueryClient } from '@tanstack/react-query';

interface AudioUploadParams {
  sessionId: string;
  audioBlob: Blob;
  messageSequence?: number;
}

interface AudioProcessingResponse {
  transcription: string;
  confidence: number;
  processing_time_ms: number;
  audio_metadata: {
    provider: string;
    model: string;
    format: string;
    file_size_bytes: number;
    sample_rate_hz: number;
    confidence: number;
    processing_time_ms: number;
    language: string;
  };
  next_question_ready: boolean;
  message_id: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Hook for uploading audio files to the backend for transcription
 * Integrates with POST /api/v1/interviews/{interview_id}/audio
 */
export function useAudioUpload() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ sessionId, audioBlob, messageSequence }: AudioUploadParams) => {
      const url = `${API_BASE_URL}/interviews/${sessionId}/audio`;
      
      console.log('📤 Uploading audio:', {
        url,
        sessionId,
        size: audioBlob.size,
        type: audioBlob.type,
        messageSequence,
        API_BASE_URL,
      });

      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');
      
      if (messageSequence !== undefined) {
        formData.append('message_sequence', messageSequence.toString());
      }

      // Get auth token from localStorage
      const token = localStorage.getItem('auth_token');
      const headers: Record<string, string> = {};
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(
        url,
        {
          method: 'POST',
          body: formData,
          headers,
        }
      );

      console.log('📥 Response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
      });

      if (!response.ok) {
        let error;
        try {
          error = await response.json();
        } catch (e) {
          error = { message: `HTTP ${response.status}: ${response.statusText}` };
        }
        console.error('❌ Audio upload failed:', error);
        
        // Handle different error formats
        const errorMessage = 
          error?.detail?.message || 
          error?.message || 
          error?.detail || 
          `Failed to process audio (HTTP ${response.status})`;
        
        throw new Error(errorMessage);
      }

      const data: AudioProcessingResponse = await response.json();
      console.log('✅ Audio processed:', data);
      return data;
    },
    onSuccess: (_data, variables) => {
      // Invalidate messages query to refetch with new AI response
      queryClient.invalidateQueries({ 
        queryKey: ['interview', variables.sessionId, 'messages'] 
      });
    },
  });
}
