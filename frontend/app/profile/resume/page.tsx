"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import Link from "next/link"
import { FileText, ArrowLeft, AlertCircle, Upload, CheckCircle2, XCircle, Clock, Loader2 } from "lucide-react"
import { useProfile } from "@/hooks/use-profile"
import { useResumeParsingStatus } from "@/hooks/use-profile-mutations"

export default function ResumePage() {
  const { data: profile, isLoading, isError, error } = useProfile()
  const { data: parsingStatus, isLoading: isLoadingStatus } = useResumeParsingStatus(profile?.resume_id)

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (isError || !profile) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error?.message || "Failed to load profile. Please try again."}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  const hasResume = !!profile.resume_id
  const status = parsingStatus?.status

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <Button variant="ghost" size="sm" asChild className="mb-2">
          <Link href="/profile">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Profile
          </Link>
        </Button>
        <h1 className="text-3xl font-bold mb-2">Resume</h1>
        <p className="text-muted-foreground">
          Upload your resume to auto-populate your profile and improve matches
        </p>
      </div>

      {/* Resume Upload Status */}
      <Card>
        <CardHeader>
          <CardTitle>Resume Status</CardTitle>
          <CardDescription>
            {hasResume ? "Your resume is on file" : "No resume uploaded yet"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!hasResume ? (
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="font-semibold mb-2">Resume Upload Coming Soon</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Resume upload functionality will be added in a future update. 
                For now, you can manually add your skills and experience to your profile.
              </p>
              <Button disabled variant="outline">
                <Upload className="mr-2 h-4 w-4" />
                Upload Resume (Coming Soon)
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Resume File Info */}
              <div className="p-4 rounded-lg border bg-muted/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <div className="font-medium">Resume Uploaded</div>
                      <div className="text-sm text-muted-foreground">
                        ID: {profile.resume_id.substring(0, 8)}...
                      </div>
                    </div>
                  </div>
                  {status && (
                    <Badge variant={
                      status === 'completed' ? 'default' :
                      status === 'failed' ? 'destructive' :
                      'secondary'
                    }>
                      {status === 'pending' && <Clock className="h-3 w-3 mr-1" />}
                      {status === 'processing' && <Loader2 className="h-3 w-3 mr-1 animate-spin" />}
                      {status === 'completed' && <CheckCircle2 className="h-3 w-3 mr-1" />}
                      {status === 'failed' && <XCircle className="h-3 w-3 mr-1" />}
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </Badge>
                  )}
                </div>
              </div>

              {/* Parsing Status Details */}
              {isLoadingStatus && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading parsing status...
                </div>
              )}

              {status === 'processing' && (
                <Alert>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <AlertDescription>
                    Analyzing your resume... This may take up to 30 seconds.
                  </AlertDescription>
                </Alert>
              )}

              {status === 'completed' && parsingStatus?.parsed_data && (
                <Card>
                  <CardHeader>
                    <CardTitle>Parsed Information</CardTitle>
                    <CardDescription>
                      Information extracted from your resume
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {parsingStatus.parsed_data.skills && parsingStatus.parsed_data.skills.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-muted-foreground mb-2">
                          Extracted Skills ({parsingStatus.parsed_data.skills.length})
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {parsingStatus.parsed_data.skills.map((skill) => (
                            <Badge key={skill} variant="secondary">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {parsingStatus.parsed_data.experience_years && (
                      <div>
                        <div className="text-sm font-medium text-muted-foreground mb-1">
                          Experience
                        </div>
                        <div className="text-base">
                          {parsingStatus.parsed_data.experience_years} years
                        </div>
                      </div>
                    )}

                    {parsingStatus.parsed_data.education && parsingStatus.parsed_data.education.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-muted-foreground mb-1">
                          Education
                        </div>
                        <ul className="list-disc list-inside text-sm space-y-1">
                          {parsingStatus.parsed_data.education.map((edu, i) => (
                            <li key={i}>{edu}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {parsingStatus.parsed_data.previous_roles && parsingStatus.parsed_data.previous_roles.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-muted-foreground mb-1">
                          Previous Roles
                        </div>
                        <ul className="list-disc list-inside text-sm space-y-1">
                          {parsingStatus.parsed_data.previous_roles.map((role, i) => (
                            <li key={i}>{role}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {status === 'failed' && (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>
                    {parsingStatus?.error_message || "Failed to parse resume. Please try uploading again."}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Resume Benefits</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>• Resume upload contributes 15% to your profile completeness score</p>
          <p>• AI automatically extracts skills, experience, and education</p>
          <p>• Saves time by auto-populating your profile</p>
          <p>• Improves accuracy of job matching</p>
        </CardContent>
      </Card>
    </div>
  )
}
