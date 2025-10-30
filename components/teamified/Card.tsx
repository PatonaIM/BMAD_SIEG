import type React from "react"

export interface CardProps {
  children: React.ReactNode
  variant?: "default" | "outlined"
}

export function Card({ children, variant = "default" }: CardProps) {
  return <div>{children}</div>
}
