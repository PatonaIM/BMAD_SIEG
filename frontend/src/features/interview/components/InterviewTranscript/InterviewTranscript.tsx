"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot, User, Download, Loader2 } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { useInterviewTranscript } from "../../hooks/useInterviewCompletion"
import type { TranscriptMessage } from "../../services/interviewService"

export interface InterviewTranscriptProps {
  interviewId: string
}

/**
 * InterviewTranscript Component
 * Displays the full interview conversation history
 * - Shows all messages in chronological order
 * - Visual distinction between AI and candidate messages
 * - Scrollable for long conversations
 * - Export functionality (to be implemented in future story)
 * - Responsive design for mobile and desktop
 */
export const InterviewTranscript = ({ interviewId }: InterviewTranscriptProps) => {
  const { data: transcript, isLoading, error } = useInterviewTranscript(interviewId)

  // Format timestamp
  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  // Format duration
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return "N/A"
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes} min ${secs} sec`
  }

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading transcript...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center gap-2">
            <p className="text-sm text-destructive">Failed to load transcript</p>
            <p className="text-xs text-muted-foreground">{error.message}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!transcript || !transcript.messages || transcript.messages.length === 0) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">No messages found</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>Interview Transcript</CardTitle>
            <CardDescription>
              {transcript.started_at && `Started ${formatTimestamp(transcript.started_at)}`}
              {transcript.duration_seconds && ` • Duration: ${formatDuration(transcript.duration_seconds)}`}
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" disabled>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[600px] pr-4">
          <div className="space-y-6">
            {transcript.messages.map((message: TranscriptMessage, index: number) => (
              <TranscriptMessageItem key={`${message.sequence_number}-${index}`} message={message} />
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

/**
 * TranscriptMessageItem Component
 * Renders a single message in the transcript
 */
interface TranscriptMessageItemProps {
  message: TranscriptMessage
}

const TranscriptMessageItem = ({ message }: TranscriptMessageItemProps) => {
  const isAI = message.message_type === "ai_question"

  // Format timestamp
  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Avatar className={`w-8 h-8 ${isAI ? "bg-primary" : "bg-secondary"}`}>
          <AvatarFallback className={isAI ? "bg-primary text-primary-foreground" : "bg-secondary"}>
            {isAI ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <div className="flex items-baseline gap-2">
            <p className="text-sm font-semibold">{isAI ? "AI Interviewer" : "You"}</p>
            <p className="text-xs text-muted-foreground">{formatTime(message.created_at)}</p>
          </div>
        </div>
      </div>
      <div className={`ml-10 p-3 rounded-lg ${isAI ? "bg-primary/5" : "bg-secondary/50"}`}>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content_text}</p>
      </div>
      {message.sequence_number < 999 && <Separator className="my-4" />}
    </div>
  )
}
