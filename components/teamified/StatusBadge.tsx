import { cn } from "@/lib/utils"
import type { HTMLAttributes } from "react"

interface StatusBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  status: "active" | "pending" | "completed" | "failed" | "scheduled" | "in-progress"
}

export function StatusBadge({ status, className, ...props }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        {
          "bg-[#1DD1A1]/10 text-[#16A881] dark:bg-[#1DD1A1]/20": status === "active" || status === "completed",
          "bg-[#FFA502]/10 text-[#E69500] dark:bg-[#FFA502]/20": status === "pending" || status === "scheduled",
          "bg-[#EF4444]/10 text-[#DC2626] dark:bg-[#EF4444]/20": status === "failed",
          "bg-[#A16AE8]/10 text-[#8A4FD9] dark:bg-[#A16AE8]/20": status === "in-progress",
        },
        className,
      )}
      {...props}
    >
      {status.charAt(0).toUpperCase() + status.slice(1).replace("-", " ")}
    </span>
  )
}
