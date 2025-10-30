import { cn } from "@/lib/utils"

interface ProgressIndicatorProps {
  value: number
  max?: number
  size?: "sm" | "md" | "lg"
  variant?: "primary" | "success" | "warning" | "error"
  showLabel?: boolean
  className?: string
}

export function ProgressIndicator({
  value,
  max = 100,
  size = "md",
  variant = "primary",
  showLabel = false,
  className,
}: ProgressIndicatorProps) {
  const percentage = Math.min((value / max) * 100, 100)

  return (
    <div className={cn("w-full", className)}>
      <div
        className={cn("w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden", {
          "h-1": size === "sm",
          "h-2": size === "md",
          "h-3": size === "lg",
        })}
      >
        <div
          className={cn("h-full transition-all duration-300 ease-out", {
            "bg-[#A16AE8]": variant === "primary",
            "bg-[#1DD1A1]": variant === "success",
            "bg-[#FFA502]": variant === "warning",
            "bg-[#EF4444]": variant === "error",
          })}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 text-right">{Math.round(percentage)}%</p>
      )}
    </div>
  )
}
