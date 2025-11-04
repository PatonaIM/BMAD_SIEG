"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useAuthStore } from "@/src/features/auth/store/authStore"
import { useLogout } from "@/src/features/auth/hooks/useAuth"
import { useStartInterview } from "@/src/features/interview/hooks/useInterview"
import { BrainCircuit, Sparkles, CheckCircle2, Mic, MessageSquare, BarChart3 } from "lucide-react"
import Link from "next/link"
import { MockModeIndicator } from "@/src/components/shared/MockModeIndicator"

export default function InterviewStartPage() {
  const user = useAuthStore((state) => state.user)
  const logout = useLogout()
  const { mutate: startInterview, isPending, isError, error } = useStartInterview()

  const handleBeginInterview = () => {
    startInterview({
      role_type: "react",
      resume_id: null,
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container mx-auto max-w-4xl py-12">
        <MockModeIndicator />

        {/* Header */}
        <div className="text-center mb-12">
          <Badge variant="secondary" className="mb-4">
            <Sparkles className="mr-1 h-3 w-3" />
            AI-Powered Interview
          </Badge>
          <h1 className="text-4xl font-bold mb-4">Ready to Begin Your Interview?</h1>
          <p className="text-lg text-muted-foreground">
            Hello, {user?.email || "Candidate"}! Let's showcase your skills with our AI interviewer.
          </p>
        </div>

        {/* Main Card */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-lg bg-accent/10">
                <BrainCircuit className="h-6 w-6 text-accent" />
              </div>
              <div>
                <CardTitle>AI Technical Interview</CardTitle>
                <CardDescription>Speech-to-speech conversation with intelligent follow-ups</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Features */}
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-start gap-3 p-4 rounded-lg border bg-card">
                <Mic className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <div className="font-semibold text-sm mb-1">Voice Interaction</div>
                  <div className="text-xs text-muted-foreground">Natural conversation with AI</div>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 rounded-lg border bg-card">
                <MessageSquare className="h-5 w-5 text-accent mt-0.5" />
                <div>
                  <div className="font-semibold text-sm mb-1">Smart Questions</div>
                  <div className="text-xs text-muted-foreground">Adaptive follow-up queries</div>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 rounded-lg border bg-card">
                <BarChart3 className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <div className="font-semibold text-sm mb-1">Auto Scoring</div>
                  <div className="text-xs text-muted-foreground">Real-time performance analysis</div>
                </div>
              </div>
            </div>

            {/* What to Expect */}
            <div>
              <h3 className="font-semibold mb-3">What to Expect</h3>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-accent mt-0.5" />
                  <span className="text-sm">15-20 technical questions tailored to your role</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-accent mt-0.5" />
                  <span className="text-sm">Natural conversation flow with AI interviewer</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-accent mt-0.5" />
                  <span className="text-sm">Approximately 30-45 minutes duration</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-accent mt-0.5" />
                  <span className="text-sm">Instant feedback and scoring upon completion</span>
                </li>
              </ul>
            </div>

            {/* Error Message */}
            {isError && (
              <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive">
                <p className="text-sm font-medium">Failed to start interview</p>
                <p className="text-xs mt-1">{error?.message || "Unknown error occurred"}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4">
              <Button size="lg" onClick={handleBeginInterview} disabled={isPending} className="flex-1">
                {isPending ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Starting Interview...
                  </>
                ) : (
                  <>
                    <BrainCircuit className="mr-2 h-4 w-4" />
                    Begin Interview
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={logout} disabled={isPending}>
                Sign Out
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Tips Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Interview Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>• Find a quiet environment with good internet connection</li>
              <li>• Speak clearly and take your time to think through answers</li>
              <li>• Be specific and provide examples when possible</li>
              <li>• Don't worry about perfection - the AI adapts to your responses</li>
            </ul>
          </CardContent>
        </Card>

        {/* Back Link */}
        <div className="text-center mt-8">
          <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
