// React Query hooks for Resume operations

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { resumesApi, type ResumeResponse, type ResumeUploadResponse, type ResumeAnalysisResponse } from '@/lib/api/resumes';
import { useToast } from '@/hooks/use-toast';

/**
 * Query key factory for resumes
 */
export const resumeKeys = {
  all: ['resumes'] as const,
  lists: () => [...resumeKeys.all, 'list'] as const,
  list: () => [...resumeKeys.lists()] as const,
  details: () => [...resumeKeys.all, 'detail'] as const,
  detail: (id: string) => [...resumeKeys.details(), id] as const,
  analyses: () => [...resumeKeys.all, 'analysis'] as const,
  analysis: (id: string) => [...resumeKeys.analyses(), id] as const,
};

/**
 * Hook to fetch all resumes for current candidate
 */
export function useResumes() {
  return useQuery({
    queryKey: resumeKeys.list(),
    queryFn: () => resumesApi.list(),
    staleTime: 30 * 1000, // 30 seconds
  });
}

/**
 * Hook to fetch single resume details
 */
export function useResume(resumeId: string | null) {
  return useQuery({
    queryKey: resumeId ? resumeKeys.detail(resumeId) : ['resumes', 'detail', 'null'],
    queryFn: () => resumeId ? resumesApi.get(resumeId) : Promise.resolve(null),
    enabled: !!resumeId,
  });
}

/**
 * Hook to fetch resume analysis with polling
 */
export function useResumeAnalysis(resumeId: string | null, options?: { 
  enabled?: boolean;
  refetchInterval?: number;
}) {
  return useQuery({
    queryKey: resumeId ? resumeKeys.analysis(resumeId) : ['resumes', 'analysis', 'null'],
    queryFn: () => resumeId ? resumesApi.getAnalysis(resumeId) : Promise.resolve(null),
    enabled: options?.enabled !== false && !!resumeId,
    refetchInterval: options?.refetchInterval, // For polling
    retry: false, // Don't retry 404s
  });
}

/**
 * Hook to upload a resume
 */
export function useUploadResume() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (file: File) => resumesApi.upload(file),
    onSuccess: (data: ResumeUploadResponse) => {
      // Invalidate resumes list to refetch
      queryClient.invalidateQueries({ queryKey: resumeKeys.list() });
      
      toast({
        title: 'Resume uploaded successfully',
        description: 'AI analysis is processing in the background...',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Upload failed',
        description: error.message || 'Failed to upload resume. Please try again.',
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook to activate a resume
 */
export function useActivateResume() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (resumeId: string) => resumesApi.activate(resumeId),
    onMutate: async (resumeId: string) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: resumeKeys.list() });

      // Snapshot previous value
      const previousResumes = queryClient.getQueryData<ResumeResponse[]>(resumeKeys.list());

      // Optimistically update to the new value
      if (previousResumes) {
        queryClient.setQueryData<ResumeResponse[]>(
          resumeKeys.list(),
          previousResumes.map(r => ({
            ...r,
            is_active: r.id === resumeId,
          }))
        );
      }

      return { previousResumes };
    },
    onError: (error: Error, _resumeId, context) => {
      // Rollback optimistic update
      if (context?.previousResumes) {
        queryClient.setQueryData(resumeKeys.list(), context.previousResumes);
      }

      toast({
        title: 'Failed to set active resume',
        description: error.message,
        variant: 'destructive',
      });
    },
    onSuccess: () => {
      toast({
        title: 'Resume activated',
        description: 'This resume is now your active resume.',
      });
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: resumeKeys.list() });
    },
  });
}

/**
 * Hook to delete a resume
 */
export function useDeleteResume() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (resumeId: string) => resumesApi.delete(resumeId),
    onMutate: async (resumeId: string) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: resumeKeys.list() });

      // Snapshot previous value
      const previousResumes = queryClient.getQueryData<ResumeResponse[]>(resumeKeys.list());

      // Optimistically remove from list
      if (previousResumes) {
        queryClient.setQueryData<ResumeResponse[]>(
          resumeKeys.list(),
          previousResumes.filter(r => r.id !== resumeId)
        );
      }

      return { previousResumes };
    },
    onError: (error: Error, _resumeId, context) => {
      // Rollback optimistic update
      if (context?.previousResumes) {
        queryClient.setQueryData(resumeKeys.list(), context.previousResumes);
      }

      toast({
        title: 'Failed to delete resume',
        description: error.message,
        variant: 'destructive',
      });
    },
    onSuccess: () => {
      toast({
        title: 'Resume deleted',
        description: 'Your resume has been removed.',
      });
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: resumeKeys.list() });
    },
  });
}

/**
 * Hook to download a resume
 */
export function useDownloadResume() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (resumeId: string) => {
      const url = await resumesApi.getDownloadUrl(resumeId);
      // Open in new tab
      window.open(url, '_blank');
      return url;
    },
    onError: (error: Error) => {
      toast({
        title: 'Download failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}
