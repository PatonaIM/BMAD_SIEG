"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import Link from "next/link"
import { FileText, Calendar, Clock, CheckCircle2, XCircle, AlertCircle, Briefcase } from "lucide-react"
import { useApplications } from "@/hooks/use-applications"
import { useAuthStore } from "@/src/features/auth/store/authStore"
import type { ApplicationStatus, Application } from "@/lib/api-client"

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
function getNextStepMessage(status: ApplicationStatus, interviewId?: string | null, interviewStatus?: string): string {
  if (interviewId && interviewStatus === 'completed') {
    return 'Interview completed - view results available';
  }
  
  switch (status) {
    case 'interview_scheduled':
      return 'AI Interview scheduled - start when ready';
    case 'interview_completed':
      return 'Interview completed - awaiting review';
    case 'under_review':
      return 'Application under review by recruiter';
    case 'applied':
      return 'Application submitted successfully';
    case 'rejected':
      return 'Position filled with another candidate';
    case 'offered':
      return 'Job offer received - action required';
    case 'accepted':
      return 'Offer accepted - onboarding pending';
    case 'withdrawn':
      return 'Application withdrawn';
    default:
      return 'Application in progress';
  }
}

export default function ApplicationsPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  const { data, isLoading, isError, refetch } = useApplications();
  const [activeTab, setActiveTab] = useState("all");

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

  // Filter applications based on active tab
  const filterApplications = (apps: Application[], tab: string): Application[] => {
    switch(tab) {
      case 'all': 
        return apps;
      case 'interview_scheduled': 
        return apps.filter(a => a.status === 'interview_scheduled');
      case 'under_review': 
        return apps.filter(a => a.status === 'under_review');
      case 'applied': 
        return apps.filter(a => a.status === 'applied');
      default: 
        return apps;
    }
  };

  // Calculate stats from real data
  const stats = {
    total: data?.length || 0,
    active: data?.filter(a => !['rejected', 'withdrawn'].includes(a.status)).length || 0,
    interviews: data?.filter(a => a.status === 'interview_scheduled').length || 0,
    pending: data?.filter(a => a.status === 'under_review').length || 0,
  };

  // Calculate tab counts dynamically
  const tabCounts = {
    all: data?.length || 0,
    interviews: data?.filter(a => a.status === 'interview_scheduled').length || 0,
    underReview: data?.filter(a => a.status === 'under_review').length || 0,
    applied: data?.filter(a => a.status === 'applied').length || 0,
  };

  // Filtered applications based on active tab
  const filteredApplications = data ? filterApplications(data, activeTab) : [];

  const getStatusConfig = (status: ApplicationStatus) => {
    switch (status) {
      case "interview_scheduled":
        return {
          label: "Interview Scheduled",
          color: "bg-accent/10 text-accent border-accent/20",
          icon: Calendar,
        }
      case "interview_completed":
        return {
          label: "Interview Complete",
          color: "bg-green-500/10 text-green-700 border-green-500/20",
          icon: CheckCircle2,
        }
      case "under_review":
        return {
          label: "Under Review",
          color: "bg-primary/10 text-primary border-primary/20",
          icon: Clock,
        }
      case "applied":
        return {
          label: "Applied",
          color: "bg-muted text-muted-foreground",
          icon: CheckCircle2,
        }
      case "rejected":
        return {
          label: "Not Selected",
          color: "bg-destructive/10 text-destructive border-destructive/20",
          icon: XCircle,
        }
      case "offered":
        return {
          label: "Offer Received",
          color: "bg-green-500/10 text-green-700 border-green-500/20",
          icon: CheckCircle2,
        }
      default:
        return {
          label: status,
          color: "bg-muted text-muted-foreground",
          icon: AlertCircle,
        }
    }
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">My Applications</h1>
        <p className="text-muted-foreground">Track and manage your job applications</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Interviews</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.interviews}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Under Review</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending}</div>
          </CardContent>
        </Card>
      </div>

      {/* Applications List with Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All ({tabCounts.all})</TabsTrigger>
          <TabsTrigger value="interview_scheduled">
            Interviews ({tabCounts.interviews})
          </TabsTrigger>
          <TabsTrigger value="under_review">
            Under Review ({tabCounts.underReview})
          </TabsTrigger>
          <TabsTrigger value="applied">
            Applied ({tabCounts.applied})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="space-y-4 mt-6">
          {/* Loading State */}
          {isLoading && (
            <div className="grid gap-4 md:grid-cols-2">
              {[1, 2, 3, 4].map(i => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4 mb-2" />
                    <Skeleton className="h-4 w-1/2" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-4 w-full mb-2" />
                    <Skeleton className="h-4 w-2/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Error State */}
          {isError && (
            <Card className="p-12 text-center">
              <div className="flex justify-center mb-4">
                <div className="p-4 rounded-full bg-destructive/10">
                  <AlertCircle className="h-8 w-8 text-destructive" />
                </div>
              </div>
              <h3 className="text-xl font-semibold mb-2">Error loading applications</h3>
              <p className="text-muted-foreground mb-6">Failed to fetch your applications. Please try again.</p>
              <Button onClick={() => refetch()}>
                Retry
              </Button>
            </Card>
          )}

          {/* Empty State */}
          {!isLoading && !isError && filteredApplications.length === 0 && (
            <Card className="p-12 text-center">
              <div className="flex justify-center mb-4">
                <div className="p-4 rounded-full bg-muted">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                </div>
              </div>
              <h3 className="text-xl font-semibold mb-2">No applications yet</h3>
              <p className="text-muted-foreground mb-6">Start applying to jobs to see them here</p>
              <Button asChild>
                <Link href="/jobs">Browse Jobs</Link>
              </Button>
            </Card>
          )}

          {/* Applications List */}
          {!isLoading && !isError && filteredApplications.length > 0 && filteredApplications.map((app) => {
            const statusConfig = getStatusConfig(app.status);
            const StatusIcon = statusConfig.icon;
            const hasInterviewResults = app.interview_id && app.interview?.status === 'completed';

            return (
              <Card key={app.id}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{app.job_posting.title}</CardTitle>
                      <CardDescription className="text-base">{app.job_posting.company}</CardDescription>
                    </div>
                    <Button variant="outline" asChild>
                      <Link href={`/jobs/${app.job_posting_id}`}>View Details</Link>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className={statusConfig.color}>
                      <StatusIcon className="h-3 w-3 mr-1" />
                      {statusConfig.label}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      Applied {formatAppliedDate(app.applied_at)}
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-muted/50 text-sm">
                    {getNextStepMessage(app.status, app.interview_id, app.interview?.status)}
                  </div>

                  <div className="flex items-center gap-4 text-sm text-muted-foreground flex-wrap">
                    <span>{app.job_posting.location}</span>
                    <span>•</span>
                    <span className="capitalize">{app.job_posting.work_setup.replace(/_/g, ' ')}</span>
                    <span>•</span>
                    <span className="capitalize">{app.job_posting.employment_type.replace(/_/g, ' ')}</span>
                  </div>

                  {/* View Interview Results Link */}
                  {hasInterviewResults && (
                    <div className="pt-2">
                      <Button variant="secondary" size="sm" asChild className="w-full sm:w-auto">
                        <Link href={`/interview/${app.interview_id}/results`}>
                          <CheckCircle2 className="h-4 w-4 mr-2" />
                          View Interview Results
                        </Link>
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </TabsContent>
      </Tabs>
    </div>
  )
}
