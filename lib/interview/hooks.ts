"use client"

import { useMutation, useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { startInterview, getInterviewMessages, sendInterviewMessage } from "./service"
import type { StartInterviewRequest, InterviewResponse, SendMessageResponse } from "./service"
import { useInterviewStore } from "./store"

/**
 * Hook for starting a new interview
 * Calls backend API and navigates to interview page on success
 */
export const useStartInterview = () => {
  const router = useRouter()
  const { setSessionId, setStatus, clearMessages } = useInterviewStore()

  return useMutation({
    mutationFn: (data: StartInterviewRequest) => startInterview(data),
    onSuccess: (interview: InterviewResponse) => {
      console.log("[v0] Interview started successfully:", interview)

      // Clear any previous interview data
      clearMessages()

      // Set new interview session
      setSessionId(interview.id)
      setStatus(interview.status as "in_progress" | "completed")

      console.log("[v0] Navigating to:", `/interview/${interview.id}`)

      // Navigate to interview page
      router.push(`/interview/${interview.id}`)
    },
    onError: (error: Error) => {
      console.error("[v0] Failed to start interview:", error)
    },
  })
}

/**
 * Hook for fetching interview messages
 * Loads conversation history when interview page mounts
 */
export const useInterviewMessages = (interviewId: string | undefined) => {
  const { setMessages, updateProgress } = useInterviewStore()

  return useQuery({
    queryKey: ["interview", interviewId, "messages"],
    queryFn: async () => {
      console.log("[v0] Fetching messages for interview:", interviewId)

      if (!interviewId) {
        throw new Error("Interview ID is required")
      }
      const data = await getInterviewMessages(interviewId)

      console.log("[v0] Received messages:", data)

      // Convert backend messages to frontend format
      const messages = data.messages.map((msg) => ({
        id: msg.id,
        role: msg.message_type === "ai_question" ? ("ai" as const) : ("candidate" as const),
        content: msg.content_text,
        timestamp: new Date(msg.created_at).getTime(),
      }))

      console.log("[v0] Converted messages:", messages)

      // Set messages in store
      setMessages(messages)

      // Update progress if we have messages
      if (messages.length > 0) {
        const aiQuestions = messages.filter((m) => m.role === "ai").length
        updateProgress(aiQuestions, 15) // TODO: Get actual total from backend
      }

      return data
    },
    enabled: !!interviewId,
    staleTime: 1000 * 60, // Consider data fresh for 1 minute
    refetchOnWindowFocus: false,
  })
}

/**
 * Custom hook for sending interview messages
 * Uses TanStack Query for mutation management
 * Updates interview store on success
 */
export function useSendMessage({ sessionId }: { sessionId: string }) {
  const { addMessage, setAiTyping, updateProgress } = useInterviewStore()

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

    onSuccess: (data) => {
      // Add AI response to messages
      addMessage({
        role: "ai",
        content: data.ai_response,
      })

      // Update progress
      updateProgress(data.question_number, data.total_questions)

      // Hide typing indicator
      setAiTyping(false)
    },

    onError: (error) => {
      // Hide typing indicator on error
      setAiTyping(false)

      // Log error (in production, show notification to user)
      console.error("[v0] Failed to send message:", error)
    },
  })
}
