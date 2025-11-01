"use client"

import { useParams } from "next/navigation"
import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useInterviewStore } from "@/src/features/interview/store/interviewStore"
import { getInterviewTranscript } from "@/src/features/interview/services/interviewService"
import type { InterviewCompleteResponse } from "@/src/features/interview/services/interviewService"
import { CheckCircle2, Clock, MessageSquare, TrendingUp, FileText } from "lucide-react"

export default function InterviewResultsPage() {
  const params = useParams()
  const sessionId = params?.sessionId as string | undefined

  const { completionData, setCompletionData } = useInterviewStore()
  const [isLoadingData, setIsLoadingData] = useState(false)

  // Fetch completion data from transcript if not in store
  useEffect(() => {
    const fetchCompletionData = async () => {
      if (sessionId && !completionData && !isLoadingData) {
        setIsLoadingData(true)
        try {
          // Fetch transcript to get interview completion data
          const transcript = await getInterviewTranscript(sessionId)
          
          // Calculate metrics from transcript
          const candidateMessages = transcript.messages.filter(m => m.message_type === "candidate_response")
          
          // Build completion data from transcript
          const data: InterviewCompleteResponse = {
            interview_id: transcript.interview_id,
            completed_at: transcript.completed_at || new Date().toISOString(),
            duration_seconds: transcript.duration_seconds || 0,
            questions_answered: candidateMessages.length,
            skill_boundaries_identified: 0, // We don't have this in transcript, default to 0
            message: "Interview completed successfully"
          }
          
          setCompletionData(data)
        } catch (error) {
          console.error("[Results] Failed to fetch completion data:", error)
        } finally {
          setIsLoadingData(false)
        }
      }
    }

    fetchCompletionData()
  }, [sessionId, completionData, setCompletionData, isLoadingData])

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="max-w-md w-full p-6 text-center">
          <h1 className="text-xl font-semibold mb-2">Invalid Session</h1>
          <p className="text-muted-foreground mb-4">No session ID provided.</p>
          <Button asChild>
            <a href="/dashboard">Return to Dashboard</a>
          </Button>
        </Card>
      </div>
    )
  }

  if (isLoadingData || !completionData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
          <p className="text-muted-foreground">Loading completion data...</p>
        </div>
      </div>
    )
  }

  // Format duration as "X minutes Y seconds"
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins} min ${secs} sec`
  }

  // Format completion timestamp
  const completionDate = new Date(completionData.completed_at).toLocaleString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })

  return (
    <div className="min-h-screen bg-muted/30 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Success Header */}
        <Card className="p-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-4 rounded-full bg-primary/10">
              <CheckCircle2 className="h-12 w-12 text-primary" />
            </div>
          </div>
          <h1 className="text-3xl font-bold mb-2">Thank You!</h1>
          <p className="text-muted-foreground text-lg">
            Your interview has been completed successfully.
          </p>
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <MessageSquare className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold">Questions Answered</h3>
            </div>
            <p className="text-3xl font-bold">{completionData.questions_answered}</p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <Clock className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold">Duration</h3>
            </div>
            <p className="text-3xl font-bold">{formatDuration(completionData.duration_seconds)}</p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <TrendingUp className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold">Skills Assessed</h3>
            </div>
            <p className="text-3xl font-bold">{completionData.skill_boundaries_identified}</p>
          </Card>
        </div>

        {/* Next Steps */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">What&apos;s Next?</h2>
          <div className="space-y-3 mb-6">
            <div className="flex items-start gap-3">
              <div className="mt-1 h-2 w-2 rounded-full bg-primary shrink-0" />
              <p className="text-muted-foreground">
                Your responses are being analyzed by our AI assessment system.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-1 h-2 w-2 rounded-full bg-primary shrink-0" />
              <p className="text-muted-foreground">
                You&apos;ll receive an email notification with your results within 24 hours.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-1 h-2 w-2 rounded-full bg-primary shrink-0" />
              <p className="text-muted-foreground">
                Check your dashboard to view your interview history and results.
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button asChild className="flex-1">
              <a href="/dashboard">Return to Dashboard</a>
            </Button>
            <Button
              asChild
              variant="outline"
              className="flex-1"
            >
              <a href={`/interview/${sessionId}/transcript`} className="flex items-center gap-2 justify-center">
                <FileText className="h-4 w-4" />
                View Transcript
              </a>
            </Button>
          </div>
        </Card>

        {/* Interview Summary */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Interview Summary</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Interview ID</p>
              <p className="font-mono text-sm">{completionData.interview_id}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Status</p>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                <CheckCircle2 className="h-4 w-4" />
                Completed
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Completion Time</p>
              <p className="text-sm">{completionDate}</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
