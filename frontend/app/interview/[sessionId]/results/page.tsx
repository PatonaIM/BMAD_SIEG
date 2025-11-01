"use client"

import { useParams, useRouter } from "next/navigation"
import { useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useInterviewStore } from "@/src/features/interview/store/interviewStore"
import { CheckCircle2, Clock, MessageSquare, TrendingUp } from "lucide-react"

export default function InterviewResultsPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params?.sessionId as string | undefined

  const { messages, currentQuestion, totalQuestions, status } = useInterviewStore()

  useEffect(() => {
    // Redirect if interview is not completed
    if (status !== "completed") {
      console.log("[v0] Interview not completed, redirecting...")
      router.push(`/interview/${sessionId}`)
    }
  }, [status, sessionId, router])

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

  const candidateMessages = messages.filter((m) => m.role === "candidate")
  const estimatedDuration = Math.ceil(candidateMessages.length * 2.5) // Rough estimate

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
          <h1 className="text-3xl font-bold mb-2">Interview Complete!</h1>
          <p className="text-muted-foreground text-lg">
            Great job! You've successfully completed all {totalQuestions} questions.
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
            <p className="text-3xl font-bold">
              {currentQuestion}/{totalQuestions}
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <Clock className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold">Estimated Duration</h3>
            </div>
            <p className="text-3xl font-bold">{estimatedDuration} min</p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <TrendingUp className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold">Total Responses</h3>
            </div>
            <p className="text-3xl font-bold">{candidateMessages.length}</p>
          </Card>
        </div>

        {/* Next Steps */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">What's Next?</h2>
          <div className="space-y-3 mb-6">
            <div className="flex items-start gap-3">
              <div className="mt-1 h-2 w-2 rounded-full bg-primary flex-shrink-0" />
              <p className="text-muted-foreground">
                Your interview responses have been recorded and will be reviewed by our team.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-1 h-2 w-2 rounded-full bg-primary flex-shrink-0" />
              <p className="text-muted-foreground">You'll receive feedback and results within 2-3 business days.</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="mt-1 h-2 w-2 rounded-full bg-primary flex-shrink-0" />
              <p className="text-muted-foreground">Check your dashboard for updates on your interview status.</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button asChild className="flex-1">
              <a href="/dashboard">Return to Dashboard</a>
            </Button>
            <Button asChild variant="outline" className="flex-1 bg-transparent">
              <a href="/interview/practice">Practice More</a>
            </Button>
          </div>
        </Card>

        {/* Interview Summary */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Interview Summary</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Session ID</p>
              <p className="font-mono text-sm">{sessionId}</p>
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
              <p className="text-sm">{new Date().toLocaleString()}</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
