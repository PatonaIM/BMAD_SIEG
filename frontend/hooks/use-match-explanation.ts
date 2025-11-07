/**
 * Custom React Query hook for fetching match explanations
 * 
 * This hook provides a wrapper around React Query's useQuery for fetching
 * match explanations from the API with lazy loading support.
 * 
 * @example
 * ```tsx
 * const [expanded, setExpanded] = useState(false);
 * const { data, isLoading, isError } = useMatchExplanation(jobId, expanded);
 * 
 * <Collapsible open={expanded} onOpenChange={setExpanded}>
 *   {isLoading && <Skeleton />}
 *   {data && <ExplanationContent explanation={data} />}
 * </Collapsible>
 * ```
 */

import { useQuery } from '@tanstack/react-query';
import { matchingApi } from '@/lib/api-client';
import type { MatchExplanation } from '@/types/matching';
import { useToast } from '@/hooks/use-toast';

/**
 * Query key factory for match explanations
 * Ensures proper cache invalidation
 */
export const matchExplanationKeys = {
  all: ['match-explanations'] as const,
  detail: (jobId: string) => [...matchExplanationKeys.all, jobId] as const,
};

/**
 * Hook for fetching match explanation for a specific job
 * 
 * @param jobId - Job posting UUID
 * @param enabled - Whether to fetch explanation (default: true, set to false for lazy loading)
 * @returns React Query result with explanation data, loading, and error states
 */
export function useMatchExplanation(jobId: string, enabled: boolean = true) {
  const { toast } = useToast();

  return useQuery<MatchExplanation, Error>({
    queryKey: matchExplanationKeys.detail(jobId),
    queryFn: async () => {
      try {
        return await matchingApi.getExplanation(jobId);
      } catch (error) {
        // Handle specific error cases
        if (error instanceof Error) {
          if (error.message.includes('404')) {
            toast({
              title: 'Explanation Not Available',
              description: 'Match explanation is only available for matches with scores ≥40%.',
              variant: 'destructive',
            });
          } else if (error.message.includes('500')) {
            toast({
              title: 'Service Unavailable',
              description: 'Unable to generate explanation. Please try again later.',
              variant: 'destructive',
            });
          } else {
            toast({
              title: 'Failed to Load Explanation',
              description: 'Unable to fetch match explanation. Please try again.',
              variant: 'destructive',
            });
          }
        }
        throw error;
      }
    },
    enabled, // Only fetch when enabled (for lazy loading)
    staleTime: 1000 * 60 * 60 * 24, // 24 hours (backend caches explanations)
    gcTime: 1000 * 60 * 60 * 24, // 24 hours cache
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
