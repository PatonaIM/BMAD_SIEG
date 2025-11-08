"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { AlertCircle, FileText } from "lucide-react"
import { useResumes } from "@/hooks/use-resumes"
import { ResumeUpload } from "@/components/profile/resume-upload"
import { ResumeList } from "@/components/profile/resume-list"

export default function ResumePage() {
  const { data: resumes, isLoading, isError, error } = useResumes()

  if (isLoading) {
    return (
      <div className="w-full max-w-5xl mx-auto space-y-6">
        <Skeleton className="h-9 w-48 mb-2" />
        <Skeleton className="h-5 w-64 mb-6" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="w-full max-w-5xl mx-auto space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error?.message || "Failed to load resumes. Please try again."}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  const hasResumes = resumes && resumes.length > 0

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Resume Management</h1>
        <p className="text-muted-foreground">
          Upload your resume and receive AI-powered feedback to improve your job matching
        </p>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            <CardTitle>Upload Resume</CardTitle>
          </div>
          <CardDescription>
            Upload a PDF version of your resume. AI analysis will automatically provide feedback.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResumeUpload />
        </CardContent>
      </Card>

      {/* Resumes List */}
      {hasResumes && (
        <Card>
          <CardHeader>
            <CardTitle>Your Resumes</CardTitle>
            <CardDescription>
              {resumes.length} {resumes.length === 1 ? 'resume' : 'resumes'} uploaded
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResumeList resumes={resumes} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
