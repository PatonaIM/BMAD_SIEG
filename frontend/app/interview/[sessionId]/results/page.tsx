"use client"

import { useParams } from "next/navigation"
import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useInterviewStore } from "@/src/features/interview/store/interviewStore"
import { getInterviewTranscript } from "@/src/features/interview/services/interviewService"
import type { InterviewCompleteResponse } from "@/src/features/interview/services/interviewService"
import { CheckCircle2, Clock, MessageSquare, TrendingUp, FileText, Star, Target, Lightbulb, Award } from "lucide-react"

export default function InterviewResultsPage() {
  const params = useParams()
  const sessionId = params?.sessionId as string | undefined

  const { completionData, setCompletionData } = useInterviewStore()
  const [isLoadingData, setIsLoadingData] = useState(false)

  // Fetch completion data - try completion endpoint first, then fall back to transcript
  useEffect(() => {
    console.log("[Results] Current completionData:", completionData)
    
    const fetchCompletionData = async () => {
      if (sessionId && !completionData && !isLoadingData) {
        console.log("[Results] No completion data in store, calling completion endpoint...")
        setIsLoadingData(true)
        try {
          // FIRST: Try calling completion endpoint to generate enhanced feedback
          const { completeInterview } = await import('@/src/features/interview/services/interviewService')
          console.log("[Results] Calling completion endpoint for interview:", sessionId)
          const data = await completeInterview(sessionId)
          console.log("[Results] Completion endpoint returned data:", data)
          
          // Store the enhanced completion data
          setCompletionData({
            interview_id: data.interview_id,
            completed_at: data.completed_at,
            duration_seconds: data.duration_seconds,
            questions_answered: data.questions_answered,
            skill_boundaries_identified: data.skill_boundaries_identified || 0,
            message: data.message,
            skill_assessments: data.skill_assessments || [],
            highlights: data.highlights || [],
            growth_areas: data.growth_areas || []
          })
          
          console.log("[Results] Enhanced completion data stored:", {
            hasSkillAssessments: !!data.skill_assessments?.length,
            hasHighlights: !!data.highlights?.length,
            hasGrowthAreas: !!data.growth_areas?.length
          })
        } catch (completionError) {
          console.error("[Results] Completion endpoint failed, falling back to transcript:", completionError)
          
          // FALLBACK: Use transcript if completion endpoint fails
          try {
            const transcript = await getInterviewTranscript(sessionId)
            const candidateMessages = transcript.messages.filter(m => m.message_type === "candidate_response")
            
            const fallbackData: InterviewCompleteResponse = {
              interview_id: transcript.interview_id,
              completed_at: transcript.completed_at || new Date().toISOString(),
              duration_seconds: transcript.duration_seconds || 0,
              questions_answered: candidateMessages.length,
              skill_boundaries_identified: 0,
              message: "Interview completed successfully",
              skill_assessments: [],
              highlights: [],
              growth_areas: []
            }
            
            console.log("[Results] Built fallback completion data from transcript:", fallbackData)
            setCompletionData(fallbackData)
          } catch (transcriptError) {
            console.error("[Results] Failed to fetch transcript:", transcriptError)
          }
        } finally {
          setIsLoadingData(false)
        }
      } else if (completionData) {
        console.log("[Results] Using completion data from store:", {
          hasSkillAssessments: !!completionData.skill_assessments?.length,
          hasHighlights: !!completionData.highlights?.length,
          hasGrowthAreas: !!completionData.growth_areas?.length
        })
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

  // Helper to get proficiency color and label
  const getProficiencyDetails = (level: string) => {
    const details = {
      expert: { color: "text-green-600 bg-green-50 border-green-200", label: "Expert", progress: 100 },
      proficient: { color: "text-blue-600 bg-blue-50 border-blue-200", label: "Proficient", progress: 75 },
      intermediate: { color: "text-yellow-600 bg-yellow-50 border-yellow-200", label: "Intermediate", progress: 50 },
      novice: { color: "text-orange-600 bg-orange-50 border-orange-200", label: "Beginner", progress: 25 }
    }
    return details[level as keyof typeof details] || details.novice
  }

  // Generate default highlights if backend returned empty array
  const highlights = completionData.highlights && completionData.highlights.length > 0 
    ? completionData.highlights 
    : [{
        title: completionData.questions_answered >= 10 
          ? "Great Engagement"
          : completionData.questions_answered >= 5
          ? "Active Participation"
          : "Good Start",
        description: completionData.questions_answered >= 10
          ? `You actively participated throughout the interview, answering ${completionData.questions_answered} questions with thoughtful responses`
          : completionData.questions_answered >= 5
          ? `You engaged well with the interview process, answering ${completionData.questions_answered} questions thoughtfully`
          : `You began the interview process and provided ${completionData.questions_answered} response${completionData.questions_answered > 1 ? 's' : ''}. Every interview is a learning opportunity!`,
        skill_area: null
      }]

  // Generate default growth areas if backend returned empty array
  const growthAreas = completionData.growth_areas && completionData.growth_areas.length > 0
    ? completionData.growth_areas
    : [
        {
          display_name: "Complete Full Assessment",
          suggestion: "Complete a full interview session to get detailed skill assessments and personalized feedback on your technical abilities.",
          skill_area: null
        },
        {
          display_name: "Communication Skills",
          suggestion: "Practice articulating your thought process clearly when answering technical questions. This helps interviewers understand your problem-solving approach.",
          skill_area: null
        },
        {
          display_name: "Core Fundamentals",
          suggestion: "Review fundamental concepts in your target role. Strong foundational knowledge helps you tackle more complex problems with confidence.",
          skill_area: null
        }
      ]

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
          <h1 className="text-3xl font-bold mb-2">Great Work!</h1>
          <p className="text-muted-foreground text-lg">
            Here&apos;s what we learned about your skills
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
            <p className="text-3xl font-bold">{completionData.skill_assessments?.length || completionData.skill_boundaries_identified}</p>
          </Card>
        </div>

        {/* Interview Highlights */}
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Award className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-semibold">Your Strengths</h2>
          </div>
          <div className="space-y-4">
            {highlights.map((highlight, index) => (
              <div key={index} className="flex items-start gap-3 p-4 rounded-lg bg-green-50 border border-green-200">
                <Star className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-green-900 mb-1">{highlight.title}</h3>
                  <p className="text-sm text-green-800">{highlight.description}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Skills Breakdown */}
        {completionData.skill_assessments && completionData.skill_assessments.length > 0 && (
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Target className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">Skills Breakdown</h2>
            </div>
            <div className="space-y-4">
              {completionData.skill_assessments.map((skill, index) => {
                const profDetails = getProficiencyDetails(skill.proficiency_level)
                return (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{skill.display_name}</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium border ${profDetails.color}`}>
                        {profDetails.label}
                      </span>
                    </div>
                    <Progress value={profDetails.progress} className="h-2" />
                  </div>
                )
              })}
            </div>
          </Card>
        )}

        {/* Growth Areas */}
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-semibold">Areas for Growth</h2>
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            Here are some suggestions to help you improve:
          </p>
          <div className="space-y-4">
            {growthAreas.map((area, index) => (
              <div key={index} className="flex items-start gap-3 p-4 rounded-lg bg-blue-50 border border-blue-200">
                <Target className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-blue-900 mb-1">{area.display_name}</h3>
                  <p className="text-sm text-blue-800">{area.suggestion}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

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
