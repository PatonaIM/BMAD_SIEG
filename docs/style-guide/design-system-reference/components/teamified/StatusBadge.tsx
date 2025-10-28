import type React from "react"
import { Box, Typography } from "@mui/material"
import type { SxProps, Theme } from "@mui/material/styles"

export interface StatusBadgeProps {
  variant: "success" | "warning" | "error" | "info"
  icon?: React.ReactNode
  children: React.ReactNode
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ variant, icon, children }) => {
  const getVariantStyles = (): SxProps<Theme> => {
    const baseStyles: SxProps<Theme> = {
      display: "inline-flex",
      alignItems: "center",
      gap: "4px",
      height: "24px",
      padding: "4px 12px",
      borderRadius: "16px",
      fontSize: "12px",
      fontWeight: 500,
      textTransform: "capitalize",
    }

    switch (variant) {
      case "success":
        return {
          ...baseStyles,
          backgroundColor: "#1DD1A1",
          color: "#FFFFFF",
        }
      case "warning":
        return {
          ...baseStyles,
          backgroundColor: "#FFA502",
          color: "#FFFFFF",
        }
      case "error":
        return {
          ...baseStyles,
          backgroundColor: "#EF4444",
          color: "#FFFFFF",
        }
      case "info":
        return {
          ...baseStyles,
          backgroundColor: "#D4F5EE",
          color: "#1DD1A1",
        }
      default:
        return baseStyles
    }
  }

  return (
    <Box sx={getVariantStyles()} role="status" aria-label={`${variant} status`}>
      {icon && <Box sx={{ display: "flex", alignItems: "center", fontSize: "14px" }}>{icon}</Box>}
      <Typography component="span" sx={{ fontSize: "inherit", fontWeight: "inherit" }}>
        {children}
      </Typography>
    </Box>
  )
}
