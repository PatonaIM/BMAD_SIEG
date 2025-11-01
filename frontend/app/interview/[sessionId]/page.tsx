"use client"

import { useParams } from "next/navigation"
import { useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useInterviewStore } from "@/src/features/interview/store/interviewStore"
import { useSendMessage } from "@/src/features/interview/hooks/useSendMessage"
import { useInterviewMessages } from "@/src/features/interview/hooks/useInterview"
import InterviewProgress from "@/src/features/interview/components/InterviewProgress/InterviewProgress"
import InterviewChat from "@/src/features/interview/components/InterviewChat/InterviewChat"
import ChatInput from "@/src/features/interview/components/ChatInput/ChatInput"
import TypingIndicator from "@/src/features/interview/components/TypingIndicator/TypingIndicator"
import { AlertCircle } from "lucide-react"

export default function InterviewPage() {
  const params = useParams()
  const sessionId = params?.sessionId as string | undefined

  const { messages, isAiTyping, currentQuestion, totalQuestions, setSessionId, setStatus } = useInterviewStore()

  const { mutate: sendMessage, isPending } = useSendMessage({
    sessionId: sessionId || "",
  })

  const { isLoading, isError, error } = useInterviewMessages(sessionId)

  useEffect(() => {
    if (sessionId) {
      setSessionId(sessionId)
      setStatus("in_progress")
    }
  }, [sessionId, setSessionId, setStatus])

  const handleSendMessage = (messageText: string) => {
    sendMessage(messageText)
  }

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="max-w-md w-full p-6 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full bg-destructive/10">
              <AlertCircle className="h-6 w-6 text-destructive" />
            </div>
          </div>
          <h1 className="text-xl font-semibold mb-2">Invalid Interview Session</h1>
          <p className="text-muted-foreground mb-4">
            No session ID provided. Please return to the interview start page.
          </p>
          <Button asChild>
            <a href="/interview/start">Return to Start</a>
          </Button>
        </Card>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
          <p className="text-muted-foreground">Loading interview...</p>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="max-w-md w-full p-6 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full bg-destructive/10">
              <AlertCircle className="h-6 w-6 text-destructive" />
            </div>
          </div>
          <h1 className="text-xl font-semibold mb-2 text-destructive">Failed to Load Interview</h1>
          <p className="text-muted-foreground mb-4">{error?.message || "Unknown error occurred"}</p>
          <Button variant="outline" asChild>
            <a href="/dashboard">Return to Dashboard</a>
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-muted/30">
      {/* Progress Bar */}
      {totalQuestions > 0 && (
        <div className="border-b bg-background">
          <InterviewProgress current={currentQuestion} total={totalQuestions} />
        </div>
      )}

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden">
        <InterviewChat messages={messages} isTyping={isAiTyping} />

        {isAiTyping && (
          <div className="px-4">
            <TypingIndicator isVisible={isAiTyping} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t bg-background">
        <ChatInput
          onSubmit={handleSendMessage}
          disabled={isPending || isAiTyping}
          placeholder="Type your response..."
        />
      </div>
    </div>
  )
}
