"use client"

import type React from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { AuthenticatedLayout } from "@/components/layouts/authenticated-layout"

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <AuthenticatedLayout>{children}</AuthenticatedLayout>
    </ProtectedRoute>
  )
}
