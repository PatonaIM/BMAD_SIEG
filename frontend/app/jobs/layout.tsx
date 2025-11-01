"use client"

import type React from "react"
import { ConditionalLayout } from "@/components/layouts/conditional-layout"

export default function JobsLayout({ children }: { children: React.ReactNode }) {
  return <ConditionalLayout>{children}</ConditionalLayout>
}
