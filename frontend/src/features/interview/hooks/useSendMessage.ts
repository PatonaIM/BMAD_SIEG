"use client"

import { useMutation } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { sendInterviewMessage, completeInterview } from "../services/interviewService"
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
  const { addMessage, setAiTyping, updateProgress, setStatus } = useInterviewStore()
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

      console.log(`[v0] Interview progress: ${data.question_number}/${data.total_questions}`)

      // Hide typing indicator
      setAiTyping(false)

      if (data.question_number >= data.total_questions) {
        console.log("[v0] Interview completed - all questions answered")

        // Mark interview as completed
        setStatus("completed")

        // Call completion API endpoint
        try {
          await completeInterview(sessionId)
          console.log("[v0] Interview completion recorded")
        } catch (error) {
          console.error("[v0] Failed to record completion:", error)
        }

        // Redirect to results page after a short delay
        setTimeout(() => {
          console.log("[v0] Redirecting to results page")
          router.push(`/interview/${sessionId}/results`)
        }, 2000)
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
