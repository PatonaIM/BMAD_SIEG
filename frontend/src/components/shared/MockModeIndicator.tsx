"use client"

import { env } from "@/config/env"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { InfoIcon } from "lucide-react"

/**
 * Visual indicator when mock API mode is enabled
 * Shows at the top of the page to remind users they're viewing mock data
 */
export function MockModeIndicator() {
  if (!env.mockApi) return null

  return (
    <Alert className="mb-4 border-amber-500 bg-amber-50 dark:bg-amber-950/20">
      <InfoIcon className="h-4 w-4 text-amber-600" />
      <AlertDescription className="text-amber-800 dark:text-amber-200">
        <strong>Mock Mode Active:</strong> All API calls are disabled. You're viewing the UI with sample data. Set{" "}
        <code className="px-1 py-0.5 bg-amber-100 dark:bg-amber-900 rounded text-xs">NEXT_PUBLIC_MOCK_API=false</code>{" "}
        to enable real API calls.
      </AlertDescription>
    </Alert>
  )
}
