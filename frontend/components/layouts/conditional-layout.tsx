"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { useAuthStore } from "@/src/features/auth/store/authStore"
import { AuthenticatedLayout } from "./authenticated-layout"
import { UnauthenticatedHeader } from "./unauthenticated-header"

export function ConditionalLayout({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated())

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  if (isAuthenticated) {
    return <AuthenticatedLayout>{children}</AuthenticatedLayout>
  }

  return (
    <div className="min-h-screen">
      <UnauthenticatedHeader />
      <main className="p-4 md:p-6 lg:p-8">
        <div className="mx-auto max-w-7xl">{children}</div>
      </main>
    </div>
  )
}
