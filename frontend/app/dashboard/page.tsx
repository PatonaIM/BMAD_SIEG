"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import Link from "next/link"
import {
  BrainCircuit,
  Briefcase,
  FileText,
  Target,
  TrendingUp,
  Calendar,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Clock,
  AlertCircle,
} from "lucide-react"
import { useApplications } from "@/hooks/use-applications"
import { useProfile } from "@/hooks/use-profile"
import { useJobMatches } from "@/hooks/use-job-matches"
import { calculateProfileCompleteness } from "@/lib/profile-utils"
import { useAuthStore } from "@/src/features/auth/store/authStore"
import type { ApplicationStatus } from "@/lib/api-client"

/**
 * Format applied date as relative time
 */
function formatAppliedDate(appliedAt: string): string {
  const date = new Date(appliedAt);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return `${Math.floor(diffDays / 30)} months ago`;
}

/**
 * Get next step message based on application status
 */
function getNextStepMessage(status: ApplicationStatus): string {
  switch (status) {
    case 'interview_scheduled':
      return 'AI Interview scheduled';
    case 'interview_completed':
      return 'Interview completed - awaiting results';
    case 'under_review':
      return 'Application under review by recruiter';
    case 'applied':
      return 'Application submitted successfully';
    case 'rejected':
      return 'Position filled with another candidate';
    case 'offered':
      return 'Job offer received';
    case 'accepted':
      return 'Offer accepted';
    case 'withdrawn':
      return 'Application withdrawn';
    default:
      return 'Application in progress';
  }
}

export default function DashboardPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  const { data, isLoading, isError, refetch } = useApplications();
  const { data: profile } = useProfile();
  const { data: matchesData, isLoading: matchesLoading } = useJobMatches(1, 2); // Fetch top 2 matches

  // Authentication check
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Redirect if not authenticated
  if (!isAuthenticated) {
    return <div>Redirecting...</div>;
  }

  // Extract recent applications (top 3)
  const recentApplications = data?.slice(0, 3) || [];

  // Extract matched jobs from real API data (limit to top 2 for dashboard)
  const matchedJobs = matchesData?.jobs?.slice(0, 2) || [];

  // Calculate profile completion from real data
  const profileCompletion = profile 
    ? calculateProfileCompleteness(profile).total 
    : 0;

  // Calculate stats from real data
  const stats = {
    applications: data?.length || 0,
    interviews: data?.filter(a => a.status === 'interview_scheduled').length || 0,
    matches: matchesData?.total || 0, // Use real matches count
    profileCompletion,
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "interview_scheduled":
        return "bg-accent/10 text-accent border-accent/20"
      case "under_review":
        return "bg-primary/10 text-primary border-primary/20"
      case "applied":
        return "bg-muted text-muted-foreground"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "interview_scheduled":
        return <Calendar className="h-4 w-4" />
      case "under_review":
        return <Clock className="h-4 w-4" />
      case "applied":
        return <CheckCircle2 className="h-4 w-4" />
      default:
        return <AlertCircle className="h-4 w-4" />
    }
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Welcome back!</h1>
        <p className="text-muted-foreground">Here's what's happening with your job search</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Applications</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.applications}</div>
            <p className="text-xs text-muted-foreground">Active applications</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Interviews</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.interviews}</div>
            <p className="text-xs text-muted-foreground">Scheduled this month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Job Matches</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.matches}</div>
            <p className="text-xs text-muted-foreground">New matches this week</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Profile</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.profileCompletion}%</div>
            <p className="text-xs text-muted-foreground mb-2">Profile completion</p>
            {stats.profileCompletion < 100 && (
              <Button variant="ghost" size="sm" className="h-auto p-0 text-xs" asChild>
                <Link href="/profile">Complete Profile →</Link>
              </Button>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI Features Quick Access */}
      <Card className="bg-gradient-to-br from-primary/10 via-accent/10 to-primary/10 border-primary/20">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-accent" />
            <CardTitle>AI-Powered Features</CardTitle>
          </div>
          <CardDescription>Boost your job search with our AI tools</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button variant="outline" className="h-auto flex-col items-start p-4 gap-2 bg-card hover:bg-accent/10 transition-colors" asChild>
              <Link href="/interview/practice">
                <BrainCircuit className="h-5 w-5 text-accent group-hover:text-accent" />
                <div className="text-left">
                  <div className="font-semibold text-foreground">Mock Interview</div>
                  <div className="text-xs text-muted-foreground">Practice with AI</div>
                </div>
              </Link>
            </Button>

            <Button variant="outline" className="h-auto flex-col items-start p-4 gap-2 bg-card hover:bg-primary/10 transition-colors" asChild>
              <Link href="/profile/resume">
                <FileText className="h-5 w-5 text-primary group-hover:text-primary" />
                <div className="text-left">
                  <div className="font-semibold text-foreground">Resume Analysis</div>
                  <div className="text-xs text-muted-foreground">Get AI feedback</div>
                </div>
              </Link>
            </Button>

            <Button variant="outline" className="h-auto flex-col items-start p-4 gap-2 bg-card hover:bg-accent/10 transition-colors" asChild>
              <Link href="/jobs/matches">
                <Target className="h-5 w-5 text-accent group-hover:text-accent" />
                <div className="text-left">
                  <div className="font-semibold text-foreground">Job Matching</div>
                  <div className="text-xs text-muted-foreground">Find perfect roles</div>
                </div>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Applications */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Applications</CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/applications">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
            <CardDescription>Track your application progress</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading && (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="p-4 rounded-lg border">
                    <Skeleton className="h-6 w-3/4 mb-2" />
                    <Skeleton className="h-4 w-1/2 mb-4" />
                    <Skeleton className="h-4 w-full" />
                  </div>
                ))}
              </div>
            )}

            {isError && (
              <div className="p-6 text-center">
                <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
                <p className="text-sm text-muted-foreground mb-4">Error loading applications</p>
                <Button variant="outline" size="sm" onClick={() => refetch()}>
                  Retry
                </Button>
              </div>
            )}

            {!isLoading && !isError && recentApplications.length === 0 && (
              <div className="p-6 text-center">
                <Briefcase className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground mb-4">No applications yet</p>
                <Button variant="outline" size="sm" asChild>
                  <Link href="/jobs">Browse Jobs</Link>
                </Button>
              </div>
            )}

            {!isLoading && !isError && recentApplications.length > 0 && (
              <div className="space-y-4">
                {recentApplications.map((app) => {
                  // If interview is completed, link to results; otherwise link to job posting
                  const hasInterviewResults = app.interview_id && app.interview?.status === 'completed';
                  const viewUrl = hasInterviewResults 
                    ? `/interview/${app.interview_id}/results`
                    : `/jobs/${app.job_posting_id}`;
                  
                  return (
                    <div key={app.id} className="flex items-start gap-4 p-4 rounded-lg border">
                      <div className="flex-1 space-y-1">
                        <div className="font-semibold">{app.job_posting.title}</div>
                        <div className="text-sm text-muted-foreground">{app.job_posting.company}</div>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="outline" className={getStatusColor(app.status)}>
                            {getStatusIcon(app.status)}
                            <span className="ml-1 capitalize">{app.status.replace(/_/g, " ")}</span>
                          </Badge>
                          <span className="text-xs text-muted-foreground">{formatAppliedDate(app.applied_at)}</span>
                        </div>
                        <div className="text-sm text-muted-foreground mt-2">{getNextStepMessage(app.status)}</div>
                      </div>
                      <Button size="sm" variant="ghost" asChild>
                        <Link href={viewUrl}>View</Link>
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Matched Jobs */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Top Job Matches</CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/jobs/matches">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
            <CardDescription>AI-recommended jobs based on your profile</CardDescription>
          </CardHeader>
          <CardContent>
            {matchesLoading && (
              <div className="space-y-4">
                {[1, 2].map(i => (
                  <div key={i} className="p-4 rounded-lg border">
                    <Skeleton className="h-6 w-3/4 mb-2" />
                    <Skeleton className="h-4 w-1/2 mb-4" />
                    <Skeleton className="h-2 w-full mb-3" />
                    <Skeleton className="h-10 w-full" />
                  </div>
                ))}
              </div>
            )}

            {!matchesLoading && matchedJobs.length === 0 && (
              <div className="p-6 text-center">
                <Target className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground mb-4">
                  {profile && profile.profile_completeness_score < 40 
                    ? 'Complete your profile to unlock AI job matching'
                    : 'No matches yet - check back soon!'}
                </p>
                <Button variant="outline" size="sm" asChild>
                  <Link href={profile && profile.profile_completeness_score < 40 ? "/profile" : "/jobs"}>
                    {profile && profile.profile_completeness_score < 40 ? 'Complete Profile' : 'Browse Jobs'}
                  </Link>
                </Button>
              </div>
            )}

            {!matchesLoading && matchedJobs.length > 0 && (
              <div className="space-y-4">
                {matchedJobs.map((job) => {
                  // Format salary display
                  const salaryDisplay = job.salary_min && job.salary_max 
                    ? `$${(job.salary_min / 1000).toFixed(0)}k - $${(job.salary_max / 1000).toFixed(0)}k`
                    : 'Salary not specified';
                  
                  return (
                    <div key={job.id} className="p-4 rounded-lg border">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="font-semibold">{job.title}</div>
                          <div className="text-sm text-muted-foreground">{job.company}</div>
                        </div>
                        <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">
                          {job.match_score}% Match
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">{job.location}</span>
                        <span className="font-medium">{salaryDisplay}</span>
                      </div>
                      <Button className="w-full mt-3" size="sm" asChild>
                        <Link href={`/jobs/${job.id}`}>View Details →</Link>
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Profile Completion */}
      {stats.profileCompletion < 100 && (
        <Card>
          <CardHeader>
            <CardTitle>Complete Your Profile</CardTitle>
            <CardDescription>
              A complete profile increases your chances of getting matched with the right jobs
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Profile Completion</span>
                  <span className="text-sm text-muted-foreground">{stats.profileCompletion}%</span>
                </div>
                <Progress value={stats.profileCompletion} className="h-2" />
              </div>
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" asChild>
                  <Link href="/profile/resume">Upload Resume</Link>
                </Button>
                <Button variant="outline" size="sm" asChild>
                  <Link href="/profile/skills">Add Skills</Link>
                </Button>
                <Button variant="outline" size="sm" asChild>
                  <Link href="/profile/preferences">Set Preferences</Link>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
