"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
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

export default function DashboardPage() {
  // Mock data - will be replaced with API calls
  const stats = {
    applications: 12,
    interviews: 3,
    matches: 8,
    profileCompletion: 75,
  }

  const recentApplications = [
    {
      id: "1",
      jobTitle: "Senior Full Stack Developer",
      company: "TechCorp Inc.",
      status: "interview_scheduled",
      appliedAt: "2 days ago",
      nextStep: "AI Interview on Jan 15",
    },
    {
      id: "2",
      jobTitle: "Product Manager",
      company: "Innovation Labs",
      status: "under_review",
      appliedAt: "1 week ago",
      nextStep: "Awaiting recruiter review",
    },
    {
      id: "3",
      jobTitle: "Data Scientist",
      company: "AI Solutions",
      status: "applied",
      appliedAt: "3 days ago",
      nextStep: "Application submitted",
    },
  ]

  const matchedJobs = [
    {
      id: "1",
      title: "Lead Frontend Engineer",
      company: "StartupXYZ",
      matchScore: 95,
      location: "Remote",
      salary: "$150k - $200k",
    },
    {
      id: "2",
      title: "Engineering Manager",
      company: "BigTech Co",
      matchScore: 88,
      location: "San Francisco, CA",
      salary: "$180k - $240k",
    },
  ]

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
    <div className="space-y-8">
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
            <p className="text-xs text-muted-foreground">Profile completion</p>
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
            <Button variant="outline" className="h-auto flex-col items-start p-4 gap-2 bg-transparent" asChild>
              <Link href="/interview/practice">
                <BrainCircuit className="h-5 w-5 text-accent" />
                <div className="text-left">
                  <div className="font-semibold">Mock Interview</div>
                  <div className="text-xs text-muted-foreground">Practice with AI</div>
                </div>
              </Link>
            </Button>

            <Button variant="outline" className="h-auto flex-col items-start p-4 gap-2 bg-transparent" asChild>
              <Link href="/profile/resume">
                <FileText className="h-5 w-5 text-primary" />
                <div className="text-left">
                  <div className="font-semibold">Resume Analysis</div>
                  <div className="text-xs text-muted-foreground">Get AI feedback</div>
                </div>
              </Link>
            </Button>

            <Button variant="outline" className="h-auto flex-col items-start p-4 gap-2 bg-transparent" asChild>
              <Link href="/jobs/matches">
                <Target className="h-5 w-5 text-accent" />
                <div className="text-left">
                  <div className="font-semibold">Job Matching</div>
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
            <div className="space-y-4">
              {recentApplications.map((app) => (
                <div key={app.id} className="flex items-start gap-4 p-4 rounded-lg border">
                  <div className="flex-1 space-y-1">
                    <div className="font-semibold">{app.jobTitle}</div>
                    <div className="text-sm text-muted-foreground">{app.company}</div>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline" className={getStatusColor(app.status)}>
                        {getStatusIcon(app.status)}
                        <span className="ml-1 capitalize">{app.status.replace("_", " ")}</span>
                      </Badge>
                      <span className="text-xs text-muted-foreground">{app.appliedAt}</span>
                    </div>
                    <div className="text-sm text-muted-foreground mt-2">{app.nextStep}</div>
                  </div>
                  <Button size="sm" variant="ghost" asChild>
                    <Link href={`/applications/${app.id}`}>View</Link>
                  </Button>
                </div>
              ))}
            </div>
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
            <div className="space-y-4">
              {matchedJobs.map((job) => (
                <div key={job.id} className="p-4 rounded-lg border">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="font-semibold">{job.title}</div>
                      <div className="text-sm text-muted-foreground">{job.company}</div>
                    </div>
                    <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">
                      {job.matchScore}% Match
                    </Badge>
                  </div>
                  <Progress value={job.matchScore} className="h-2 mb-3" />
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{job.location}</span>
                    <span className="font-medium">{job.salary}</span>
                  </div>
                  <Button className="w-full mt-3" size="sm" asChild>
                    <Link href={`/jobs/${job.id}`}>View & Apply</Link>
                  </Button>
                </div>
              ))}
            </div>
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
