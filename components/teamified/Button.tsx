"use client"

import type React from "react"

export interface ButtonProps {
  children: React.ReactNode
  variant?: "primary" | "secondary" | "tertiary"
  size?: "small" | "medium" | "large"
  disabled?: boolean
  onClick?: () => void
}

export function Button({ children, variant = "primary", size = "medium", disabled = false, onClick }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled}>
      {children}
    </button>
  )
}
