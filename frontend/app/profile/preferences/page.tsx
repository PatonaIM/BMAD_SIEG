"use client"

import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import Link from "next/link"
import { Save, ArrowLeft, AlertCircle, Loader2 } from "lucide-react"
import { useProfile } from "@/hooks/use-profile"
import { useUpdatePreferences } from "@/hooks/use-profile-mutations"
import type { UpdatePreferencesRequest } from "@/types/profile"

// Validation schema
const preferencesSchema = z.object({
  preferred_job_types: z.string().min(1, "Please select at least one job type"),
  preferred_locations: z.string().min(1, "Please enter at least one location"),
  preferred_work_setup: z.enum(["remote", "hybrid", "onsite", "any"]),
  salary_expectation_min: z.string().optional(),
  salary_expectation_max: z.string().optional(),
  salary_currency: z.enum(["USD", "AUD", "EUR", "GBP"]),
}).refine((data) => {
  // If either salary field is filled, both must be filled
  const hasMin = data.salary_expectation_min && data.salary_expectation_min.trim() !== ""
  const hasMax = data.salary_expectation_max && data.salary_expectation_max.trim() !== ""
  
  if (hasMin !== hasMax) {
    return false
  }
  
  // If both are filled, min must be less than max
  if (hasMin && hasMax) {
    const min = parseInt(data.salary_expectation_min || "0")
    const max = parseInt(data.salary_expectation_max || "0")
    return min < max && min > 0 && max > 0
  }
  
  return true
}, {
  message: "Both salary fields must be filled, and minimum must be less than maximum",
  path: ["salary_expectation_max"],
})

type PreferencesFormData = z.infer<typeof preferencesSchema>

export default function PreferencesPage() {
  const { data: profile, isLoading, isError, error } = useProfile()
  const { mutate: updatePreferences, isPending } = useUpdatePreferences()

  const form = useForm<PreferencesFormData>({
    resolver: zodResolver(preferencesSchema),
    defaultValues: {
      preferred_job_types: "",
      preferred_locations: "",
      preferred_work_setup: "any",
      salary_expectation_min: "",
      salary_expectation_max: "",
      salary_currency: "USD",
    },
  })

  // Initialize form from profile data
  useEffect(() => {
    if (profile) {
      form.reset({
        preferred_job_types: profile.preferred_job_types.join(", "),
        preferred_locations: profile.preferred_locations.join(", "),
        preferred_work_setup: profile.preferred_work_setup,
        salary_expectation_min: profile.salary_expectation_min?.toString() || "",
        salary_expectation_max: profile.salary_expectation_max?.toString() || "",
        salary_currency: (profile.salary_currency as "USD" | "AUD" | "EUR" | "GBP") || "USD",
      })
    }
  }, [profile, form])

  const onSubmit = (data: PreferencesFormData) => {
    // Convert comma-separated strings to arrays
    const jobTypes = data.preferred_job_types
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0)
    
    const locations = data.preferred_locations
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0)

    const payload: UpdatePreferencesRequest = {
      preferred_job_types: jobTypes,
      preferred_locations: locations,
      preferred_work_setup: data.preferred_work_setup,
      salary_currency: data.salary_currency,
    }

    // Only include salary if both fields are filled
    if (data.salary_expectation_min && data.salary_expectation_max) {
      payload.salary_expectation_min = parseInt(data.salary_expectation_min)
      payload.salary_expectation_max = parseInt(data.salary_expectation_max)
    }

    updatePreferences(payload)
  }

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (isError || !profile) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error?.message || "Failed to load profile. Please try again."}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <Button variant="ghost" size="sm" asChild className="mb-2">
          <Link href="/profile">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Profile
          </Link>
        </Button>
        <h1 className="text-3xl font-bold mb-2">Job Preferences</h1>
        <p className="text-muted-foreground">
          Set your job preferences to get better matched opportunities
        </p>
      </div>

      {/* Preferences Form */}
      <Card>
        <CardHeader>
          <CardTitle>Your Preferences</CardTitle>
          <CardDescription>
            Tell us what you're looking for in your next role
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Job Types */}
              <FormField
                control={form.control}
                name="preferred_job_types"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Job Types</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="e.g., full_time, part_time, contract"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Enter job types separated by commas (full_time, part_time, contract, internship)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Locations */}
              <FormField
                control={form.control}
                name="preferred_locations"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Preferred Locations</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="e.g., San Francisco, Remote, New York"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Enter locations separated by commas (max 10)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Work Setup */}
              <FormField
                control={form.control}
                name="preferred_work_setup"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Work Setup</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select work setup" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="remote">Remote</SelectItem>
                        <SelectItem value="hybrid">Hybrid</SelectItem>
                        <SelectItem value="onsite">On-site</SelectItem>
                        <SelectItem value="any">Any</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Preferred work arrangement
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Salary Range */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormField
                  control={form.control}
                  name="salary_expectation_min"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Salary Min</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="60000"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="salary_expectation_max"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Salary Max</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="100000"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="salary_currency"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Currency</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="USD">USD</SelectItem>
                          <SelectItem value="AUD">AUD</SelectItem>
                          <SelectItem value="EUR">EUR</SelectItem>
                          <SelectItem value="GBP">GBP</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="text-xs text-muted-foreground">
                * Both salary fields must be filled if you want to specify a range
              </div>

              {/* Submit Button */}
              <Button 
                type="submit" 
                disabled={isPending}
                className="w-full"
              >
                {isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save Preferences
                  </>
                )}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {/* Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Why Preferences Matter</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>• Complete preferences contribute 20% to your profile completeness score</p>
          <p>• Better matching with job opportunities that fit your criteria</p>
          <p>• Recruiters can filter candidates based on preferences</p>
          <p>• You can update these anytime as your preferences change</p>
        </CardContent>
      </Card>
    </div>
  )
}
