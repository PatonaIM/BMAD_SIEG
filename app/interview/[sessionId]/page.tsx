"use client"

import { use } from "react"
import { Box, Container } from "@mui/material"
import { useInterviewStore } from "@/lib/interview/store"
import { useInterviewMessages, useSendMessage } from "@/lib/interview/hooks"
import InterviewProgress from "@/components/interview/interview-progress"
import InterviewChat from "@/components/interview/interview-chat"
import ChatInput from "@/components/interview/chat-input"
import TypingIndicator from "@/components/interview/typing-indicator"

export default function InterviewPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const { sessionId } = use(params)
  const { messages, currentQuestion, totalQuestions, isAiTyping } = useInterviewStore()

  // Fetch interview messages on mount
  const { isLoading, isError } = useInterviewMessages(sessionId)

  // Send message mutation
  const { mutate: sendMessage, isPending } = useSendMessage({ sessionId })

  const handleSendMessage = (messageText: string) => {
    sendMessage(messageText)
  }

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
          Loading interview...
        </Box>
      </Container>
    )
  }

  if (isError) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
          Failed to load interview. Please try again.
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" disableGutters>
      <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
        <InterviewProgress current={currentQuestion} total={totalQuestions} />

        <Box sx={{ flex: 1, overflow: "hidden", position: "relative" }}>
          <InterviewChat messages={messages} isTyping={isAiTyping} />
          {isAiTyping && <TypingIndicator isVisible={isAiTyping} />}
        </Box>

        <ChatInput onSendMessage={handleSendMessage} disabled={isPending || isAiTyping} isLoading={isPending} />
      </Box>
    </Container>
  )
}
