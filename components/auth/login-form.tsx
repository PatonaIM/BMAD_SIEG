"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Box, Button, TextField, Typography, Alert, FormControlLabel, Checkbox } from "@mui/material"
import Link from "next/link"
import { useLogin } from "@/lib/auth/hooks"
import type { LoginData } from "@/lib/auth/types"

const loginSchema = z.object({
  email: z.string().email("Invalid email format"),
  password: z.string().min(1, "Password is required"),
})

export function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginData>({
    resolver: zodResolver(loginSchema),
  })

  const loginMutation = useLogin()

  const onSubmit = (data: LoginData) => {
    loginMutation.mutate(data)
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ width: "100%", maxWidth: 400 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Sign In
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Welcome back! Please sign in to continue.
      </Typography>

      {loginMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {loginMutation.error instanceof Error
            ? loginMutation.error.message
            : "Invalid email or password. Please try again."}
        </Alert>
      )}

      <TextField
        {...register("email")}
        label="Email"
        type="email"
        fullWidth
        margin="normal"
        error={!!errors.email}
        helperText={errors.email?.message}
        disabled={loginMutation.isPending}
        autoComplete="email"
      />

      <TextField
        {...register("password")}
        label="Password"
        type="password"
        fullWidth
        margin="normal"
        error={!!errors.password}
        helperText={errors.password?.message}
        disabled={loginMutation.isPending}
        autoComplete="current-password"
      />

      <FormControlLabel control={<Checkbox defaultChecked color="primary" />} label="Remember me" sx={{ mt: 1 }} />

      <Button
        type="submit"
        variant="contained"
        fullWidth
        size="large"
        disabled={loginMutation.isPending}
        sx={{ mt: 2 }}
      >
        {loginMutation.isPending ? "Signing In..." : "Sign In"}
      </Button>

      <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: "center" }}>
        Don&apos;t have an account?{" "}
        <Link href="/register" style={{ color: "#A16AE8", textDecoration: "none", fontWeight: 500 }}>
          Create Account
        </Link>
      </Typography>
    </Box>
  )
}
