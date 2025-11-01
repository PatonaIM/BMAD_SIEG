"use client"

import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Checkbox } from "@/components/ui/checkbox"
import Link from "next/link"
import { useLogin } from "../../hooks/useAuth"

const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Invalid email format"),
  password: z.string().min(1, "Password is required"),
})

type LoginFormData = z.infer<typeof loginSchema>

export const LoginForm = () => {
  const form = useForm<LoginFormData>({
    defaultValues: {
      email: "",
      password: "",
    },
  })

  const loginMutation = useLogin()

  const email = form.watch("email")
  const password = form.watch("password")
  const isFieldsEmpty = !email || !password

  const handleFieldBlur = (field: keyof LoginFormData) => {
    const value = form.getValues(field)
    try {
      if (field === "email") {
        loginSchema.shape.email.parse(value)
      } else if (field === "password") {
        loginSchema.shape.password.parse(value)
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

  const onSubmit = async (data: LoginFormData) => {
    form.clearErrors()

    try {
      const validatedData = loginSchema.parse(data)
      loginMutation.mutate(validatedData)
    } catch (error) {
      if (error instanceof z.ZodError && error.errors) {
        error.errors.forEach((err) => {
          const field = err.path[0] as keyof LoginFormData
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

  const hasErrors = Object.keys(form.formState.errors).length > 0

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold tracking-tight">Sign In</h1>
        <p className="text-muted-foreground">Welcome back! Please sign in to continue.</p>
      </div>

      {hasErrors && (
        <Alert variant="destructive">
          <AlertDescription>
            <ul className="list-disc list-inside space-y-1">
              {form.formState.errors.email && <li>{form.formState.errors.email.message}</li>}
              {form.formState.errors.password && <li>{form.formState.errors.password.message}</li>}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {loginMutation.isError && (
        <Alert variant="destructive">
          <AlertDescription>
            {loginMutation.error instanceof Error
              ? loginMutation.error.message
              : "Invalid email or password. Please try again."}
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
            disabled={loginMutation.isPending || form.formState.isSubmitting}
            autoComplete="email"
            className={form.formState.errors.email ? "border-destructive" : ""}
            onBlur={() => handleFieldBlur("email")}
          />
          {form.formState.errors.email && (
            <p className="text-sm text-destructive">{form.formState.errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            {...form.register("password")}
            id="password"
            type="password"
            placeholder="Enter your password"
            disabled={loginMutation.isPending || form.formState.isSubmitting}
            autoComplete="current-password"
            className={form.formState.errors.password ? "border-destructive" : ""}
            onBlur={() => handleFieldBlur("password")}
          />
          {form.formState.errors.password && (
            <p className="text-sm text-destructive">{form.formState.errors.password.message}</p>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox id="remember" defaultChecked />
          <Label htmlFor="remember" className="text-sm font-normal cursor-pointer">
            Remember me
          </Label>
        </div>
      </div>

      <Button
        type="submit"
        className="w-full"
        size="lg"
        disabled={loginMutation.isPending || form.formState.isSubmitting || isFieldsEmpty}
      >
        {loginMutation.isPending || form.formState.isSubmitting ? "Signing In..." : "Sign In"}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        Don't have an account?{" "}
        <Link href="/register" className="text-primary font-medium hover:underline">
          Create Account
        </Link>
      </p>
    </form>
  )
}
