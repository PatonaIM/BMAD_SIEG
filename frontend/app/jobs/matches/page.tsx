"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { Sparkles, Target, MapPin, DollarSign, Briefcase, TrendingUp, Settings2 } from "lucide-react"

export default function JobMatchesPage() {
  const [matchingEnabled, setMatchingEnabled] = useState(true)

  // Mock matched jobs data
  const matchedJobs = [
    {
      id: "1",
      title: "Senior Full Stack Developer",
      company: "TechCorp Inc.",
      location: "Remote",
      type: "Full-time",
      salary: "$140k - $180k",
      matchScore: 95,
      matchReasons: [
        "5+ years React experience matches requirement",
        "Node.js expertise aligns with tech stack",
        "Remote preference matches job location",
        "Salary expectation within range",
      ],
      skills: ["React", "Node.js", "TypeScript", "AWS"],
      postedAt: "2 days ago",
    },
    {
      id: "2",
      title: "Lead Frontend Engineer",
      company: "StartupXYZ",
      location: "San Francisco, CA",
      type: "Full-time",
      salary: "$150k - $200k",
      matchScore: 88,
      matchReasons: [
        "Strong React and TypeScript skills",
        "Leadership experience matches role",
        "Startup experience preferred",
      ],
      skills: ["React", "TypeScript", "Next.js", "GraphQL"],
      postedAt: "1 week ago",
    },
    {
      id: "3",
      title: "Engineering Manager",
      company: "BigTech Co",
      location: "New York, NY",
      type: "Full-time",
      salary: "$180k - $240k",
      matchScore: 82,
      matchReasons: ["Technical background aligns", "Team leadership experience", "Agile methodology expertise"],
      skills: ["Leadership", "Agile", "Technical Strategy"],
      postedAt: "3 days ago",
    },
  ]

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
          <Link href="/profile/preferences">
            <Settings2 className="mr-2 h-4 w-4" />
            Preferences
          </Link>
        </Button>
      </div>

      {/* Matching Status Card */}
      <Card className="bg-gradient-to-br from-accent/10 to-primary/10 border-accent/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent/20">
                <Sparkles className="h-5 w-5 text-accent" />
              </div>
              <div>
                <CardTitle>AI Job Matching</CardTitle>
                <CardDescription>Automatically find jobs that match your profile</CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Label htmlFor="matching-toggle" className="text-sm">
                {matchingEnabled ? "Enabled" : "Disabled"}
              </Label>
              <Switch id="matching-toggle" checked={matchingEnabled} onCheckedChange={setMatchingEnabled} />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-accent" />
              <span>
                <strong>{matchedJobs.length}</strong> new matches this week
              </span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              <span>
                <strong>95%</strong> average match score
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-accent" />
              <span>Updated daily with new opportunities</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Matched Jobs List */}
      <div className="space-y-4">
        {matchedJobs.map((job) => (
          <Card key={job.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <CardTitle className="text-xl">{job.title}</CardTitle>
                    <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">
                      <Sparkles className="h-3 w-3 mr-1" />
                      {job.matchScore}% Match
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
                  <span className="text-sm text-muted-foreground">{job.matchScore}%</span>
                </div>
                <Progress value={job.matchScore} className="h-2" />
              </div>

              {/* Match Reasons */}
              <div>
                <div className="text-sm font-medium mb-2">Why this matches you:</div>
                <ul className="space-y-1">
                  {job.matchReasons.map((reason, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-accent mt-0.5">•</span>
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Job Details */}
              <div className="flex flex-wrap gap-4 text-sm text-muted-foreground pt-2 border-t">
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
              </div>

              {/* Skills */}
              <div className="flex flex-wrap gap-2">
                {job.skills.map((skill) => (
                  <Badge key={skill} variant="outline">
                    {skill}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State (when no matches) */}
      {matchedJobs.length === 0 && (
        <Card className="p-12 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-4 rounded-full bg-muted">
              <Target className="h-8 w-8 text-muted-foreground" />
            </div>
          </div>
          <h3 className="text-xl font-semibold mb-2">No matches yet</h3>
          <p className="text-muted-foreground mb-6">
            Complete your profile to start receiving personalized job matches
          </p>
          <Button asChild>
            <Link href="/profile">Complete Profile</Link>
          </Button>
        </Card>
      )}
    </div>
  )
}
