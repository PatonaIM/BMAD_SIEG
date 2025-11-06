"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import Link from "next/link"
import { Search, MapPin, DollarSign, Briefcase, Clock, Building2, Filter, Sparkles } from "lucide-react"
import { useDebouncedCallback } from "use-debounce"
import { useJobPostings } from "@/hooks/use-job-postings"
import type { JobPostingFilters } from "@/lib/api-client"

// Helper function to format posted date
function formatPostedDate(postedAt: string): string {
  const date = new Date(postedAt)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return "Today"
  if (diffDays === 1) return "1 day ago"
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return `${Math.floor(diffDays / 30)} months ago`
}

// Helper function to format salary range
function formatSalaryRange(min: number | null, max: number | null): string {
  if (!min && !max) return "Salary not specified"
  if (!max) return `$${Math.round(min! / 1000)}k+`
  if (!min) return `Up to $${Math.round(max / 1000)}k`
  return `$${Math.round(min / 1000)}k - $${Math.round(max / 1000)}k`
}

export default function JobsPage() {
  const [filters, setFilters] = useState<JobPostingFilters>({
    search: "",
    location: "",
    role_category: "",
    tech_stack: "",
    employment_type: "",
    work_setup: "",
    experience_level: "",
    skip: 0,
    limit: 20,
  })

  const { data, isLoading, isError, error, refetch } = useJobPostings(filters)

  const handleFilterChange = (key: keyof JobPostingFilters, value: string | number) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      skip: key !== "skip" ? 0 : (value as number), // Reset to page 1 on filter change
    }))
  }

  const handleSearch = useDebouncedCallback((value: string) => {
    handleFilterChange("search", value)
  }, 500)

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
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
                  defaultValue={filters.search}
                  onChange={(e) => handleSearch(e.target.value)}
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
                  value={filters.location}
                  onChange={(e) => handleFilterChange("location", e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="job-type">Job Type</Label>
              <Select
                value={filters.employment_type || "all"}
                onValueChange={(value) => handleFilterChange("employment_type", value === "all" ? "" : value)}
              >
                <SelectTrigger id="job-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="full_time">Full-time</SelectItem>
                  <SelectItem value="part_time">Part-time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="experience">Experience Level</Label>
              <Select
                value={filters.experience_level || "all"}
                onValueChange={(value) => handleFilterChange("experience_level", value === "all" ? "" : value)}
              >
                <SelectTrigger id="experience">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="entry">Entry</SelectItem>
                  <SelectItem value="junior">Junior</SelectItem>
                  <SelectItem value="mid">Mid-level</SelectItem>
                  <SelectItem value="senior">Senior</SelectItem>
                  <SelectItem value="lead">Lead</SelectItem>
                  <SelectItem value="principal">Principal</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button className="flex-1" disabled={isLoading}>
              <Search className="mr-2 h-4 w-4" />
              {isLoading ? "Searching..." : "Search Jobs"}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setFilters({
                  search: "",
                  location: "",
                  role_category: "",
                  tech_stack: "",
                  employment_type: "",
                  work_setup: "",
                  experience_level: "",
                  skip: 0,
                  limit: 20,
                })
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
          Showing <strong>{data?.jobs.length || 0}</strong> of <strong>{data?.total || 0}</strong> jobs
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
        {/* Loading State */}
        {isLoading && (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full mt-2" />
                  <div className="flex gap-2 mt-4">
                    <Skeleton className="h-6 w-16" />
                    <Skeleton className="h-6 w-16" />
                    <Skeleton className="h-6 w-16" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Error State */}
        {isError && (
          <Card>
            <CardHeader>
              <CardTitle>Error Loading Jobs</CardTitle>
              <CardDescription>
                {error?.message || "Failed to load job postings. Please try again."}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => refetch()}>Retry</Button>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!isLoading && !isError && data?.jobs.length === 0 && (
          <Card>
            <CardHeader>
              <CardTitle>No Jobs Found</CardTitle>
              <CardDescription>
                Try adjusting your filters or search terms to find more opportunities.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() =>
                  setFilters({
                    search: "",
                    location: "",
                    role_category: "",
                    tech_stack: "",
                    employment_type: "",
                    work_setup: "",
                    experience_level: "",
                    skip: 0,
                    limit: 20,
                  })
                }
              >
                Clear Filters
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Job Cards */}
        {!isLoading && !isError && data?.jobs && data.jobs.length > 0 && (
          <>
            {data.jobs.map((job) => {
              const skills = job.required_skills || []
              
              return (
                <Card key={job.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <CardTitle className="text-xl">{job.title}</CardTitle>
                          {job.status === "active" && (
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
                        {job.employment_type.replace("_", "-")}
                      </div>
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4" />
                        {formatSalaryRange(job.salary_range_min, job.salary_range_max)}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {formatPostedDate(job.posted_at)}
                      </div>
                    </div>

                    {/* Skills */}
                    {skills.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {skills.map((skill) => (
                          <Badge key={skill} variant="outline">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    )}

                    {/* Footer */}
                    <div className="flex items-center justify-between pt-2 border-t text-sm text-muted-foreground">
                      <span>Apply now</span>
                      <Badge variant="secondary">{job.experience_level}</Badge>
                    </div>
                  </CardContent>
                </Card>
              )
            })}

            {/* Pagination */}
            {data && data.total > data.limit && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <Button
                  variant="outline"
                  disabled={filters.skip === 0}
                  onClick={() => handleFilterChange("skip", Math.max(0, (filters.skip || 0) - (filters.limit || 20)))}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {Math.floor((filters.skip || 0) / (filters.limit || 20)) + 1} of{" "}
                  {Math.ceil(data.total / (filters.limit || 20))}
                </span>
                <Button
                  variant="outline"
                  disabled={(filters.skip || 0) + (filters.limit || 20) >= data.total}
                  onClick={() => handleFilterChange("skip", (filters.skip || 0) + (filters.limit || 20))}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
