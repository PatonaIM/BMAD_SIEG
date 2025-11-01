"use client"

import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import Link from "next/link"
import { useRegister } from "../../hooks/useAuth"
import type { RegisterData } from "../../types/auth.types"

const registerSchema = z.object({
  email: z.string().email("Invalid email format"),
  full_name: z.string().min(2, "Full name must be at least 2 characters"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, "Password must contain uppercase, lowercase, and number"),
})

export const RegisterForm = () => {
  const form = useForm<RegisterData>({
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
    },
  })

  const registerMutation = useRegister()

  const email = form.watch("email")
  const fullName = form.watch("full_name")
  const password = form.watch("password", "")
  const isFieldsEmpty = !email || !fullName || !password

  const handleFieldBlur = (field: keyof RegisterData) => {
    const value = form.getValues(field)
    try {
      if (field === "email") {
        registerSchema.shape.email.parse(value)
      } else if (field === "full_name") {
        registerSchema.shape.full_name.parse(value)
      } else if (field === "password") {
        registerSchema.shape.password.parse(value)
      }
      form.clearErrors(field)
    } catch (error) {
      if (error instanceof z.ZodError && error.errors && error.errors.length > 0) {
        form.setError(field, {
          type: "manual",
          message: error.errors[0].message,
        })
      }
    }
  }

  const onSubmit = async (data: RegisterData) => {
    form.clearErrors()

    try {
      const validatedData = registerSchema.parse(data)
      registerMutation.mutate(validatedData)
    } catch (error) {
      if (error instanceof z.ZodError && error.errors) {
        error.errors.forEach((err) => {
          const field = err.path[0] as keyof RegisterData
          if (field) {
            form.setError(field, {
              type: "manual",
              message: err.message,
            })
          }
        })
      }
    }
  }

  // Password strength indicator
  const getPasswordStrength = (pass: string) => {
    if (!pass) return { value: 0, label: "", color: "" }
    if (pass.length < 8) return { value: 25, label: "Weak", color: "bg-destructive" }
    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(pass)) {
      return { value: 50, label: "Fair", color: "bg-yellow-500" }
    }
    if (pass.length >= 12) {
      return { value: 100, label: "Strong", color: "bg-green-500" }
    }
    return { value: 75, label: "Good", color: "bg-blue-500" }
  }

  const passwordStrength = getPasswordStrength(password)
  const hasErrors = Object.keys(form.formState.errors).length > 0

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold tracking-tight">Create Account</h1>
        <p className="text-muted-foreground">Register to start your interview</p>
      </div>

      {hasErrors && (
        <Alert variant="destructive">
          <AlertDescription>
            <ul className="list-disc list-inside space-y-1">
              {form.formState.errors.email && <li>{form.formState.errors.email.message}</li>}
              {form.formState.errors.full_name && <li>{form.formState.errors.full_name.message}</li>}
              {form.formState.errors.password && <li>{form.formState.errors.password.message}</li>}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {registerMutation.isError && (
        <Alert variant="destructive">
          <AlertDescription>
            {registerMutation.error instanceof Error
              ? registerMutation.error.message
              : "Registration failed. Please try again."}
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            {...form.register("email")}
            id="email"
            type="email"
            placeholder="Enter your email"
            disabled={registerMutation.isPending || form.formState.isSubmitting}
            className={form.formState.errors.email ? "border-destructive" : ""}
            onBlur={() => handleFieldBlur("email")}
          />
          {form.formState.errors.email && (
            <p className="text-sm text-destructive">{form.formState.errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="full_name">Full Name</Label>
          <Input
            {...form.register("full_name")}
            id="full_name"
            type="text"
            placeholder="Enter your full name"
            disabled={registerMutation.isPending || form.formState.isSubmitting}
            className={form.formState.errors.full_name ? "border-destructive" : ""}
            onBlur={() => handleFieldBlur("full_name")}
          />
          {form.formState.errors.full_name && (
            <p className="text-sm text-destructive">{form.formState.errors.full_name.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            {...form.register("password")}
            id="password"
            type="password"
            placeholder="Enter your password"
            disabled={registerMutation.isPending || form.formState.isSubmitting}
            className={form.formState.errors.password ? "border-destructive" : ""}
            onBlur={() => handleFieldBlur("password")}
          />
          {form.formState.errors.password && (
            <p className="text-sm text-destructive">{form.formState.errors.password.message}</p>
          )}
        </div>

        {password && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Password Strength</span>
              <span className={passwordStrength.color.replace("bg-", "text-")}>{passwordStrength.label}</span>
            </div>
            <Progress value={passwordStrength.value} className="h-2" />
          </div>
        )}
      </div>

      <Button
        type="submit"
        className="w-full"
        size="lg"
        disabled={registerMutation.isPending || form.formState.isSubmitting || isFieldsEmpty}
      >
        {registerMutation.isPending || form.formState.isSubmitting ? "Creating Account..." : "Create Account"}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="text-primary font-medium hover:underline">
          Sign In
        </Link>
      </p>
    </form>
  )
}
