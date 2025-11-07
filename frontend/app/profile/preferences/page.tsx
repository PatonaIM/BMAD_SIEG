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
import { Checkbox } from "@/components/ui/checkbox"
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
import { JOB_TYPES, WORK_SETUPS, CURRENCIES, SALARY_PERIOD } from "@/lib/constants/profile"

// Validation schema
const preferencesSchema = z.object({
  preferred_job_types: z.array(z.string()).min(1, "Please select at least one job type"),
  preferred_work_setup: z.enum(["remote", "hybrid", "onsite", "any"]),
  salary_expectation_min: z.string().optional(),
  salary_expectation_max: z.string().optional(),
  salary_currency: z.enum(["USD", "PHP", "AUD", "INR", "LKR", "JPY", "KRW", "BRL", "EUR", "GBP", "CAD", "SGD", "AED"]),
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
      preferred_job_types: [],
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
        preferred_job_types: profile.preferred_job_types,
        preferred_work_setup: profile.preferred_work_setup,
        salary_expectation_min: profile.salary_expectation_min?.toString() || "",
        salary_expectation_max: profile.salary_expectation_max?.toString() || "",
        salary_currency: (profile.salary_currency as "USD" | "PHP" | "AUD" | "INR" | "LKR" | "JPY" | "KRW" | "BRL" | "EUR" | "GBP" | "CAD" | "SGD" | "AED") || "USD",
      })
    }
  }, [profile, form])

  const onSubmit = (data: PreferencesFormData) => {
    const payload: UpdatePreferencesRequest = {
      preferred_job_types: data.preferred_job_types,
      preferred_locations: [], // Empty array - location not collected
      preferred_work_setup: data.preferred_work_setup,
      salary_currency: data.salary_currency,
      salary_period: SALARY_PERIOD, // Always annually
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
                render={() => (
                  <FormItem>
                    <FormLabel>Job Types</FormLabel>
                    <FormDescription>
                      Select all job types you're interested in
                    </FormDescription>
                    <div className="grid grid-cols-2 gap-4 mt-2">
                      {JOB_TYPES.map((jobType) => (
                        <FormField
                          key={jobType.value}
                          control={form.control}
                          name="preferred_job_types"
                          render={({ field }) => {
                            return (
                              <FormItem
                                key={jobType.value}
                                className="flex flex-row items-start space-x-3 space-y-0"
                              >
                                <FormControl>
                                  <Checkbox
                                    checked={field.value?.includes(jobType.value)}
                                    onCheckedChange={(checked) => {
                                      return checked
                                        ? field.onChange([...field.value, jobType.value])
                                        : field.onChange(
                                            field.value?.filter(
                                              (value) => value !== jobType.value
                                            )
                                          )
                                    }}
                                  />
                                </FormControl>
                                <FormLabel className="font-normal cursor-pointer">
                                  {jobType.label}
                                </FormLabel>
                              </FormItem>
                            )
                          }}
                        />
                      ))}
                    </div>
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
                        {WORK_SETUPS.map((setup) => (
                          <SelectItem key={setup.value} value={setup.value}>
                            {setup.label}
                          </SelectItem>
                        ))}
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
              <div className="space-y-4">
                <div>
                  <FormLabel>Salary Expectations (Annual)</FormLabel>
                  <p className="text-xs text-muted-foreground mt-1">
                    All salaries are annual for consistency across markets
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <FormField
                    control={form.control}
                    name="salary_expectation_min"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Min</FormLabel>
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
                        <FormLabel>Max</FormLabel>
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
                            {CURRENCIES.map((currency) => (
                              <SelectItem key={currency.value} value={currency.value}>
                                {currency.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
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
