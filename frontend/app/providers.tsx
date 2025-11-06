"use client"

import type React from "react"
import { QueryClientProvider } from "@tanstack/react-query"
import { ThemeProvider } from "next-themes"
import { queryClient } from "@/src/services/api/queryClient"
import { Toaster } from "@/components/ui/toaster"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        {children}
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
  )
}
