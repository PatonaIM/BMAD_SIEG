/**
 * Custom React Query mutation hook for submitting job applications
 * 
 * This hook provides a wrapper around React Query's useMutation for creating
 * applications via the API. Handles success notifications, cache invalidation,
 * and error handling including duplicate application detection.
 * 
 * @example
 * ```tsx
 * const { mutate: applyToJob, isPending, isSuccess, isError, error } = useApplyToJob();
 * 
 * const handleApply = () => {
 *   applyToJob(jobId, {
 *     onSuccess: (application) => {
 *       console.log('Applied! Interview ID:', application.interview_id);
 *       router.push(`/interview/start?application_id=${application.id}`);
 *     },
 *   });
 * };
 * 
 * return (
 *   <Button onClick={handleApply} disabled={isPending}>
 *     {isPending ? 'Applying...' : 'Apply Now'}
 *   </Button>
 * );
 * ```
 */

import { useMutation, useQueryClient, type UseMutationResult } from '@tanstack/react-query';
import { applicationsApi, type Application } from '@/lib/api-client';
import { applicationsKeys } from './use-applications';
import { useToast } from '@/hooks/use-toast';

/**
 * Hook for submitting job applications
 * 
 * Automatically:
 * - Shows success toast notification
 * - Invalidates applications cache to refetch updated list
 * - Handles duplicate application errors (409 Conflict)
 * - Handles authentication errors (401 Unauthorized)
 * 
 * @returns React Query mutation result with mutate function and status states
 */
export function useApplyToJob(): UseMutationResult<Application, Error, string, unknown> {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (jobPostingId: string) => applicationsApi.createApplication(jobPostingId),
    
    onSuccess: (data) => {
      // Show success notification
      toast({
        title: 'Application submitted successfully!',
        description: 'Your application has been received. You can now start the AI interview.',
        variant: 'default',
      });

      // Invalidate applications cache to trigger refetch
      queryClient.invalidateQueries({ queryKey: applicationsKeys.me() });
      
      // Optionally update the applications cache optimistically
      queryClient.setQueryData<Application[]>(applicationsKeys.me(), (old) => {
        if (!old) return [data];
        return [data, ...old];
      });
    },
    
    onError: (error) => {
      // Handle specific error cases
      if (error.message === 'Already applied to this job') {
        toast({
          title: 'Already applied',
          description: 'You have already submitted an application for this position.',
          variant: 'destructive',
        });
      } else if (error.message === 'Job posting not found') {
        toast({
          title: 'Job not found',
          description: 'This job posting is no longer available.',
          variant: 'destructive',
        });
      } else if (error.message === 'Job posting is not active') {
        toast({
          title: 'Job not available',
          description: 'This job posting is no longer accepting applications.',
          variant: 'destructive',
        });
      } else if (error.message === 'Authentication required') {
        toast({
          title: 'Authentication required',
          description: 'Please log in to apply for this position.',
          variant: 'destructive',
        });
      } else {
        toast({
          title: 'Application failed',
          description: error.message || 'An error occurred while submitting your application. Please try again.',
          variant: 'destructive',
        });
      }
    },
  });
}
