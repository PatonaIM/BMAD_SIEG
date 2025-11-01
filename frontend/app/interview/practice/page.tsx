"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { BrainCircuit, Zap, Target, TrendingUp, ArrowRight } from "lucide-react"

export default function MockInterviewPage() {
  const practiceCategories = [
    {
      id: "technical",
      title: "Technical Interview",
      description: "Practice coding and system design questions",
      difficulty: "Medium",
      duration: "30-45 min",
      icon: BrainCircuit,
    },
    {
      id: "behavioral",
      title: "Behavioral Interview",
      description: "Work on communication and soft skills",
      difficulty: "Easy",
      duration: "20-30 min",
      icon: Target,
    },
    {
      id: "quick",
      title: "Quick Practice",
      description: "5-minute rapid-fire questions",
      difficulty: "Easy",
      duration: "5-10 min",
      icon: Zap,
    },
  ]

  return (
    <div className="container max-w-5xl py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Mock Interview Practice</h1>
        <p className="text-muted-foreground">
          Practice with our AI interviewer to build confidence and improve your skills
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {practiceCategories.map((category) => {
          const Icon = category.icon
          return (
            <Card key={category.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <Badge variant="outline">{category.difficulty}</Badge>
                </div>
                <CardTitle>{category.title}</CardTitle>
                <CardDescription>{category.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground mb-4">Duration: {category.duration}</div>
                <Button className="w-full" asChild>
                  <Link href={`/interview/practice/${category.id}`}>
                    Start Practice
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Stats Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-accent" />
            <CardTitle>Your Practice Stats</CardTitle>
          </div>
          <CardDescription>Track your improvement over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">12</div>
              <div className="text-sm text-muted-foreground">Sessions</div>
            </div>
            <div>
              <div className="text-2xl font-bold">8.5</div>
              <div className="text-sm text-muted-foreground">Avg Score</div>
            </div>
            <div>
              <div className="text-2xl font-bold">6h</div>
              <div className="text-sm text-muted-foreground">Total Time</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
