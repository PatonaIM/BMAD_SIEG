"use client"

import { useEffect, useState } from "react"
import { CheckCircle2, AlertTriangle, Lightbulb, Loader2, RefreshCw } from "lucide-react"
import { useResumeAnalysis } from "@/hooks/use-resumes"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ScoreCard } from "./score-card"
import { AnalysisSection } from "./analysis-section"
import { KeywordChips } from "./keyword-chips"
import { Separator } from "@/components/ui/separator"

interface ResumeAnalysisModalProps {
  resumeId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ResumeAnalysisModal({ resumeId, open, onOpenChange }: ResumeAnalysisModalProps) {
  const [pollingInterval, setPollingInterval] = useState<number | undefined>(2000)

  const { 
    data: analysis, 
    isLoading, 
    isError,
    error,
    refetch 
  } = useResumeAnalysis(resumeId, {
    enabled: open,
    refetchInterval: pollingInterval
  })

  // Stop polling once we have analysis data
  useEffect(() => {
    if (analysis) {
      setPollingInterval(undefined)
    }
  }, [analysis])

  // Re-enable polling when modal reopens
  useEffect(() => {
    if (open && !analysis) {
      setPollingInterval(2000)
    }
  }, [open, analysis])

  const handleReAnalyze = () => {
    // TODO: Implement re-analyze API call
    // For now, just refetch
    refetch()
  }

  const handleDownloadAnalysis = () => {
    if (!analysis) return

    // Create text export of analysis
    const analysisText = `
RESUME ANALYSIS REPORT
Generated: ${new Date(analysis.analyzed_at).toLocaleString()}

OVERALL SCORE: ${analysis.overall_score}/100

STRENGTHS:
${analysis.strengths.map((s, i) => `${i + 1}. ${s}`).join('\n')}

AREAS TO IMPROVE:
${analysis.weaknesses.map((w, i) => `${i + 1}. ${w}`).join('\n')}

ACTIONABLE SUGGESTIONS:
${analysis.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}

MISSING KEYWORDS:
${analysis.keywords_missing.join(', ')}

Analysis Model: ${analysis.analysis_model}
    `.trim()

    // Download as text file
    const blob = new Blob([analysisText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `resume-analysis-${resumeId}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Resume Analysis</DialogTitle>
          <DialogDescription>
            AI-powered feedback to help you improve your resume
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Loading State */}
          {isLoading && !analysis && (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <div className="text-center">
                <p className="font-medium">Analyzing your resume...</p>
                <p className="text-sm text-muted-foreground">This may take a few moments</p>
              </div>
            </div>
          )}

          {/* Error State */}
          {isError && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {error?.message || "Failed to load analysis. The analysis may still be processing."}
              </AlertDescription>
            </Alert>
          )}

          {/* Analysis Results */}
          {analysis && (
            <>
              {/* Overall Score */}
              <ScoreCard score={analysis.overall_score} />

              {/* Strengths */}
              <AnalysisSection
                title="Strengths"
                items={analysis.strengths}
                icon={CheckCircle2}
                variant="success"
              />

              {/* Weaknesses */}
              <AnalysisSection
                title="Areas to Improve"
                items={analysis.weaknesses}
                icon={AlertTriangle}
                variant="warning"
              />

              {/* Suggestions */}
              <AnalysisSection
                title="Actionable Suggestions"
                items={analysis.suggestions}
                icon={Lightbulb}
                variant="info"
              />

              <Separator />

              {/* Missing Keywords */}
              <KeywordChips keywords={analysis.keywords_missing} />

              {/* Actions */}
              <div className="flex items-center justify-between pt-4">
                <p className="text-xs text-muted-foreground">
                  Analyzed on {new Date(analysis.analyzed_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
                <div className="flex gap-2">
                  <Button
                    onClick={handleDownloadAnalysis}
                    variant="outline"
                    size="sm"
                  >
                    Download Analysis
                  </Button>
                  <Button
                    onClick={handleReAnalyze}
                    variant="outline"
                    size="sm"
                    disabled
                  >
                    <RefreshCw className="h-4 w-4 mr-1" />
                    Re-analyze
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
