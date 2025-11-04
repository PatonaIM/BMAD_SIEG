"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import Link from "next/link"
import { User, FileText, Briefcase, MapPin, Mail, Phone, Edit, Award, Target } from "lucide-react"

export default function ProfilePage() {
  // Mock profile data
  const profile = {
    name: "John Doe",
    email: "john.doe@example.com",
    phone: "+1 (555) 123-4567",
    location: "San Francisco, CA",
    title: "Senior Full Stack Developer",
    experience: "5+ years",
    completion: 75,
    skills: ["React", "Node.js", "TypeScript", "AWS", "Python", "Docker"],
    preferences: {
      jobType: "Full-time",
      remote: true,
      salaryMin: "$140k",
      salaryMax: "$180k",
    },
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">My Profile</h1>
          <p className="text-muted-foreground">Manage your professional information</p>
        </div>
        <Button asChild>
          <Link href="/profile/edit">
            <Edit className="mr-2 h-4 w-4" />
            Edit Profile
          </Link>
        </Button>
      </div>

      {/* Profile Completion */}
      <Card>
        <CardHeader>
          <CardTitle>Profile Completion</CardTitle>
          <CardDescription>Complete your profile to increase your chances of getting matched</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Overall Progress</span>
              <span className="text-sm text-muted-foreground">{profile.completion}%</span>
            </div>
            <Progress value={profile.completion} className="h-2" />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link href="/profile/resume">Upload Resume</Link>
            </Button>
            <Button variant="outline" size="sm" asChild>
              <Link href="/profile/skills">Add More Skills</Link>
            </Button>
            <Button variant="outline" size="sm" asChild>
              <Link href="/profile/preferences">Set Job Preferences</Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5" />
              <CardTitle>Basic Information</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Name</div>
              <div className="text-base">{profile.name}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Email</div>
              <div className="flex items-center gap-2 text-base">
                <Mail className="h-4 w-4" />
                {profile.email}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Phone</div>
              <div className="flex items-center gap-2 text-base">
                <Phone className="h-4 w-4" />
                {profile.phone}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Location</div>
              <div className="flex items-center gap-2 text-base">
                <MapPin className="h-4 w-4" />
                {profile.location}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Professional Info */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Briefcase className="h-5 w-5" />
              <CardTitle>Professional Information</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Current Title</div>
              <div className="text-base">{profile.title}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Experience</div>
              <div className="text-base">{profile.experience}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">Skills</div>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill) => (
                  <Badge key={skill} variant="secondary">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Job Preferences */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              <CardTitle>Job Preferences</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Job Type</div>
              <div className="text-base">{profile.preferences.jobType}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Remote Work</div>
              <div className="text-base">{profile.preferences.remote ? "Yes, preferred" : "No preference"}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Salary Range</div>
              <div className="text-base">
                {profile.preferences.salaryMin} - {profile.preferences.salaryMax}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Resume */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              <CardTitle>Resume</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg border bg-muted/50">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  <span className="font-medium">resume_john_doe.pdf</span>
                </div>
                <Badge variant="secondary">
                  <Award className="h-3 w-3 mr-1" />
                  AI Analyzed
                </Badge>
              </div>
              <div className="text-sm text-muted-foreground">Uploaded 2 weeks ago</div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="flex-1 bg-transparent" asChild>
                <Link href="/profile/resume">View Resume</Link>
              </Button>
              <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                Upload New
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
