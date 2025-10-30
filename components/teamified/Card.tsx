import { cn } from "@/lib/utils"
import { type HTMLAttributes, forwardRef } from "react"

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "outlined" | "elevated"
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "default", children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-xl transition-all duration-200",
          {
            "bg-white dark:bg-gray-800": variant === "default",
            "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700": variant === "outlined",
            "bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl": variant === "elevated",
          },
          className,
        )}
        {...props}
      >
        {children}
      </div>
    )
  },
)

Card.displayName = "Card"
