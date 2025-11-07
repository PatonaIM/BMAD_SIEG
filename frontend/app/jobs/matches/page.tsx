"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import Link from "next/link"
import { 
  Sparkles, 
  Target, 
  MapPin, 
  DollarSign, 
  Briefcase, 
  Settings2, 
  ChevronDown,
  CheckCircle2,
  AlertCircle
} from "lucide-react"
import { useProfile } from "@/hooks/use-profile"
import { useJobMatches } from "@/hooks/use-job-matches"
import { useMatchExplanation } from "@/hooks/use-match-explanation"
import { useMatchingStore } from "@/stores/matching-store"
import type { JobMatch, MatchClassification } from "@/types/matching"

/**
 * Get badge color based on match classification
 */
function getMatchBadgeColor(classification: MatchClassification): string {
  switch (classification) {
    case 'Excellent':
      return 'bg-green-500/10 text-green-700 border-green-500/20'
    case 'Great':
      return 'bg-blue-500/10 text-blue-700 border-blue-500/20'
    case 'Good':
      return 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20'
    case 'Fair':
      return 'bg-orange-500/10 text-orange-700 border-orange-500/20'
  }
}

/**
 * Job Match Card Component
 */
function JobMatchCard({ job }: { job: JobMatch }) {
  const { toggleExplanation, isExplanationExpanded } = useMatchingStore()
  const isExpanded = isExplanationExpanded(job.id)
  const { data: explanation, isLoading: explanationLoading } = useMatchExplanation(job.id, isExpanded)

  // Format salary
  const salaryDisplay = job.salary_min && job.salary_max 
    ? `$${(job.salary_min / 1000).toFixed(0)}k - $${(job.salary_max / 1000).toFixed(0)}k`
    : 'Salary not specified'

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <CardTitle className="text-xl">{job.title}</CardTitle>
              <Badge 
                variant="outline" 
                className={getMatchBadgeColor(job.match_classification)}
                aria-label={`${job.match_classification} match`}
              >
                <Sparkles className="h-3 w-3 mr-1" />
                {job.match_score}% Match
              </Badge>
            </div>
            <CardDescription className="text-base">{job.company}</CardDescription>
          </div>
          <Button asChild>
            <Link href={`/jobs/${job.id}`}>View & Apply</Link>
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Match Score Progress */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Match Score</span>
            <span className="text-sm text-muted-foreground">{job.match_score}%</span>
          </div>
          <Progress value={job.match_score} className="h-2" />
        </div>

        {/* Collapsible Match Explanation */}
        <Collapsible open={isExpanded} onOpenChange={() => toggleExplanation(job.id)}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="w-full justify-between">
              <span className="text-sm font-medium">Why this matches you</span>
              <ChevronDown className={`h-4 w-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="space-y-3 pt-3">
            {explanationLoading && (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-4/6" />
              </div>
            )}
            {explanation && (
              <>
                {/* Matching Factors */}
                {explanation.matching_factors.length > 0 && (
                  <div>
                    <div className="text-sm font-medium mb-2 flex items-center gap-1">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      What Aligns
                    </div>
                    <ul className="space-y-1">
                      {explanation.matching_factors.map((factor, index) => (
                        <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-green-600 mt-0.5">•</span>
                          {factor}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Missing Requirements */}
                {explanation.missing_requirements.length > 0 && (
                  <div>
                    <div className="text-sm font-medium mb-2 flex items-center gap-1">
                      <AlertCircle className="h-4 w-4 text-orange-600" />
                      Areas to Develop
                    </div>
                    <ul className="space-y-1">
                      {explanation.missing_requirements.map((requirement, index) => (
                        <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-orange-600 mt-0.5">•</span>
                          {requirement}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Overall Reasoning */}
                {explanation.overall_reasoning && (
                  <div>
                    <div className="text-sm font-medium mb-2">Summary</div>
                    <p className="text-sm text-muted-foreground">{explanation.overall_reasoning}</p>
                  </div>
                )}
              </>
            )}
          </CollapsibleContent>
        </Collapsible>

        {/* Job Details */}
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground pt-2 border-t">
          <div className="flex items-center gap-1">
            <MapPin className="h-4 w-4" />
            {job.location}
          </div>
          <div className="flex items-center gap-1">
            <Briefcase className="h-4 w-4" />
            {job.employment_type}
          </div>
          <div className="flex items-center gap-1">
            <DollarSign className="h-4 w-4" />
            {salaryDisplay}
          </div>
        </div>

        {/* Skills */}
        {job.required_skills && job.required_skills.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {job.required_skills.map((skill) => (
              <Badge key={skill} variant="outline">
                {skill}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function JobMatchesPage() {
  const { currentPage, setCurrentPage } = useMatchingStore()
  const { data: profile, isLoading: profileLoading } = useProfile()
  const { data: matchesData, isLoading: matchesLoading, isError: matchesError } = useJobMatches(currentPage, 20)

  // Loading state
  if (profileLoading || matchesLoading) {
    return (
      <div className="w-full max-w-7xl mx-auto space-y-6">
        <Skeleton className="h-12 w-64" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  // Profile completeness gate
  if (profile && profile.profile_completeness_score < 40) {
    return (
      <div className="w-full max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">AI Job Matches</h1>
          <p className="text-muted-foreground">
            Personalized job recommendations based on your profile
          </p>
        </div>
        
        <Card className="p-8 text-center border-orange-500/20 bg-orange-50/50 dark:bg-orange-950/20">
          <div className="flex justify-center mb-4">
            <div className="p-4 rounded-full bg-orange-100 dark:bg-orange-900/30">
              <AlertCircle className="h-8 w-8 text-orange-600 dark:text-orange-500" />
            </div>
          </div>
          <h3 className="text-xl font-semibold mb-2">Complete Your Profile to Unlock AI Matching</h3>
          <p className="text-muted-foreground mb-4">
            You need at least 40% profile completeness to access AI job matching features.
            Currently at {profile.profile_completeness_score}%.
          </p>
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Profile Completeness</span>
              <span className="text-sm text-muted-foreground">{profile.profile_completeness_score}%</span>
            </div>
            <Progress value={profile.profile_completeness_score} className="h-2" />
          </div>
          <Button asChild size="lg">
            <Link href="/profile">
              Complete Profile
            </Link>
          </Button>
        </Card>
      </div>
    )
  }

  // Error state
  if (matchesError) {
    return (
      <div className="w-full max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">AI Job Matches</h1>
          <p className="text-muted-foreground">
            Personalized job recommendations based on your profile
          </p>
        </div>
        
        <Card className="p-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-4 rounded-full bg-red-100 dark:bg-red-900/30">
              <AlertCircle className="h-8 w-8 text-red-600 dark:text-red-500" />
            </div>
          </div>
          <h3 className="text-xl font-semibold mb-2">Unable to Load Matches</h3>
          <p className="text-muted-foreground mb-6">
            There was an error loading your job matches. Please try again later.
          </p>
          <Button onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Card>
      </div>
    )
  }

  const matchedJobs = matchesData?.jobs || []
  const hasMorePages = matchesData && matchesData.total > currentPage * 20

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">AI Job Matches</h1>
          <p className="text-muted-foreground">
            Personalized job recommendations based on your profile and preferences
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/profile">
            <Settings2 className="mr-2 h-4 w-4" />
            Preferences
          </Link>
        </Button>
      </div>

      {/* Matching Status Card */}
      {matchedJobs.length > 0 && (
        <Card className="bg-gradient-to-br from-accent/10 to-primary/10 border-accent/20">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent/20">
                <Sparkles className="h-5 w-5 text-accent" />
              </div>
              <div>
                <CardTitle>AI Job Matching Active</CardTitle>
                <CardDescription>Finding opportunities that match your profile</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-accent" />
                <span>
                  <strong>{matchesData?.total || 0}</strong> total matches found
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-accent" />
                <span>Updated daily with new opportunities</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Matched Jobs List */}
      {matchedJobs.length > 0 && (
        <div className="space-y-4">
          {matchedJobs.map((job) => (
            <JobMatchCard key={job.id} job={job} />
          ))}
        </div>
      )}

      {/* Load More Button */}
      {hasMorePages && (
        <div className="flex justify-center">
          <Button 
            variant="outline" 
            size="lg"
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Load More Matches
          </Button>
        </div>
      )}

      {/* Empty State */}
      {matchedJobs.length === 0 && !matchesError && (
        <Card className="p-12 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-4 rounded-full bg-muted">
              <Target className="h-8 w-8 text-muted-foreground" />
            </div>
          </div>
          <h3 className="text-xl font-semibold mb-2">No Matches Yet</h3>
          <p className="text-muted-foreground mb-6">
            We haven't found any matching jobs yet. Try updating your preferences or skills to discover more opportunities.
          </p>
          <div className="flex gap-3 justify-center">
            <Button asChild variant="outline">
              <Link href="/profile">
                Update Profile
              </Link>
            </Button>
            <Button asChild>
              <Link href="/jobs">
                Browse All Jobs
              </Link>
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
