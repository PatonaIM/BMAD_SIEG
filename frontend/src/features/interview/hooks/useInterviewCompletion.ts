"use client"

import { useMutation, useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import {
  completeInterview,
  getInterviewTranscript,
  type InterviewCompleteResponse,
  type InterviewTranscriptResponse,
} from "../services/interviewService"
import { useInterviewStore } from "../store/interviewStore"

/**
 * Hook for completing an interview
 * Calls completion endpoint, updates store, and navigates to results page
 */
export const useCompleteInterview = () => {
  const router = useRouter()
  const { setCompleted, setCompletionData } = useInterviewStore()

  return useMutation({
    mutationFn: (interviewId: string) => completeInterview(interviewId),
    onSuccess: (data: InterviewCompleteResponse, interviewId: string) => {
      console.log("Interview completed successfully:", data)

      // Update store with completion data
      setCompleted()
      setCompletionData({
        interview_id: data.interview_id,
        completed_at: data.completed_at,
        duration_seconds: data.duration_seconds,
        questions_answered: data.questions_answered,
        skill_boundaries_identified: data.skill_boundaries_identified,
        message: data.message,
      })

      // Navigate to results page
      router.push(`/interview/${interviewId}/results`)
    },
    onError: (error: Error) => {
      console.error("Failed to complete interview:", error)
      // TODO: Show error notification to user
    },
  })
}

/**
 * Hook for fetching interview transcript
 * Loads full conversation history with caching
 * Transcript is immutable once interview is completed
 */
export const useInterviewTranscript = (interviewId: string | undefined) => {
  return useQuery({
    queryKey: ["interview", interviewId, "transcript"],
    queryFn: async () => {
      if (!interviewId) {
        throw new Error("Interview ID is required")
      }

      console.log("Fetching transcript for interview:", interviewId)
      const transcript = await getInterviewTranscript(interviewId)

      return transcript
    },
    enabled: !!interviewId, // Only fetch if interviewId is provided
    staleTime: Infinity, // Transcript is immutable after completion
    gcTime: 1000 * 60 * 60, // Cache for 1 hour
    retry: 2,
  })
}
