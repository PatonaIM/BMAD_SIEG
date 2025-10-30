"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, MapPin, Briefcase, Clock } from "lucide-react"
import Link from "next/link"

const jobs = [
  {
    id: 1,
    title: "Senior React Developer",
    company: "TechCorp Inc.",
    location: "Remote",
    type: "Full-time",
    salary: "$120k - $160k",
    posted: "2 days ago",
    tags: ["React", "TypeScript", "Next.js"],
  },
  {
    id: 2,
    title: "Python Backend Engineer",
    company: "DataFlow Systems",
    location: "New York, NY",
    type: "Full-time",
    salary: "$130k - $170k",
    posted: "1 week ago",
    tags: ["Python", "FastAPI", "PostgreSQL"],
  },
  {
    id: 3,
    title: "Full-Stack Developer",
    company: "StartupXYZ",
    location: "San Francisco, CA",
    type: "Full-time",
    salary: "$110k - $150k",
    posted: "3 days ago",
    tags: ["JavaScript", "Node.js", "React"],
  },
]

export default function JobsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold text-foreground md:text-4xl">Find Your Next Opportunity</h1>
          <p className="text-muted-foreground">Browse AI-powered job matches tailored to your skills</p>
        </div>

        {/* Search Bar */}
        <Card className="mb-8 p-4">
          <div className="flex flex-col gap-4 md:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Search jobs, skills, or companies..." className="pl-10" />
            </div>
            <div className="relative flex-1">
              <MapPin className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Location" className="pl-10" />
            </div>
            <Button className="md:w-auto">Search</Button>
          </div>
        </Card>

        {/* Job Listings */}
        <div className="space-y-4">
          {jobs.map((job) => (
            <Card key={job.id} className="p-6 transition-shadow hover:shadow-lg">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="flex-1">
                  <h3 className="mb-2 text-xl font-semibold text-foreground">{job.title}</h3>
                  <p className="mb-3 text-muted-foreground">{job.company}</p>

                  <div className="mb-4 flex flex-wrap gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {job.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <Briefcase className="h-4 w-4" />
                      {job.type}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {job.posted}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {job.tags.map((tag) => (
                      <Badge key={tag} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col gap-2 md:items-end">
                  <p className="text-lg font-semibold text-foreground">{job.salary}</p>
                  <Button asChild>
                    <Link href={`/jobs/${job.id}`}>View Details</Link>
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
