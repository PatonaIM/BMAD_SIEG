/**
 * Custom React Query hook for fetching job postings
 * 
 * This hook provides a wrapper around React Query's useQuery for fetching
 * job postings from the API with filtering, pagination, and caching support.
 * 
 * @example
 * ```tsx
 * const { data, isLoading, isError, error, refetch } = useJobPostings({
 *   search: 'developer',
 *   employment_type: 'permanent',
 *   skip: 0,
 *   limit: 20
 * });
 * ```
 */

import { useQuery } from '@tanstack/react-query';
import { jobPostingsApi, type JobPostingFilters } from '@/lib/api-client';

/**
 * Query key factory for job postings
 * Ensures proper cache invalidation when filters change
 */
export const jobPostingsKeys = {
  all: ['job-postings'] as const,
  lists: () => [...jobPostingsKeys.all, 'list'] as const,
  list: (filters: JobPostingFilters) => [...jobPostingsKeys.lists(), filters] as const,
};

/**
 * Hook for fetching job postings with filters
 * 
 * @param filters - Optional filter parameters for querying job postings
 * @returns React Query result with job postings data, loading, and error states
 */
export function useJobPostings(filters: JobPostingFilters = {}) {
  return useQuery({
    queryKey: jobPostingsKeys.list(filters),
    queryFn: () => jobPostingsApi.list(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes cache (formerly cacheTime)
    retry: 2,
    refetchOnWindowFocus: false,
  });
}
