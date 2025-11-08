"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import Link from "next/link"
import { User, FileText, Briefcase, Mail, Phone, Award, Target, AlertCircle, CheckCircle2 } from "lucide-react"
import { useProfile } from "@/hooks/use-profile"
import { calculateProfileCompleteness, formatEnumArray, formatEnumValue } from "@/lib/profile-utils"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { EditBasicInfoDialog } from "@/components/profile/edit-basic-info-dialog"

export default function ProfilePage() {
  const { data: profile, isLoading, isError, error } = useProfile()

  if (isLoading) {
    return (
      <div className="w-full max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-9 w-48 mb-2" />
            <Skeleton className="h-5 w-64" />
          </div>
        </div>
        <Skeleton className="h-48 w-full" />
        <div className="grid lg:grid-cols-2 gap-6">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  if (isError || !profile) {
    return (
      <div className="w-full max-w-7xl mx-auto space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error?.message || "Failed to load profile. Please try again."}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  const breakdown = calculateProfileCompleteness(profile)

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">My Profile</h1>
          <p className="text-muted-foreground">Manage your professional information</p>
        </div>
      </div>

      {/* Profile Completion */}
      <Card>
        <CardHeader>
          <CardTitle>Profile Completion</CardTitle>
          <CardDescription>Complete your profile to increase your chances of getting matched</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Overall Progress</span>
              <span className="text-sm text-muted-foreground">{breakdown.total}%</span>
            </div>
            <Progress value={breakdown.total} className="h-2" />
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-2 pt-2">
            {breakdown.resume === 0 && (
              <Button variant="outline" size="sm" asChild>
                <Link href="/profile/resume">Upload Resume</Link>
              </Button>
            )}
            {breakdown.skills < 20 && (
              <Button variant="outline" size="sm" asChild>
                <Link href="/profile/skills">Add More Skills</Link>
              </Button>
            )}
            {breakdown.preferences < 20 && (
              <Button variant="outline" size="sm" asChild>
                <Link href="/profile/preferences">Set Job Preferences</Link>
              </Button>
            )}
            {breakdown.total === 100 && (
              <Badge variant="default" className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" />
                Profile Complete!
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <User className="h-5 w-5" />
                <CardTitle>Basic Information</CardTitle>
              </div>
              <EditBasicInfoDialog 
                currentName={profile.full_name} 
                currentPhone={profile.phone}
                currentExperience={profile.experience_years}
              />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Name</div>
              <div className="text-base">{profile.full_name || "Not provided"}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Email</div>
              <div className="flex items-center gap-2 text-base">
                <Mail className="h-4 w-4" />
                {profile.email}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Phone</div>
              <div className="flex items-center gap-2 text-base">
                <Phone className="h-4 w-4" />
                {profile.phone || "Not provided"}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Experience Years</div>
              <div className="flex items-center gap-2 text-base">
                <Briefcase className="h-4 w-4" />
                {profile.experience_years ? `${profile.experience_years} years` : "Not provided"}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Skills */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              <CardTitle>Skills</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">
                {profile.skills.length} {profile.skills.length === 1 ? 'skill' : 'skills'}
              </div>
              {profile.skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {profile.skills.map((skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No skills added yet</p>
              )}
            </div>
            <Button variant="outline" size="sm" asChild className="w-full">
              <Link href="/profile/skills">Manage Skills</Link>
            </Button>
          </CardContent>
        </Card>

        {/* Job Preferences */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              <CardTitle>Job Preferences</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Job Types</div>
              <div className="text-base">
                {profile.preferred_job_types.length > 0 
                  ? formatEnumArray(profile.preferred_job_types)
                  : "Not set"}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Work Setup</div>
              <div className="text-base">{formatEnumValue(profile.preferred_work_setup)}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Salary Range (Annual)</div>
              <div className="text-base">
                {profile.salary_expectation_min && profile.salary_expectation_max
                  ? `${profile.salary_currency} ${profile.salary_expectation_min.toLocaleString()} - ${profile.salary_expectation_max.toLocaleString()}`
                  : "Not set"}
              </div>
            </div>
            <Button variant="outline" size="sm" asChild className="w-full">
              <Link href="/profile/preferences">Update Preferences</Link>
            </Button>
          </CardContent>
        </Card>

        {/* Resume */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              <CardTitle>Resume</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {profile.resume_id ? (
              <div className="p-4 rounded-lg border bg-muted/50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    <span className="font-medium">Resume uploaded</span>
                  </div>
                  <Badge variant="secondary">
                    <Award className="h-3 w-3 mr-1" />
                    On File
                  </Badge>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-lg border border-dashed">
                <p className="text-sm text-muted-foreground text-center">No resume uploaded yet</p>
              </div>
            )}
            <Button variant="outline" size="sm" asChild className="w-full">
              <Link href="/profile/resume">
                {profile.resume_id ? "View Resume Details" : "Upload Resume"}
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
