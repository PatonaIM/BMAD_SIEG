"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"
import { FileText, Calendar, Clock, CheckCircle2, XCircle, AlertCircle, Briefcase } from "lucide-react"

export default function ApplicationsPage() {
  const [activeTab, setActiveTab] = useState("all")

  // Mock applications data
  const applications = [
    {
      id: "1",
      jobTitle: "Senior Full Stack Developer",
      company: "TechCorp Inc.",
      status: "interview_scheduled",
      appliedAt: "2024-01-10",
      nextStep: "AI Interview scheduled for Jan 15, 2024",
      location: "Remote",
      salary: "$140k - $180k",
    },
    {
      id: "2",
      jobTitle: "Lead Frontend Engineer",
      company: "StartupXYZ",
      status: "under_review",
      appliedAt: "2024-01-08",
      nextStep: "Application under review by recruiter",
      location: "San Francisco, CA",
      salary: "$150k - $200k",
    },
    {
      id: "3",
      jobTitle: "Product Manager",
      company: "Innovation Labs",
      status: "applied",
      appliedAt: "2024-01-05",
      nextStep: "Application submitted successfully",
      location: "New York, NY",
      salary: "$140k - $200k",
    },
    {
      id: "4",
      jobTitle: "Data Scientist",
      company: "AI Solutions",
      status: "rejected",
      appliedAt: "2023-12-28",
      nextStep: "Position filled with another candidate",
      location: "Remote",
      salary: "$130k - $190k",
    },
  ]

  const getStatusConfig = (status: string) => {
    switch (status) {
      case "interview_scheduled":
        return {
          label: "Interview Scheduled",
          color: "bg-accent/10 text-accent border-accent/20",
          icon: Calendar,
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
      default:
        return {
          label: status,
          color: "bg-muted text-muted-foreground",
          icon: AlertCircle,
        }
    }
  }

  const filterApplications = (status: string) => {
    if (status === "all") return applications
    return applications.filter((app) => app.status === status)
  }

  const stats = {
    total: applications.length,
    active: applications.filter((a) => !["rejected", "withdrawn"].includes(a.status)).length,
    interviews: applications.filter((a) => a.status === "interview_scheduled").length,
    pending: applications.filter((a) => a.status === "under_review").length,
  }

  return (
    <div className="space-y-6">
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
          <TabsTrigger value="all">All ({applications.length})</TabsTrigger>
          <TabsTrigger value="interview_scheduled">
            Interviews ({applications.filter((a) => a.status === "interview_scheduled").length})
          </TabsTrigger>
          <TabsTrigger value="under_review">
            Under Review ({applications.filter((a) => a.status === "under_review").length})
          </TabsTrigger>
          <TabsTrigger value="applied">
            Applied ({applications.filter((a) => a.status === "applied").length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="space-y-4 mt-6">
          {filterApplications(activeTab).map((app) => {
            const statusConfig = getStatusConfig(app.status)
            const StatusIcon = statusConfig.icon

            return (
              <Card key={app.id}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{app.jobTitle}</CardTitle>
                      <CardDescription className="text-base">{app.company}</CardDescription>
                    </div>
                    <Button variant="outline" asChild>
                      <Link href={`/applications/${app.id}`}>View Details</Link>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={statusConfig.color}>
                      <StatusIcon className="h-3 w-3 mr-1" />
                      {statusConfig.label}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      Applied {new Date(app.appliedAt).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-muted/50 text-sm">{app.nextStep}</div>

                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>{app.location}</span>
                    <span>•</span>
                    <span>{app.salary}</span>
                  </div>
                </CardContent>
              </Card>
            )
          })}

          {filterApplications(activeTab).length === 0 && (
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
        </TabsContent>
      </Tabs>
    </div>
  )
}
