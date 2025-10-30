"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Briefcase, Users, Sparkles, TrendingUp } from "lucide-react"
import Link from "next/link"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border">
        <div className="container mx-auto px-4 py-16 md:py-24 lg:py-32">
          <div className="mx-auto max-w-4xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary">
              <Sparkles className="h-4 w-4" />
              AI-Powered Recruitment
            </div>
            <h1 className="mb-6 text-balance text-4xl font-bold tracking-tight text-foreground md:text-5xl lg:text-6xl">
              Transform Your Hiring with AI Interviews
            </h1>
            <p className="mb-8 text-pretty text-lg text-muted-foreground md:text-xl">
              Streamline technical assessments with intelligent AI-driven interviews. Evaluate candidates faster,
              fairer, and more effectively.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button asChild size="lg" className="text-base">
                <Link href="/jobs">Browse Jobs</Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="text-base bg-transparent">
                <Link href="/login">Sign In</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold text-foreground md:text-4xl">Why Choose Teamified?</h2>
            <p className="mx-auto max-w-2xl text-pretty text-muted-foreground">
              Our platform combines cutting-edge AI technology with human expertise to deliver exceptional recruitment
              outcomes.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">AI-Powered Interviews</h3>
              <p className="text-muted-foreground">
                Natural speech-to-speech conversations that adapt to candidate responses and provide comprehensive skill
                assessments.
              </p>
            </Card>

            <Card className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-success/10">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Smart Job Matching</h3>
              <p className="text-muted-foreground">
                AI algorithms match candidates to perfect opportunities based on skills, experience, and career
                preferences.
              </p>
            </Card>

            <Card className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
                <Users className="h-6 w-6 text-accent-foreground" />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Recruiter Dashboard</h3>
              <p className="text-muted-foreground">
                Comprehensive tools for managing candidates, reviewing interviews, and making data-driven hiring
                decisions.
              </p>
            </Card>

            <Card className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-warning/10">
                <Briefcase className="h-6 w-6 text-warning" />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Multi-Domain Assessment</h3>
              <p className="text-muted-foreground">
                Support for React, Python, JavaScript, and Full-Stack roles with tailored technical evaluations.
              </p>
            </Card>

            <Card className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Resume Analysis</h3>
              <p className="text-muted-foreground">
                AI-powered resume parsing and feedback to help candidates improve their profiles and stand out.
              </p>
            </Card>

            <Card className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-success/10">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Real-Time Analytics</h3>
              <p className="text-muted-foreground">
                Track hiring metrics, interview performance, and candidate pipeline with comprehensive analytics.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t border-border bg-muted/30 py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="mb-4 text-3xl font-bold text-foreground md:text-4xl">Ready to Get Started?</h2>
            <p className="mb-8 text-pretty text-lg text-muted-foreground">
              Join thousands of candidates and recruiters using Teamified to transform their hiring process.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button asChild size="lg" className="text-base">
                <Link href="/register">Create Account</Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="text-base bg-transparent">
                <Link href="/jobs">Explore Jobs</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
