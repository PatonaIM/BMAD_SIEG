/**
 * Custom React Query hook for fetching candidate applications
 * 
 * This hook provides a wrapper around React Query's useQuery for fetching
 * the authenticated candidate's applications from the API.
 * 
 * IMPORTANT: Backend returns Application[] directly (array), NOT an object with pagination metadata.
 * Calculate total from array.length.
 * 
 * @example
 * ```tsx
 * const { data, isLoading, isError, error, refetch } = useApplications();
 * 
 * // data is Application[] or undefined
 * const totalApps = data?.length || 0;
 * const recentApps = data?.slice(0, 3) || [];
 * ```
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { applicationsApi, type Application } from '@/lib/api-client';

/**
 * Query key factory for applications
 * Ensures proper cache invalidation
 */
export const applicationsKeys = {
  all: ['applications'] as const,
  me: () => [...applicationsKeys.all, 'me'] as const,
};

/**
 * Hook for fetching authenticated candidate's applications
 * 
 * @returns React Query result with applications data (Application[]), loading, and error states
 */
export function useApplications(): UseQueryResult<Application[], Error> {
  return useQuery({
    queryKey: applicationsKeys.me(),
    queryFn: () => applicationsApi.getMyApplications(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes cache (formerly cacheTime)
    retry: 2,
    refetchOnMount: true,
  });
}
