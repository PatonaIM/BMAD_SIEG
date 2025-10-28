"use client"

import type React from "react"
import { Card as MuiCard, CardContent } from "@mui/material"
import type { SxProps, Theme } from "@mui/material/styles"

export interface CardProps {
  variant?: "default" | "interactive" | "selected"
  onClick?: () => void
  children: React.ReactNode
  className?: string
  sx?: SxProps<Theme>
}

export const Card: React.FC<CardProps> = ({ variant = "default", onClick, children, className, sx }) => {
  const getVariantStyles = (): SxProps<Theme> => {
    const baseStyles: SxProps<Theme> = {
      backgroundColor: "#FFFFFF",
      border: "1px solid #E0E4E8",
      borderRadius: "12px",
      padding: "24px",
      boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)",
    }

    switch (variant) {
      case "interactive":
        return {
          ...baseStyles,
          cursor: "pointer",
          transition: "all 250ms cubic-bezier(0.4, 0.0, 0.2, 1)",
          "&:hover": {
            boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
            transform: "translateY(-2px)",
          },
        }
      case "selected":
        return {
          ...baseStyles,
          border: "2px solid #A16AE8",
        }
      default:
        return baseStyles
    }
  }

  return (
    <MuiCard
      sx={{ ...getVariantStyles(), ...sx }}
      onClick={onClick}
      className={className}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault()
                onClick()
              }
            }
          : undefined
      }
    >
      <CardContent sx={{ padding: 0, "&:last-child": { paddingBottom: 0 } }}>{children}</CardContent>
    </MuiCard>
  )
}
