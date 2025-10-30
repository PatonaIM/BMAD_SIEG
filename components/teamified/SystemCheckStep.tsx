"use client"

import { CheckCircle2, XCircle, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface SystemCheckStepProps {
  label: string
  status: "pending" | "checking" | "success" | "error"
  errorMessage?: string
}

export function SystemCheckStep({ label, status, errorMessage }: SystemCheckStepProps) {
  return (
    <div className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
      <div className="flex-shrink-0 mt-0.5">
        {status === "pending" && <div className="w-5 h-5 rounded-full border-2 border-gray-300 dark:border-gray-600" />}
        {status === "checking" && <Loader2 className="w-5 h-5 text-[#A16AE8] animate-spin" />}
        {status === "success" && <CheckCircle2 className="w-5 h-5 text-[#1DD1A1]" />}
        {status === "error" && <XCircle className="w-5 h-5 text-[#EF4444]" />}
      </div>
      <div className="flex-1 min-w-0">
        <p
          className={cn(
            "text-sm font-medium",
            status === "success" && "text-[#1DD1A1]",
            status === "error" && "text-[#EF4444]",
            (status === "pending" || status === "checking") && "text-gray-700 dark:text-gray-300",
          )}
        >
          {label}
        </p>
        {errorMessage && status === "error" && <p className="mt-1 text-xs text-[#EF4444]">{errorMessage}</p>}
      </div>
    </div>
  )
}
