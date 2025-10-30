import { cn } from "@/lib/utils"
import { type ButtonHTMLAttributes, forwardRef } from "react"

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "success" | "error" | "warning"
  size?: "sm" | "md" | "lg"
  fullWidth?: boolean
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", fullWidth, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200",
          "focus:outline-none focus:ring-2 focus:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          {
            "bg-[#A16AE8] text-white hover:bg-[#8A4FD9] focus:ring-[#A16AE8]": variant === "primary",
            "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-400 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600":
              variant === "secondary",
            "border-2 border-[#A16AE8] text-[#A16AE8] hover:bg-[#A16AE8] hover:text-white focus:ring-[#A16AE8]":
              variant === "outline",
            "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800": variant === "ghost",
            "bg-[#1DD1A1] text-white hover:bg-[#16A881] focus:ring-[#1DD1A1]": variant === "success",
            "bg-[#EF4444] text-white hover:bg-[#DC2626] focus:ring-[#EF4444]": variant === "error",
            "bg-[#FFA502] text-black hover:bg-[#E69500] focus:ring-[#FFA502]": variant === "warning",
          },
          {
            "px-3 py-1.5 text-sm": size === "sm",
            "px-4 py-2 text-base": size === "md",
            "px-6 py-3 text-lg": size === "lg",
          },
          fullWidth && "w-full",
          className,
        )}
        {...props}
      >
        {children}
      </button>
    )
  },
)

Button.displayName = "Button"
