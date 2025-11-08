"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuthStore } from "@/src/features/auth/store/authStore"
import { useStartInterview } from "@/src/features/interview/hooks/useInterview"
import { useApplication } from "@/hooks/use-application"
import { BrainCircuit, Sparkles, CheckCircle2, Mic, MessageSquare, BarChart3, AlertCircle, Briefcase, Building2 } from "lucide-react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { MockModeIndicator } from "@/src/components/shared/MockModeIndicator"
import type { Application } from "@/lib/api-client"

/**
 * Get tech stack-specific preparation tips
 */
function getPreparationTips(techStack: string | null): string[] {
  const stack = techStack?.toLowerCase() || 'unknown'
  
  const tipsMap: Record<string, string[]> = {
    react: [
      "Review component lifecycle and hooks (useState, useEffect, useContext)",
      "Practice state management patterns (Redux, Zustand, Context API)",
      "Be ready for JSX/TypeScript questions and component composition"
    ],
    python: [
      "Brush up on list comprehensions and decorators",
      "Review OOP concepts and design patterns",
      "Practice algorithm questions and data structures"
    ],
    javascript: [
      "Review closures and async/await patterns",
      "Practice DOM manipulation and event handling",
      "Be ready for ES6+ features (arrow functions, destructuring, modules)"
    ],
    typescript: [
      "Review type system and generics",
      "Practice interface and type definitions",
      "Be ready for advanced type patterns (utility types, conditional types)"
    ],
    go: [
      "Review goroutines and channels for concurrency",
      "Practice error handling patterns",
      "Be ready for questions about interfaces and composition"
    ],
    node: [
      "Review async patterns and event loop",
      "Practice Express/Fastify framework concepts",
      "Be ready for questions about streams and buffers"
    ],
    nodejs: [
      "Review async patterns and event loop",
      "Practice Express/Fastify framework concepts",
      "Be ready for questions about streams and buffers"
    ],
  }
  
  return tipsMap[stack] || [
    "Review core programming concepts and best practices",
    "Practice problem-solving and algorithmic thinking",
    "Be ready for technical discussions about your experience"
  ]
}

/**
 * Job Context Card - displays job details for application-linked interviews
 */
function JobContextCard({ application }: { application: Application }) {
  const { job_posting } = application
  const tips = getPreparationTips(job_posting.tech_stack)
  const techStackDisplay = job_posting.tech_stack || 'Technical'
  
  return (
    <Card className="mb-6 border-primary bg-accent/5">
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Briefcase className="h-5 w-5 text-primary" />
          </div>
          <div className="flex-1">
            <CardTitle className="text-xl">Interview for {job_posting.title}</CardTitle>
            <CardDescription className="flex items-center gap-2 mt-1">
              <Building2 className="h-3 w-3" />
              {job_posting.company} • {job_posting.role_category}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Tech Stack Badge */}
        <div>
          <Badge variant="secondary" className="text-sm">
            {techStackDisplay}
          </Badge>
        </div>
        
        {/* Preparation Tips */}
        <div>
          <h3 className="font-semibold text-sm mb-2">
            What to prepare for {techStackDisplay} interview:
          </h3>
          <ul className="space-y-1.5">
            {tips.map((tip, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                <CheckCircle2 className="h-3.5 w-3.5 text-accent mt-0.5 shrink-0" />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}

export default function InterviewStartPage() {
  const searchParams = useSearchParams()
  const applicationId = searchParams.get('application_id')
  
  const user = useAuthStore((state) => state.user)
  const { mutate: startInterview, isPending, isError, error } = useStartInterview()
  
  const { 
    data: application, 
    isLoading: isLoadingApp, 
    isError: isAppError, 
    error: appError 
  } = useApplication(applicationId)

  const handleBeginInterview = () => {
    // When application_id provided, role_type derived from job on backend
    startInterview({
      role_type: applicationId ? null : "react",
      resume_id: null,
      application_id: applicationId || null,
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

        {/* Loading State for Application */}
        {isLoadingApp && applicationId && (
          <Card className="mb-6 p-6">
            <Skeleton className="h-8 w-3/4 mb-4" />
            <Skeleton className="h-4 w-1/2 mb-2" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
          </Card>
        )}

        {/* Error State for Application */}
        {isAppError && applicationId && (
          <Card className="mb-6 p-6 border-destructive bg-destructive/5">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-destructive mb-1">
                  Unable to Load Application
                </h3>
                <p className="text-sm text-muted-foreground">
                  {appError?.message || 'The application could not be found or you do not have access to it.'}
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="mt-3"
                  onClick={() => window.location.href = '/applications'}
                >
                  View My Applications
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Job Context Card - only show when application loaded successfully */}
        {application && !isLoadingApp && (
          <JobContextCard application={application} />
        )}

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
              <Button size="lg" onClick={handleBeginInterview} disabled={isPending} className="w-full">
                {isPending ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Starting Interview...
                  </>
                ) : (
                  <>
                    <BrainCircuit className="mr-2 h-4 w-4" />
                    {application 
                      ? `Begin ${application.job_posting.tech_stack || 'Technical'} Interview`
                      : 'Begin Interview'
                    }
                  </>
                )}
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
