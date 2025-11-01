"use client"

import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import { InterviewTranscript } from "@/src/features/interview/components/InterviewTranscript"

export default function InterviewTranscriptPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params?.sessionId as string | undefined

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-xl font-semibold mb-2">Invalid Session</h1>
          <p className="text-muted-foreground mb-4">No session ID provided.</p>
          <Button onClick={() => router.push("/dashboard")}>Return to Dashboard</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-muted/30 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header with back button */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </div>

        {/* Transcript Component */}
        <InterviewTranscript interviewId={sessionId} />
      </div>
    </div>
  )
}
