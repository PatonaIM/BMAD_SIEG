"use client"

import { useMutation } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { sendInterviewMessage } from "../services/interviewService"
import type { SendMessageResponse } from "../services/interviewService"
import { useInterviewStore } from "../store/interviewStore"

interface UseSendMessageParams {
  sessionId: string
}

/**
 * Custom hook for sending interview messages
 * Uses TanStack Query for mutation management
 * Updates interview store on success
 * Detects completion and redirects to results page
 */
export function useSendMessage({ sessionId }: UseSendMessageParams) {
  const { addMessage, setAiTyping, updateProgress, setStatus, setCurrentAudioUrl } = useInterviewStore()
  const router = useRouter()

  return useMutation<SendMessageResponse, Error, string>({
    mutationFn: (messageText: string) => sendInterviewMessage(sessionId, messageText),

    onMutate: async (messageText: string) => {
      // Optimistic update: Add candidate message immediately
      addMessage({
        role: "candidate",
        content: messageText,
      })

      // Show typing indicator
      setAiTyping(true)
    },

    onSuccess: async (data) => {
      // Add AI response to messages
      addMessage({
        role: "ai",
        content: data.ai_response,
      })

      // Update progress
      updateProgress(data.question_number, data.total_questions)

      console.log(`[Interview] Progress: ${data.question_number}/${data.total_questions}`)

      // Set audio URL if available (Story 1.5.5)
      if (data.audio_url) {
        console.log('[Interview] AI audio available:', data.audio_url)
        setCurrentAudioUrl(data.audio_url)
      } else {
        console.log('[Interview] No audio URL, text-only response')
        setCurrentAudioUrl(null)
      }

      // Hide typing indicator
      setAiTyping(false)

      // Check completion flag from backend (Story 1.8)
      if (data.interview_complete) {
        console.log("[Interview] Completion criteria met - navigating to results")

        // Mark interview as completed
        setStatus("completed")

        // Note: Backend already auto-completed the interview when completion criteria met
        // No need to call completion endpoint again - just navigate to results
        
        // Redirect to results page after a short delay
        setTimeout(() => {
          console.log("[Interview] Redirecting to results page")
          router.push(`/interview/${sessionId}/results`)
        }, 1500)
      }
    },

    onError: (error) => {
      // Hide typing indicator on error
      setAiTyping(false)

      // Log error (in production, show notification to user)
      console.error("Failed to send message:", error)
    },
  })
}
