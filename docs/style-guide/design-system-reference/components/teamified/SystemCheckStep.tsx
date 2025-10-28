"use client"

import type React from "react"
import { useState } from "react"
import { Box, Typography, Collapse, IconButton } from "@mui/material"
import { CheckCircle as CheckCircleIcon, Close as CloseIcon, ExpandMore as ExpandMoreIcon } from "@mui/icons-material"
import { CircularProgress } from "@mui/material"

export type StepStatus = "pending" | "inProgress" | "completed" | "failed"

interface SystemCheckStepProps {
  stepNumber: number
  title: string
  description: string
  status: StepStatus
  statusMessage?: string
  errorMessage?: string
  troubleshootingContent?: React.ReactNode
  children?: React.ReactNode
  onRetry?: () => void
}

export function SystemCheckStep({
  stepNumber,
  title,
  description,
  status,
  statusMessage,
  errorMessage,
  troubleshootingContent,
  children,
  onRetry,
}: SystemCheckStepProps) {
  const [showTroubleshooting, setShowTroubleshooting] = useState(false)

  const getIndicatorContent = () => {
    switch (status) {
      case "pending":
        return (
          <Typography
            sx={{
              fontSize: "16px",
              fontWeight: 600,
              color: "#9E9E9E",
            }}
          >
            {stepNumber}
          </Typography>
        )
      case "inProgress":
        return <CircularProgress size={20} sx={{ color: "#A16AE8" }} />
      case "completed":
        return <CheckCircleIcon sx={{ fontSize: "20px", color: "#FFFFFF" }} />
      case "failed":
        return <CloseIcon sx={{ fontSize: "20px", color: "#FFFFFF" }} />
    }
  }

  const getIndicatorColor = () => {
    switch (status) {
      case "pending":
        return "#E0E0E0"
      case "inProgress":
        return "#F3EBFF"
      case "completed":
        return "#1DD1A1"
      case "failed":
        return "#FF6B6B"
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case "completed":
        return "#1DD1A1"
      case "failed":
        return "#FF6B6B"
      case "inProgress":
        return "#A16AE8"
      default:
        return "#757575"
    }
  }

  return (
    <Box
      sx={{
        backgroundColor: "#FFFFFF",
        border: "1px solid #E0E0E0",
        borderRadius: "12px",
        padding: "16px",
        transition: "all 250ms ease",
        "&:hover":
          status === "inProgress"
            ? {
                boxShadow: "0 2px 8px rgba(161, 106, 232, 0.1)",
              }
            : {},
      }}
      role="region"
      aria-label={`${title} - ${status}`}
    >
      <Box sx={{ display: "flex", gap: "16px" }}>
        {/* Indicator Circle */}
        <Box
          sx={{
            width: "32px",
            height: "32px",
            borderRadius: "50%",
            backgroundColor: getIndicatorColor(),
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
            transition: "all 500ms ease",
            transform: status === "completed" ? "scale(1.1)" : "scale(1)",
          }}
          aria-hidden="true"
        >
          {getIndicatorContent()}
        </Box>

        {/* Content */}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography
            variant="body1"
            sx={{
              fontWeight: 600,
              fontSize: "16px",
              color: "#1A1A1A",
              marginBottom: "4px",
            }}
          >
            {title}
          </Typography>

          <Typography
            variant="body2"
            sx={{
              fontSize: "14px",
              color: "#757575",
              marginBottom: statusMessage ? "8px" : 0,
            }}
          >
            {description}
          </Typography>

          {statusMessage && (
            <Typography
              variant="caption"
              sx={{
                fontSize: "12px",
                color: getStatusColor(),
                fontWeight: 500,
                display: "block",
              }}
              role="status"
              aria-live="polite"
            >
              {statusMessage}
            </Typography>
          )}

          {/* Step-specific content */}
          {children && <Box sx={{ marginTop: "16px" }}>{children}</Box>}

          {/* Error message and troubleshooting */}
          {status === "failed" && errorMessage && (
            <Box sx={{ marginTop: "12px" }}>
              <Typography
                variant="body2"
                sx={{
                  fontSize: "14px",
                  color: "#FF6B6B",
                  marginBottom: "8px",
                }}
              >
                {errorMessage}
              </Typography>

              {troubleshootingContent && (
                <>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      cursor: "pointer",
                      marginBottom: "8px",
                    }}
                    onClick={() => setShowTroubleshooting(!showTroubleshooting)}
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        fontSize: "14px",
                        color: "#A16AE8",
                        fontWeight: 500,
                      }}
                    >
                      Troubleshooting tips
                    </Typography>
                    <IconButton
                      size="small"
                      sx={{
                        transform: showTroubleshooting ? "rotate(180deg)" : "rotate(0deg)",
                        transition: "transform 250ms ease",
                      }}
                    >
                      <ExpandMoreIcon fontSize="small" />
                    </IconButton>
                  </Box>

                  <Collapse in={showTroubleshooting}>
                    <Box
                      sx={{
                        backgroundColor: "#F5F6F7",
                        borderRadius: "8px",
                        padding: "12px",
                        marginBottom: "12px",
                      }}
                    >
                      {troubleshootingContent}
                    </Box>
                  </Collapse>
                </>
              )}

              {onRetry && (
                <button
                  onClick={onRetry}
                  style={{
                    backgroundColor: "#A16AE8",
                    color: "#FFFFFF",
                    border: "none",
                    borderRadius: "8px",
                    padding: "8px 16px",
                    fontSize: "14px",
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "background-color 250ms ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "#8E4FD6"
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "#A16AE8"
                  }}
                >
                  Retry
                </button>
              )}
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  )
}
