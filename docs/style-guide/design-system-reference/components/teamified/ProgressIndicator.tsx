import type React from "react"
import { Box, LinearProgress, CircularProgress, Typography, Step, StepLabel, Stepper } from "@mui/material"
import { CheckCircle } from "@mui/icons-material"

export interface ProgressIndicatorProps {
  variant: "linear" | "circular" | "stepper"
  value?: number
  steps?: number
  currentStep?: number
  size?: "small" | "standard"
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  variant,
  value = 0,
  steps = 4,
  currentStep = 1,
  size = "standard",
}) => {
  if (variant === "linear") {
    return (
      <Box sx={{ width: "100%" }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
          <Typography sx={{ fontSize: "14px", fontWeight: 500, color: "#A16AE8" }}>Progress</Typography>
          <Typography sx={{ fontSize: "14px", fontWeight: 500, color: "#A16AE8" }}>{Math.round(value)}%</Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={value}
          sx={{
            height: "8px",
            borderRadius: "4px",
            backgroundColor: "#E0E4E8",
            "& .MuiLinearProgress-bar": {
              backgroundColor: "#A16AE8",
              borderRadius: "4px",
              transition: "transform 400ms ease-out",
            },
          }}
          aria-label={`Progress: ${Math.round(value)}%`}
        />
      </Box>
    )
  }

  if (variant === "circular") {
    const circularSize = size === "standard" ? 40 : 24
    return (
      <CircularProgress
        size={circularSize}
        thickness={3}
        sx={{
          color: "#A16AE8",
        }}
        aria-label="Loading"
      />
    )
  }

  if (variant === "stepper") {
    return (
      <Box sx={{ width: "100%" }}>
        <Stepper activeStep={currentStep - 1} alternativeLabel>
          {Array.from({ length: steps }, (_, index) => (
            <Step key={index} completed={index < currentStep - 1}>
              <StepLabel
                StepIconComponent={({ active, completed }) => (
                  <Box
                    sx={{
                      width: "32px",
                      height: "32px",
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      backgroundColor: completed ? "#1DD1A1" : active ? "#A16AE8" : "#E0E4E8",
                      color: completed || active ? "#FFFFFF" : "#7F8C8D",
                      fontSize: "14px",
                      fontWeight: 500,
                    }}
                  >
                    {completed ? <CheckCircle sx={{ fontSize: "20px", color: "#FFFFFF" }} /> : index + 1}
                  </Box>
                )}
              >
                <Typography
                  sx={{
                    fontSize: "12px",
                    fontWeight: 500,
                    color: index < currentStep ? "#2C3E50" : "#7F8C8D",
                    marginTop: "8px",
                  }}
                >
                  Step {index + 1}
                </Typography>
              </StepLabel>
            </Step>
          ))}
        </Stepper>
        <Typography
          sx={{
            fontSize: "14px",
            fontWeight: 500,
            color: "#2C3E50",
            textAlign: "center",
            marginTop: "16px",
          }}
        >
          Step {currentStep} of {steps}
        </Typography>
      </Box>
    )
  }

  return null
}
