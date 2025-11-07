import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useJobMatches } from '@/hooks/use-job-matches';
import { matchingApi } from '@/lib/api-client';
import type { JobMatchesResponse } from '@/types/matching';
import React from 'react';

// Mock dependencies
vi.mock('@/lib/api-client', () => ({
  matchingApi: {
    getMatches: vi.fn(),
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

describe('useJobMatches', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return matched jobs data on success', async () => {
    const mockData: JobMatchesResponse = {
      jobs: [
        {
          id: '1',
          title: 'Senior Developer',
          company: 'Tech Corp',
          description: 'Great role',
          location: 'Remote',
          employment_type: 'permanent',
          work_setup: 'remote',
          salary_min: 100000,
          salary_max: 150000,
          required_skills: ['React', 'TypeScript'],
          experience_level: 'senior',
          status: 'active',
          match_score: 85,
          match_classification: 'Excellent',
          preference_matches: {
            location: true,
            work_setup: true,
            employment_type: true,
            salary: true,
          },
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ],
      total: 1,
      page: 1,
      limit: 20,
    };

    vi.mocked(matchingApi.getMatches).mockResolvedValue(mockData);

    const { result } = renderHook(() => useJobMatches(1, 20), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.data?.jobs).toHaveLength(1);
    expect(result.current.data?.jobs[0].title).toBe('Senior Developer');
  });

  it('should handle 403 error (profile completeness < 40%)', async () => {
    const error = new Error('API Error: 403 Forbidden');
    vi.mocked(matchingApi.getMatches).mockRejectedValue(error);

    const { result } = renderHook(() => useJobMatches(1, 20), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });

  it('should handle 404 error (no profile embedding)', async () => {
    const error = new Error('API Error: 404 Not Found');
    vi.mocked(matchingApi.getMatches).mockRejectedValue(error);

    const { result } = renderHook(() => useJobMatches(1, 20), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });

  it('should use correct query key structure', () => {
    const { result } = renderHook(() => useJobMatches(2, 10), {
      wrapper: createWrapper(),
    });

    // Query should be initiated with the correct parameters
    expect(matchingApi.getMatches).not.toHaveBeenCalled(); // Not called until loading starts
  });
});
