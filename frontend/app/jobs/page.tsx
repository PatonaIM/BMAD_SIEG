"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import Link from "next/link"
import { Search, MapPin, DollarSign, Briefcase, Clock, Building2, Filter, Sparkles } from "lucide-react"

export default function JobsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [location, setLocation] = useState("")
  const [jobType, setJobType] = useState("all")
  const [experience, setExperience] = useState("all")

  // Mock jobs data
  const jobs = [
    {
      id: "1",
      title: "Senior Full Stack Developer",
      company: "TechCorp Inc.",
      location: "Remote",
      type: "Full-time",
      salary: "$140k - $180k",
      experience: "Senior",
      skills: ["React", "Node.js", "TypeScript", "AWS"],
      postedAt: "2 days ago",
      applicants: 45,
      featured: true,
    },
    {
      id: "2",
      title: "Frontend Engineer",
      company: "StartupXYZ",
      location: "San Francisco, CA",
      type: "Full-time",
      salary: "$120k - $160k",
      experience: "Mid-level",
      skills: ["React", "TypeScript", "Next.js"],
      postedAt: "1 week ago",
      applicants: 32,
      featured: false,
    },
    {
      id: "3",
      title: "Backend Developer",
      company: "DataFlow Systems",
      location: "New York, NY",
      type: "Full-time",
      salary: "$130k - $170k",
      experience: "Mid-level",
      skills: ["Node.js", "Python", "PostgreSQL", "Docker"],
      postedAt: "3 days ago",
      applicants: 28,
      featured: false,
    },
    {
      id: "4",
      title: "Engineering Manager",
      company: "BigTech Co",
      location: "Seattle, WA",
      type: "Full-time",
      salary: "$180k - $240k",
      experience: "Senior",
      skills: ["Leadership", "Agile", "Technical Strategy"],
      postedAt: "5 days ago",
      applicants: 67,
      featured: true,
    },
    {
      id: "5",
      title: "Junior Full Stack Developer",
      company: "Innovation Labs",
      location: "Remote",
      type: "Full-time",
      salary: "$80k - $100k",
      experience: "Junior",
      skills: ["JavaScript", "React", "Node.js"],
      postedAt: "1 day ago",
      applicants: 89,
      featured: false,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Browse Jobs</h1>
          <p className="text-muted-foreground">Discover opportunities that match your skills and preferences</p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/jobs/matches">
            <Sparkles className="mr-2 h-4 w-4" />
            AI Matches
          </Link>
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            <CardTitle>Search & Filter</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="search">Job Title or Keywords</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="e.g. Full Stack Developer"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="location"
                  placeholder="e.g. San Francisco"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="job-type">Job Type</Label>
              <Select value={jobType} onValueChange={setJobType}>
                <SelectTrigger id="job-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="full-time">Full-time</SelectItem>
                  <SelectItem value="part-time">Part-time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="experience">Experience Level</Label>
              <Select value={experience} onValueChange={setExperience}>
                <SelectTrigger id="experience">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="junior">Junior</SelectItem>
                  <SelectItem value="mid-level">Mid-level</SelectItem>
                  <SelectItem value="senior">Senior</SelectItem>
                  <SelectItem value="lead">Lead</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button className="flex-1">
              <Search className="mr-2 h-4 w-4" />
              Search Jobs
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setSearchQuery("")
                setLocation("")
                setJobType("all")
                setExperience("all")
              }}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing <strong>{jobs.length}</strong> jobs
        </p>
        <Select defaultValue="recent">
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="recent">Most Recent</SelectItem>
            <SelectItem value="relevant">Most Relevant</SelectItem>
            <SelectItem value="salary-high">Salary: High to Low</SelectItem>
            <SelectItem value="salary-low">Salary: Low to High</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Job Listings */}
      <div className="space-y-4">
        {jobs.map((job) => (
          <Card key={job.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <CardTitle className="text-xl">{job.title}</CardTitle>
                    {job.featured && (
                      <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">
                        <Sparkles className="h-3 w-3 mr-1" />
                        Featured
                      </Badge>
                    )}
                  </div>
                  <CardDescription className="flex items-center gap-2 text-base">
                    <Building2 className="h-4 w-4" />
                    {job.company}
                  </CardDescription>
                </div>
                <Button asChild>
                  <Link href={`/jobs/${job.id}`}>View Details</Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Job Details */}
              <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {job.location}
                </div>
                <div className="flex items-center gap-1">
                  <Briefcase className="h-4 w-4" />
                  {job.type}
                </div>
                <div className="flex items-center gap-1">
                  <DollarSign className="h-4 w-4" />
                  {job.salary}
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {job.postedAt}
                </div>
              </div>

              {/* Skills */}
              <div className="flex flex-wrap gap-2">
                {job.skills.map((skill) => (
                  <Badge key={skill} variant="outline">
                    {skill}
                  </Badge>
                ))}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between pt-2 border-t text-sm text-muted-foreground">
                <span>{job.applicants} applicants</span>
                <Badge variant="secondary">{job.experience}</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
