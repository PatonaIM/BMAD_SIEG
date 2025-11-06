/**
 * Custom React Query hook for fetching a single application by ID
 * 
 * This hook provides a wrapper around React Query's useQuery for fetching
 * an individual application with job posting details from the API.
 * 
 * @example
 * ```tsx
 * const { data, isLoading, isError, error } = useApplication(applicationId);
 * 
 * // data is Application or undefined
 * if (data) {
 *   console.log('Job Title:', data.job_posting.title);
 *   console.log('Tech Stack:', data.job_posting.tech_stack);
 * }
 * ```
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { applicationsApi, type Application } from '@/lib/api-client';

/**
 * Hook for fetching a single application by ID
 * 
 * @param id - Application UUID or null
 * @returns React Query result with application data, loading, and error states
 */
export function useApplication(id: string | null): UseQueryResult<Application, Error> {
  return useQuery({
    queryKey: ['applications', id],
    queryFn: () => applicationsApi.getById(id!),
    enabled: !!id, // Only fetch when id is not null
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes cache
    retry: 2,
  });
}
