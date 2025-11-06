/**
 * Custom React Query hook for fetching a single job posting
 * 
 * This hook provides a wrapper around React Query's useQuery for fetching
 * a specific job posting by ID from the API.
 * 
 * @example
 * ```tsx
 * const { data: job, isLoading, isError, error } = useJobPosting(jobId);
 * 
 * if (isLoading) return <Skeleton />;
 * if (isError) return <ErrorMessage error={error} />;
 * if (!job) return <NotFound />;
 * 
 * return <JobDetail job={job} />;
 * ```
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { jobPostingsApi, type JobPosting } from '@/lib/api-client';

/**
 * Query key factory for individual job posting
 * Ensures proper cache invalidation and consistency with list queries
 */
export const jobPostingKeys = {
  all: ['job-postings'] as const,
  detail: (id: string) => [...jobPostingKeys.all, id] as const,
};

/**
 * Hook for fetching a single job posting by ID
 * 
 * @param id - Job posting UUID
 * @returns React Query result with job posting data, loading, and error states
 */
export function useJobPosting(id: string): UseQueryResult<JobPosting, Error> {
  return useQuery({
    queryKey: jobPostingKeys.detail(id),
    queryFn: () => jobPostingsApi.getById(id),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes cache (formerly cacheTime)
    retry: 2,
    enabled: !!id, // Only run query if id is provided
  });
}
