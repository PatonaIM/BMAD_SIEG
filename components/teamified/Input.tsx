import { cn } from "@/lib/utils"
import { type InputHTMLAttributes, forwardRef } from "react"

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
  helperText?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({ className, error, helperText, ...props }, ref) => {
  return (
    <div className="w-full">
      <input
        ref={ref}
        className={cn(
          "w-full px-4 py-2 rounded-lg border transition-all duration-200",
          "bg-white dark:bg-gray-800",
          "text-gray-900 dark:text-gray-100",
          "placeholder:text-gray-400 dark:placeholder:text-gray-500",
          "focus:outline-none focus:ring-2 focus:ring-offset-0",
          error
            ? "border-[#EF4444] focus:ring-[#EF4444]"
            : "border-gray-300 dark:border-gray-600 focus:ring-[#A16AE8] focus:border-[#A16AE8]",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          className,
        )}
        {...props}
      />
      {helperText && (
        <p className={cn("mt-1 text-sm", error ? "text-[#EF4444]" : "text-gray-500 dark:text-gray-400")}>
          {helperText}
        </p>
      )}
    </div>
  )
})

Input.displayName = "Input"
