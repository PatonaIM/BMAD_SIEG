/**
 * Custom React Query hook for fetching job matches
 * 
 * This hook provides a wrapper around React Query's useQuery for fetching
 * matched jobs from the API with caching support.
 * 
 * @example
 * ```tsx
 * const { data, isLoading, isError, error } = useJobMatches(1, 20);
 * 
 * if (isLoading) return <Skeleton />;
 * if (isError) return <ErrorMessage />;
 * 
 * return <JobMatchList jobs={data.jobs} />;
 * ```
 */

import { useQuery } from '@tanstack/react-query';
import { matchingApi } from '@/lib/api-client';
import type { JobMatchesResponse } from '@/types/matching';
import { useToast } from '@/hooks/use-toast';

/**
 * Query key factory for job matches data
 * Ensures proper cache invalidation
 */
export const jobMatchesKeys = {
  all: ['job-matches'] as const,
  lists: () => [...jobMatchesKeys.all, 'list'] as const,
  list: (page: number, limit: number) => [...jobMatchesKeys.lists(), page, limit] as const,
};

/**
 * Hook for fetching matched jobs for authenticated candidate
 * 
 * @param page - Page number (default: 1)
 * @param limit - Results per page (default: 20, max: 100)
 * @returns React Query result with matched jobs data, loading, and error states
 */
export function useJobMatches(page: number = 1, limit: number = 20) {
  const { toast } = useToast();

  return useQuery<JobMatchesResponse, Error>({
    queryKey: jobMatchesKeys.list(page, limit),
    queryFn: async () => {
      try {
        return await matchingApi.getMatches(page, limit);
      } catch (error) {
        // Handle specific error cases
        if (error instanceof Error) {
          if (error.message.includes('403')) {
            toast({
              title: 'Profile Incomplete',
              description: 'Complete your profile to unlock AI job matching (minimum 40% completeness required).',
              variant: 'destructive',
            });
          } else if (error.message.includes('404')) {
            toast({
              title: 'No Profile Data',
              description: 'Please complete your profile to start receiving job matches.',
              variant: 'destructive',
            });
          } else {
            toast({
              title: 'Failed to Load Matches',
              description: 'Unable to fetch job matches. Please try again later.',
              variant: 'destructive',
            });
          }
        }
        throw error;
      }
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes cache
    retry: 2,
    refetchOnWindowFocus: false,
  });
}
