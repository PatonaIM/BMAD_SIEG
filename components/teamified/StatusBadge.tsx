import type React from "react"

export interface StatusBadgeProps {
  status: "success" | "error" | "warning" | "info"
  children: React.ReactNode
}

export function StatusBadge({ status, children }: StatusBadgeProps) {
  return <span>{children}</span>
}
