"use client"

import type React from "react"
import { Button as MuiButton, CircularProgress, Box } from "@mui/material"
import type { SxProps, Theme } from "@mui/material/styles"

export interface ButtonProps {
  variant?: "primary" | "secondary" | "danger" | "ghost"
  size?: "standard" | "compact"
  disabled?: boolean
  loading?: boolean
  startIcon?: React.ReactNode
  endIcon?: React.ReactNode
  fullWidth?: boolean
  onClick?: () => void
  children: React.ReactNode
  type?: "button" | "submit" | "reset"
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "standard",
  disabled = false,
  loading = false,
  startIcon,
  endIcon,
  fullWidth = false,
  onClick,
  children,
  type = "button",
}) => {
  const getVariantStyles = (): SxProps<Theme> => {
    const baseStyles: SxProps<Theme> = {
      minHeight: size === "standard" ? "44px" : "36px",
      padding: size === "standard" ? "12px 24px" : "8px 16px",
      borderRadius: "8px",
      fontSize: "14px",
      fontWeight: 500,
      textTransform: "none",
      transition: "all 150ms ease-out",
      opacity: loading ? 0.7 : 1,
      pointerEvents: loading ? "none" : "auto",
      "&:active": {
        transform: "scale(0.95)",
        transition: "all 150ms cubic-bezier(0.4, 0.0, 0.2, 1)",
      },
      "&.Mui-disabled": {
        opacity: 0.7,
        cursor: "not-allowed",
      },
    }

    switch (variant) {
      case "primary":
        return {
          ...baseStyles,
          backgroundColor: "#A16AE8",
          color: "#FFFFFF",
          "&:hover": {
            backgroundColor: "#7B3FD6",
          },
        }
      case "secondary":
        return {
          ...baseStyles,
          backgroundColor: "transparent",
          color: "#2C3E50",
          border: "1px solid #E0E4E8",
          "&:hover": {
            backgroundColor: "#F5F6F7",
          },
        }
      case "danger":
        return {
          ...baseStyles,
          backgroundColor: "#EF4444",
          color: "#FFFFFF",
          "&:hover": {
            backgroundColor: "#DC2626",
          },
        }
      case "ghost":
        return {
          ...baseStyles,
          backgroundColor: "transparent",
          color: "#7F8C8D",
          border: "none",
          "&:hover": {
            backgroundColor: "rgba(0, 0, 0, 0.04)",
          },
        }
      default:
        return baseStyles
    }
  }

  return (
    <MuiButton
      sx={getVariantStyles()}
      disabled={disabled || loading}
      onClick={onClick}
      fullWidth={fullWidth}
      type={type}
      startIcon={loading ? null : startIcon}
      endIcon={loading ? null : endIcon}
      aria-label={typeof children === "string" ? children : undefined}
      aria-busy={loading}
    >
      {loading ? (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <CircularProgress size={16} sx={{ color: "inherit" }} />
          {children}
        </Box>
      ) : (
        children
      )}
    </MuiButton>
  )
}
