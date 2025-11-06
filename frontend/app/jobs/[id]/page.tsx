"use client";

/**
 * Job Detail Page
 * 
 * Displays full details of a job posting and allows authenticated candidates
 * to apply with one click. Handles application submission, duplicate detection,
 * and provides interview start link after successful application.
 */

import { useParams, useRouter } from 'next/navigation';
import { useAuthStore } from '@/src/features/auth/store/authStore';
import { useJobPosting } from '@/hooks/use-job-posting';
import { useApplications } from '@/hooks/use-applications';
import { useApplyToJob } from '@/hooks/use-apply-to-job';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  MapPin,
  DollarSign,
  Briefcase,
  Clock,
  Building2,
  CheckCircle2,
  ArrowLeft,
  Loader2,
  AlertCircle,
} from 'lucide-react';

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;

  // Auth state
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());

  // Fetch job details
  const { data: job, isLoading, isError, error } = useJobPosting(jobId);

  // Fetch user's applications to check if already applied
  const { data: applications } = useApplications();

  // Application mutation
  const {
    mutate: applyToJob,
    isPending: isApplying,
    isSuccess: applicationSuccess,
    data: applicationData,
  } = useApplyToJob();

  // Check if already applied to this job
  const alreadyApplied = applications?.some(
    (app) => app.job_posting_id === jobId
  );

  // Find the application if exists
  const existingApplication = applications?.find(
    (app) => app.job_posting_id === jobId
  );

  // Handle apply button click
  const handleApply = () => {
    if (!isAuthenticated) {
      router.push(`/login?returnUrl=/jobs/${jobId}`);
      return;
    }
    applyToJob(jobId);
  };

  // Handle start interview
  const handleStartInterview = () => {
    const appId = applicationData?.id || existingApplication?.id;
    if (appId) {
      router.push(`/interview/start?application_id=${appId}`);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-6">
          <Skeleton className="h-10 w-32" />
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-3/4 mb-4" />
            <Skeleton className="h-6 w-1/2" />
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[...Array(6)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-24 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  // Error state
  if (isError || !job) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Button variant="ghost" onClick={() => router.push('/jobs')} className="mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Jobs
        </Button>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error?.message || 'Job posting not found or no longer available.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Format salary range
  const formatSalary = () => {
    if (!job.salary_range_min && !job.salary_range_max) return 'Not specified';
    if (job.salary_range_min && job.salary_range_max) {
      return `$${job.salary_range_min.toLocaleString()} - $${job.salary_range_max.toLocaleString()}`;
    }
    if (job.salary_range_min) return `From $${job.salary_range_min.toLocaleString()}`;
    if (job.salary_range_max) return `Up to $${job.salary_range_max.toLocaleString()}`;
  };

  // Determine button state
  const getApplyButtonState = () => {
    if (!isAuthenticated) {
      return {
        text: 'Sign in to apply',
        disabled: false,
        variant: 'default' as const,
        icon: null,
      };
    }

    if (alreadyApplied || applicationSuccess) {
      return {
        text: 'Applied',
        disabled: true,
        variant: 'outline' as const,
        icon: <CheckCircle2 className="mr-2 h-4 w-4 text-green-600" />,
      };
    }

    if (isApplying) {
      return {
        text: 'Applying...',
        disabled: true,
        variant: 'default' as const,
        icon: <Loader2 className="mr-2 h-4 w-4 animate-spin" />,
      };
    }

    return {
      text: 'Apply Now',
      disabled: false,
      variant: 'default' as const,
      icon: null,
    };
  };

  const buttonState = getApplyButtonState();

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Back button */}
      <Button
        variant="ghost"
        onClick={() => router.push('/jobs')}
        className="mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Jobs
      </Button>

      {/* Success message */}
      {(applicationSuccess || (alreadyApplied && existingApplication)) && (
        <Alert className="mb-6 border-green-600 dark:border-green-500 bg-green-50 dark:bg-green-950/30">
          <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-500" />
          <AlertTitle className="text-green-800 dark:text-green-300">Application Submitted</AlertTitle>
          <AlertDescription className="text-green-700 dark:text-green-400">
            Your application has been received. You can start the AI interview now.
            <Button
              onClick={handleStartInterview}
              variant="link"
              className="ml-2 p-0 h-auto text-green-800 dark:text-green-300 underline"
            >
              Start Interview Now →
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Job details card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-3xl mb-2">{job.title}</CardTitle>
              <CardDescription className="text-lg flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                {job.company}
              </CardDescription>
            </div>
            <Badge variant={job.status === 'active' ? 'default' : 'secondary'}>
              {job.status}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Job metadata grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
              <MapPin className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Location</p>
                <p className="font-medium">{job.location}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
              <DollarSign className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Salary Range</p>
                <p className="font-medium">{formatSalary()}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
              <Briefcase className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Employment Type</p>
                <p className="font-medium capitalize">{job.employment_type.replace('_', ' ')}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
              <Building2 className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Work Setup</p>
                <p className="font-medium capitalize">{job.work_setup}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
              <Clock className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Experience Level</p>
                <p className="font-medium capitalize">{job.experience_level.replace('_', ' ')}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
              <Briefcase className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Role Category</p>
                <p className="font-medium capitalize">{job.role_category}</p>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-xl font-semibold mb-3">Job Description</h3>
            <p className="text-foreground whitespace-pre-line">{job.description}</p>
          </div>

          {/* Tech stack */}
          {job.tech_stack && (
            <div>
              <h3 className="text-xl font-semibold mb-3">Technology Stack</h3>
              <p className="text-foreground">{job.tech_stack}</p>
            </div>
          )}

          {/* Required skills */}
          {job.required_skills && job.required_skills.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold mb-3">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.required_skills.map((skill, index) => (
                  <Badge key={index} variant="default">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Preferred skills */}
          {job.preferred_skills && job.preferred_skills.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold mb-3">Preferred Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.preferred_skills.map((skill, index) => (
                  <Badge key={index} variant="secondary">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Benefits */}
          {job.benefits && job.benefits.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold mb-3">Benefits</h3>
              <ul className="list-disc list-inside space-y-1 text-foreground">
                {job.benefits.map((benefit, index) => (
                  <li key={index}>{benefit}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Apply button */}
          <div className="pt-6 border-t">
            <Button
              onClick={handleApply}
              disabled={buttonState.disabled}
              variant={buttonState.variant}
              size="lg"
              className="w-full md:w-auto"
            >
              {buttonState.icon}
              {buttonState.text}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
