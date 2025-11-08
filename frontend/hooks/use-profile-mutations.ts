/**
 * Custom React Query mutation hooks for profile updates
 * 
 * This module provides mutation hooks for updating profile data (skills, preferences)
 * with optimistic updates, cache invalidation, and error handling.
 * 
 * @example
 * ```tsx
 * const { mutate: updateSkills, isPending } = useUpdateSkills();
 * 
 * const handleSave = () => {
 *   updateSkills(["React", "TypeScript"], {
 *     onSuccess: () => {
 *       toast({ title: "Skills updated!" });
 *     },
 *   });
 * };
 * ```
 */

import { useMutation, useQuery, useQueryClient, type UseMutationResult } from '@tanstack/react-query';
import { profileApi, resumeApi } from '@/lib/api-client';
import { profileKeys } from './use-profile';
import { useToast } from '@/hooks/use-toast';
import type { ProfileResponse, UpdatePreferencesRequest, UpdateBasicInfoRequest, ResumeParsingStatus } from '@/types/profile';

/**
 * Hook for updating candidate skills
 * 
 * Automatically:
 * - Shows success/error toast notifications
 * - Invalidates profile cache to refetch updated data
 * - Invalidates dashboard cache (if exists)
 * - Provides optimistic updates for instant UI feedback
 * 
 * Note: Frontend sends raw skills array; backend normalizes (lowercase, trim, dedupe, sort)
 * 
 * @returns React Query mutation result with mutate function and status states
 */
export function useUpdateSkills(): UseMutationResult<ProfileResponse, Error, string[], unknown> {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (skills: string[]) => profileApi.updateSkills(skills),
    
    // Optimistic update: Update cache immediately before API call
    onMutate: async (newSkills) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: profileKeys.detail() });

      // Snapshot previous value
      const previousProfile = queryClient.getQueryData<ProfileResponse>(profileKeys.detail());

      // Optimistically update cache
      if (previousProfile) {
        queryClient.setQueryData<ProfileResponse>(profileKeys.detail(), {
          ...previousProfile,
          skills: newSkills,
        });
      }

      // Return context with previous value
      return { previousProfile };
    },
    
    onSuccess: () => {
      toast({
        title: 'Skills updated successfully!',
        description: 'Your skills have been saved.',
        variant: 'default',
      });

      // Invalidate profile cache
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
      
      // Invalidate dashboard cache if it exists
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    
    onError: (error, _newSkills, context) => {
      // Rollback optimistic update on error
      if (context?.previousProfile) {
        queryClient.setQueryData(profileKeys.detail(), context.previousProfile);
      }

      toast({
        title: 'Failed to update skills',
        description: error.message || 'An error occurred while saving your skills. Please try again.',
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook for updating candidate basic info (name, phone)
 * 
 * Automatically:
 * - Shows success/error toast notifications
 * - Invalidates profile cache to refetch updated data
 * - Invalidates dashboard cache (if exists)
 * - Provides optimistic updates for instant UI feedback
 * 
 * @returns React Query mutation result with mutate function and status states
 */
export function useUpdateBasicInfo(): UseMutationResult<ProfileResponse, Error, UpdateBasicInfoRequest, unknown> {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (basicInfo: UpdateBasicInfoRequest) => profileApi.updateBasicInfo(basicInfo),
    
    // Optimistic update: Update cache immediately before API call
    onMutate: async (newBasicInfo) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: profileKeys.detail() });

      // Snapshot previous value
      const previousProfile = queryClient.getQueryData<ProfileResponse>(profileKeys.detail());

      // Optimistically update cache
      if (previousProfile) {
        queryClient.setQueryData<ProfileResponse>(profileKeys.detail(), {
          ...previousProfile,
          ...(newBasicInfo.full_name !== undefined && { full_name: newBasicInfo.full_name }),
          ...(newBasicInfo.phone !== undefined && { phone: newBasicInfo.phone }),
          ...(newBasicInfo.experience_years !== undefined && { experience_years: newBasicInfo.experience_years }),
        });
      }

      // Return context with previous value
      return { previousProfile };
    },
    
    onSuccess: () => {
      toast({
        title: 'Profile updated successfully!',
        description: 'Your basic information has been saved.',
        variant: 'default',
      });

      // Invalidate profile cache
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
      
      // Invalidate dashboard cache if it exists
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    
    onError: (error, _newBasicInfo, context) => {
      // Rollback optimistic update on error
      if (context?.previousProfile) {
        queryClient.setQueryData(profileKeys.detail(), context.previousProfile);
      }

      toast({
        title: 'Failed to update profile',
        description: error.message || 'An error occurred while saving your information. Please try again.',
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook for updating candidate job preferences
 * 
 * Automatically:
 * - Shows success/error toast notifications
 * - Invalidates profile cache to refetch updated data
 * - Invalidates dashboard cache (if exists)
 * 
 * @returns React Query mutation result with mutate function and status states
 */
export function useUpdatePreferences(): UseMutationResult<ProfileResponse, Error, UpdatePreferencesRequest, unknown> {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (preferences: UpdatePreferencesRequest) => profileApi.updatePreferences(preferences),
    
    onSuccess: () => {
      toast({
        title: 'Preferences updated successfully!',
        description: 'Your job preferences have been saved.',
        variant: 'default',
      });

      // Invalidate profile cache
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
      
      // Invalidate dashboard cache if it exists
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    
    onError: (error) => {
      toast({
        title: 'Failed to update preferences',
        description: error.message || 'An error occurred while saving your preferences. Please try again.',
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook for fetching resume parsing status with polling
 * 
 * Automatically polls every 3 seconds while status is "processing"
 * Handles 404 gracefully (no resume uploaded yet)
 * 
 * @param resumeId - Resume UUID from profile.resume_id (null if no resume)
 * @returns React Query result with parsing status data
 */
export function useResumeParsingStatus(resumeId: string | null | undefined) {
  return useQuery<ResumeParsingStatus, Error>({
    queryKey: ['resume-parsing-status', resumeId],
    queryFn: () => {
      if (!resumeId) {
        throw new Error('No resume uploaded');
      }
      return resumeApi.getParsingStatus(resumeId);
    },
    enabled: !!resumeId, // Only run if resumeId exists
    refetchInterval: (data) => {
      // Poll every 3 seconds while processing
      if (data?.status === 'processing') {
        return 3000;
      }
      return false; // Stop polling
    },
    retry: (failureCount, error) => {
      // Don't retry on 404 (no resume)
      if (error.message.includes('404')) {
        return false;
      }
      return failureCount < 2;
    },
    staleTime: 0, // Always fresh when polling
  });
}
