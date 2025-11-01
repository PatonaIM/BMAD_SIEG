import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAudioUpload } from './useAudioUpload';

// Mock fetch
global.fetch = vi.fn();

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useAudioUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should upload audio successfully', async () => {
    const mockResponse = {
      transcription: 'Hello world',
      confidence: 0.95,
      processing_time_ms: 1500,
      audio_metadata: {
        provider: 'openai',
        model: 'whisper-1',
        format: 'audio/webm',
        file_size_bytes: 10000,
        sample_rate_hz: 16000,
        confidence: 0.95,
        processing_time_ms: 1400,
        language: 'en',
      },
      next_question_ready: true,
      message_id: 'test-message-id',
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useAudioUpload(), {
      wrapper: createWrapper(),
    });

    const audioBlob = new Blob(['test audio data'], { type: 'audio/webm' });
    
    result.current.mutate({
      sessionId: 'test-session-id',
      audioBlob,
      messageSequence: 1,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockResponse);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/interviews/test-session-id/audio'),
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      })
    );
  });

  it('should handle upload errors', async () => {
    const mockError = {
      message: 'Audio file too large',
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => mockError,
    });

    const { result } = renderHook(() => useAudioUpload(), {
      wrapper: createWrapper(),
    });

    const audioBlob = new Blob(['test audio data'], { type: 'audio/webm' });
    
    result.current.mutate({
      sessionId: 'test-session-id',
      audioBlob,
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeInstanceOf(Error);
  });
});
