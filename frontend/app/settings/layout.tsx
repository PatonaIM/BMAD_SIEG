"use client"

import type React from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { AuthenticatedLayout } from "@/components/layouts/authenticated-layout"

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <AuthenticatedLayout>{children}</AuthenticatedLayout>
    </ProtectedRoute>
  )
}
