"use client"

import type { ReactNode } from "react"
import { redirect } from "next/navigation"
import { useAuthStore } from "@/src/features/auth/store/authStore"
import { useEffect, useState } from "react"

interface ProtectedRouteProps {
  children: ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [isChecking, setIsChecking] = useState(true)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated())

  useEffect(() => {
    if (!isAuthenticated) {
      redirect("/login")
    } else {
      setIsChecking(false)
    }
  }, [isAuthenticated])

  if (isChecking) {
    return null
  }

  return <>{children}</>
}
