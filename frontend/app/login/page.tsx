"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/src/features/auth/store/authStore"
import { LoginForm } from "@/src/features/auth/components/LoginForm/LoginForm"
import { MockModeIndicator } from "@/src/components/shared/MockModeIndicator"
import { Card } from "@/components/ui/card"

export default function LoginPage() {
  const router = useRouter()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated())
  const [isMounted, setIsMounted] = useState(false)
  const [isRedirecting, setIsRedirecting] = useState(false)

  // Track when component mounts to avoid hydration mismatch
  useEffect(() => {
    setIsMounted(true)
  }, [])

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (isMounted && isAuthenticated && !isRedirecting) {
      setIsRedirecting(true)
      router.replace("/dashboard")
    }
  }, [isMounted, isAuthenticated, router, isRedirecting])

  // Wait for client-side mount before checking auth (prevents hydration mismatch)
  if (!isMounted) {
    return (
      <div className="container max-w-md mx-auto">
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="p-8 w-full shadow-lg">
            <MockModeIndicator />
            <LoginForm />
          </Card>
        </div>
      </div>
    )
  }

  // Show nothing while redirecting to prevent flash
  if (isAuthenticated || isRedirecting) {
    return null
  }

  return (
    <div className="container max-w-md mx-auto">
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="p-8 w-full shadow-lg">
          <MockModeIndicator />
          <LoginForm />
        </Card>
      </div>
    </div>
  )
}
