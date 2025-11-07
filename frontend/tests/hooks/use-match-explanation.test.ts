import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useMatchExplanation } from '@/hooks/use-match-explanation';
import { matchingApi } from '@/lib/api-client';
import type { MatchExplanation } from '@/types/matching';
import React from 'react';

// Mock dependencies
vi.mock('@/lib/api-client', () => ({
  matchingApi: {
    getExplanation: vi.fn(),
  },
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

// Helper to create QueryClient wrapper
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );
};

describe('useMatchExplanation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return explanation data on success', async () => {
    const mockData: MatchExplanation = {
      job_id: 'job-123',
      candidate_id: 'candidate-456',
      matching_factors: [
        'Strong React skills match job requirements',
        'Experience level aligns with senior position',
      ],
      missing_requirements: ['AWS certification would be beneficial'],
      overall_reasoning: 'Excellent fit for this role based on technical skills and experience.',
      confidence_score: 0.85,
      generated_at: '2024-01-01T10:00:00Z',
    };

    vi.mocked(matchingApi.getExplanation).mockResolvedValue(mockData);

    const { result } = renderHook(() => useMatchExplanation('job-123', true), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.data?.matching_factors).toHaveLength(2);
    expect(result.current.data?.missing_requirements).toHaveLength(1);
  });

  it('should not fetch when enabled is false (lazy loading)', () => {
    const { result } = renderHook(() => useMatchExplanation('job-123', false), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(false);
    expect(matchingApi.getExplanation).not.toHaveBeenCalled();
  });

  it('should handle 404 error (match score < 40%)', async () => {
    const error = new Error('API Error: 404 Not Found');
    vi.mocked(matchingApi.getExplanation).mockRejectedValue(error);

    const { result } = renderHook(() => useMatchExplanation('job-123', true), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });

  it('should handle 500 error (OpenAI service failure)', async () => {
    const error = new Error('API Error: 500 Internal Server Error');
    vi.mocked(matchingApi.getExplanation).mockRejectedValue(error);

    const { result } = renderHook(() => useMatchExplanation('job-123', true), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });

  it('should fetch explanation when enabled changes to true', async () => {
    const mockData: MatchExplanation = {
      job_id: 'job-123',
      candidate_id: 'candidate-456',
      matching_factors: ['Good match'],
      missing_requirements: [],
      overall_reasoning: 'Great fit',
      confidence_score: 0.9,
      generated_at: '2024-01-01T10:00:00Z',
    };

    vi.mocked(matchingApi.getExplanation).mockResolvedValue(mockData);

    const { result, rerender } = renderHook(
      ({ enabled }) => useMatchExplanation('job-123', enabled),
      {
        wrapper: createWrapper(),
        initialProps: { enabled: false },
      }
    );

    expect(matchingApi.getExplanation).not.toHaveBeenCalled();

    rerender({ enabled: true });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(matchingApi.getExplanation).toHaveBeenCalledWith('job-123');
  });
});
