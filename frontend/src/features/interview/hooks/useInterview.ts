"use client"

import { useMutation, useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { startInterview, getInterviewMessages } from "../services/interviewService"
import type { StartInterviewRequest, InterviewResponse } from "../services/interviewService"
import { useInterviewStore } from "../store/interviewStore"

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
      console.log("Interview started successfully:", interview)

      clearMessages()

      setSessionId(interview.id)
      setStatus(interview.status as "in_progress" | "completed")

      console.log("Navigating to:", `/interview/${interview.id}`)

      router.push(`/interview/${interview.id}`)
    },
    onError: (error: Error) => {
      console.error("Failed to start interview:", error)
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
      console.log("Fetching messages for interview:", interviewId)

      if (!interviewId) {
        throw new Error("Interview ID is required")
      }
      const data = await getInterviewMessages(interviewId)

      console.log("Received messages:", data)

      const messages = data.messages.map((msg) => ({
        id: msg.id,
        role: msg.message_type === "ai_question" ? ("ai" as const) : ("candidate" as const),
        content: msg.content_text,
        timestamp: new Date(msg.created_at).getTime(),
      }))

      console.log("Converted messages:", messages)

      setMessages(messages)

      if (messages.length > 0) {
        const aiQuestions = messages.filter((m) => m.role === "ai").length
        updateProgress(aiQuestions, 15)
      }

      return data
    },
    enabled: !!interviewId,
    staleTime: 1000 * 60,
    refetchOnWindowFocus: false,
  })
}
