/**
 * Custom React Query hook for fetching profile data
 * 
 * This hook provides a wrapper around React Query's useQuery for fetching
 * candidate profile data from the API with caching support.
 * 
 * @example
 * ```tsx
 * const { data: profile, isLoading, isError, error } = useProfile();
 * 
 * if (isLoading) return <Skeleton />;
 * if (isError) return <ErrorMessage />;
 * 
 * return <div>{profile.full_name}</div>;
 * ```
 */

import { useQuery } from '@tanstack/react-query';
import { profileApi } from '@/lib/api-client';
import type { ProfileResponse } from '@/types/profile';

/**
 * Query key factory for profile data
 * Ensures proper cache invalidation
 */
export const profileKeys = {
  all: ['profile'] as const,
  detail: () => [...profileKeys.all, 'detail'] as const,
};

/**
 * Hook for fetching authenticated candidate's profile
 * 
 * @returns React Query result with profile data, loading, and error states
 */
export function useProfile() {
  return useQuery<ProfileResponse, Error>({
    queryKey: profileKeys.detail(),
    queryFn: () => profileApi.get(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes cache
    retry: 2,
    refetchOnWindowFocus: false,
  });
}
