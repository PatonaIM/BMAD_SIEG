"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Briefcase, FileText, TrendingUp, Clock, CheckCircle2, XCircle, AlertCircle } from "lucide-react"
import Link from "next/link"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold text-foreground">Welcome back, John!</h1>
          <p className="text-muted-foreground">Here's what's happening with your job search</p>
        </div>

        {/* Stats Grid */}
        <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Applications</p>
                <p className="text-2xl font-bold text-foreground">12</p>
              </div>
              <div className="rounded-lg bg-primary/10 p-3">
                <FileText className="h-6 w-6 text-primary" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Interviews</p>
                <p className="text-2xl font-bold text-foreground">3</p>
              </div>
              <div className="rounded-lg bg-success/10 p-3">
                <Briefcase className="h-6 w-6 text-success" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Job Matches</p>
                <p className="text-2xl font-bold text-foreground">24</p>
              </div>
              <div className="rounded-lg bg-warning/10 p-3">
                <TrendingUp className="h-6 w-6 text-warning" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Profile Views</p>
                <p className="text-2xl font-bold text-foreground">156</p>
              </div>
              <div className="rounded-lg bg-accent/10 p-3">
                <TrendingUp className="h-6 w-6 text-accent-foreground" />
              </div>
            </div>
          </Card>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Recent Applications */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <h2 className="mb-4 text-xl font-semibold text-foreground">Recent Applications</h2>
              <div className="space-y-4">
                {[
                  {
                    title: "Senior React Developer",
                    company: "TechCorp Inc.",
                    status: "interview",
                    date: "2 days ago",
                  },
                  {
                    title: "Python Backend Engineer",
                    company: "DataFlow Systems",
                    status: "pending",
                    date: "1 week ago",
                  },
                  {
                    title: "Full-Stack Developer",
                    company: "StartupXYZ",
                    status: "rejected",
                    date: "2 weeks ago",
                  },
                ].map((app, idx) => (
                  <div
                    key={idx}
                    className="flex flex-col gap-3 border-b border-border pb-4 last:border-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="flex-1">
                      <h3 className="font-medium text-foreground">{app.title}</h3>
                      <p className="text-sm text-muted-foreground">{app.company}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge
                        variant={
                          app.status === "interview"
                            ? "default"
                            : app.status === "pending"
                              ? "secondary"
                              : "destructive"
                        }
                      >
                        {app.status === "interview" && <CheckCircle2 className="mr-1 h-3 w-3" />}
                        {app.status === "pending" && <Clock className="mr-1 h-3 w-3" />}
                        {app.status === "rejected" && <XCircle className="mr-1 h-3 w-3" />}
                        {app.status}
                      </Badge>
                      <span className="text-sm text-muted-foreground">{app.date}</span>
                    </div>
                  </div>
                ))}
              </div>
              <Button asChild variant="outline" className="mt-4 w-full bg-transparent">
                <Link href="/applications">View All Applications</Link>
              </Button>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="space-y-4">
            <Card className="p-6">
              <h2 className="mb-4 text-xl font-semibold text-foreground">Quick Actions</h2>
              <div className="space-y-3">
                <Button asChild className="w-full justify-start bg-transparent" variant="outline">
                  <Link href="/jobs">
                    <Briefcase className="mr-2 h-4 w-4" />
                    Browse Jobs
                  </Link>
                </Button>
                <Button asChild className="w-full justify-start bg-transparent" variant="outline">
                  <Link href="/interview/practice">
                    <AlertCircle className="mr-2 h-4 w-4" />
                    Practice Interview
                  </Link>
                </Button>
                <Button asChild className="w-full justify-start bg-transparent" variant="outline">
                  <Link href="/profile">
                    <FileText className="mr-2 h-4 w-4" />
                    Update Profile
                  </Link>
                </Button>
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="mb-2 text-xl font-semibold text-foreground">Profile Strength</h2>
              <div className="mb-4">
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">75% Complete</span>
                  <span className="font-medium text-foreground">Good</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div className="h-full w-3/4 bg-primary" />
                </div>
              </div>
              <p className="text-sm text-muted-foreground">Add your work experience to improve your profile</p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
