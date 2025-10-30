"use client"

import { useState, useEffect } from "react"
import { Box, Typography, Link } from "@mui/material"
import { HelpOutline as HelpOutlineIcon } from "@mui/icons-material"
import { SystemCheckStep, type StepStatus } from "@/components/teamified/SystemCheckStep"
import { WaveformVisualizer } from "@/components/teamified/WaveformVisualizer"
import { useMicrophonePermission } from "@/hooks/useMicrophonePermission"
import { useAudioRecording } from "@/hooks/useAudioRecording"

interface Step {
  id: string
  title: string
  description: string
  status: StepStatus
  statusMessage?: string
  errorMessage?: string
}

export default function PreInterviewCheck() {
  const [steps, setSteps] = useState<Step[]>([
    {
      id: "mic-permission",
      title: "Microphone Permission",
      description: "Allow browser access to your microphone",
      status: "pending",
    },
    {
      id: "audio-test",
      title: "Audio Test",
      description: "Record and play back a short audio sample",
      status: "pending",
    },
    {
      id: "connection-test",
      title: "Connection Test",
      description: "Verify your internet connection",
      status: "pending",
    },
  ])

  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [audioConfirmed, setAudioConfirmed] = useState(false)
  const [connectionLatency, setConnectionLatency] = useState<number | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  const { status: permissionStatus, error: permissionError, requestPermission, stream } = useMicrophonePermission()
  const {
    isRecording,
    audioUrl,
    recordingTime,
    audioLevel,
    startRecording,
    stopRecording,
    playRecording,
    resetRecording,
  } = useAudioRecording()

  // Step 1: Microphone Permission
  useEffect(() => {
    if (currentStepIndex === 0 && steps[0].status === "pending") {
      updateStepStatus(0, "inProgress", "Requesting permission...")
      requestPermission()
    }
  }, [currentStepIndex])

  useEffect(() => {
    if (permissionStatus === "granted" && steps[0].status === "inProgress") {
      updateStepStatus(0, "completed", "Permission granted ✓")
      setTimeout(() => {
        setCurrentStepIndex(1)
        updateStepStatus(1, "inProgress", "Speak now...")
      }, 500)
    } else if (permissionStatus === "denied" && steps[0].status === "inProgress") {
      updateStepStatus(0, "failed", undefined, "Microphone access denied")
      setRetryCount((prev) => prev + 1)
    }
  }, [permissionStatus])

  // Step 2: Audio Test - Start recording when step becomes active
  useEffect(() => {
    if (currentStepIndex === 1 && steps[1].status === "inProgress" && stream && !isRecording && !audioUrl) {
      startRecording(stream)
    }
  }, [currentStepIndex, stream, isRecording, audioUrl])

  // Auto-stop recording after 3 seconds
  useEffect(() => {
    if (isRecording && recordingTime >= 3) {
      stopRecording()
      updateStepStatus(1, "inProgress", "Recording complete. Listen to yourself.")
    }
  }, [isRecording, recordingTime])

  // Step 3: Connection Test
  useEffect(() => {
    if (currentStepIndex === 2 && steps[2].status === "inProgress") {
      testConnection()
    }
  }, [currentStepIndex])

  const updateStepStatus = (index: number, status: StepStatus, statusMessage?: string, errorMessage?: string) => {
    setSteps((prev) => prev.map((step, i) => (i === index ? { ...step, status, statusMessage, errorMessage } : step)))
  }

  const handleAudioConfirmation = (confirmed: boolean) => {
    if (confirmed) {
      setAudioConfirmed(true)
      updateStepStatus(1, "completed", "Audio quality confirmed ✓")
      setTimeout(() => {
        setCurrentStepIndex(2)
        updateStepStatus(2, "inProgress", "Testing connection...")
      }, 500)
    } else {
      resetRecording()
      updateStepStatus(1, "inProgress", "Speak now...")
      if (stream) {
        startRecording(stream)
      }
    }
  }

  const testConnection = async () => {
    const startTime = Date.now()

    // Simulate API ping
    await new Promise((resolve) => setTimeout(resolve, Math.random() * 300 + 100))

    const latency = Date.now() - startTime
    setConnectionLatency(latency)

    if (latency < 500) {
      const quality = latency < 200 ? "Good" : "Fair"
      updateStepStatus(2, "completed", `Connection verified ✓ (${latency}ms - ${quality})`)
    } else {
      updateStepStatus(2, "failed", undefined, "Connection unstable")
      setRetryCount((prev) => prev + 1)
    }
  }

  const handleRetryMicrophone = () => {
    updateStepStatus(0, "pending")
    setCurrentStepIndex(0)
    setTimeout(() => {
      updateStepStatus(0, "inProgress", "Requesting permission...")
      requestPermission()
    }, 100)
  }

  const handleRetryConnection = () => {
    updateStepStatus(2, "inProgress", "Testing connection...")
    testConnection()
  }

  const allStepsCompleted = steps.every((step) => step.status === "completed")

  const handleBeginInterview = () => {
    console.log("[v0] Beginning interview...")
    // Navigate to interview page (not implemented)
  }

  const completedCount = steps.filter((step) => step.status === "completed").length

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor: "#FAFBFC",
        padding: { xs: "24px", md: "48px" },
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Box
        sx={{
          maxWidth: "600px",
          width: "100%",
          backgroundColor: "#FFFFFF",
          borderRadius: "16px",
          padding: "24px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
        }}
      >
        {/* Header */}
        <Box sx={{ marginBottom: "32px", textAlign: "center" }}>
          <Box
            sx={{
              width: "48px",
              height: "48px",
              borderRadius: "50%",
              backgroundColor: "#A16AE8",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 16px",
            }}
            aria-label="Teamified logo"
          >
            <Typography
              sx={{
                fontSize: "24px",
                fontWeight: 700,
                color: "#FFFFFF",
              }}
            >
              T
            </Typography>
          </Box>

          <Typography
            variant="h4"
            sx={{
              fontSize: "30px",
              fontWeight: 600,
              color: "#1A1A1A",
              marginBottom: "8px",
            }}
          >
            System Check
          </Typography>

          <Typography
            variant="body1"
            sx={{
              fontSize: "16px",
              color: "#757575",
            }}
          >
            This will only take a minute. We want to make sure everything works perfectly.
          </Typography>
        </Box>

        {/* Progress Checklist */}
        <Box sx={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "32px" }}>
          {/* Step 1: Microphone Permission */}
          <SystemCheckStep
            stepNumber={1}
            title={steps[0].title}
            description={steps[0].description}
            status={steps[0].status}
            statusMessage={steps[0].statusMessage}
            errorMessage={steps[0].errorMessage}
            onRetry={handleRetryMicrophone}
            troubleshootingContent={
              <Box>
                <Typography variant="body2" sx={{ fontSize: "14px", fontWeight: 600, marginBottom: "8px" }}>
                  How to enable microphone access:
                </Typography>
                <Typography variant="body2" sx={{ fontSize: "13px", color: "#757575", marginBottom: "4px" }}>
                  • Chrome: Click the camera icon in address bar
                </Typography>
                <Typography variant="body2" sx={{ fontSize: "13px", color: "#757575", marginBottom: "4px" }}>
                  • Safari: Go to Preferences → Websites → Microphone
                </Typography>
                <Typography variant="body2" sx={{ fontSize: "13px", color: "#757575" }}>
                  • Firefox: Click the shield icon in address bar
                </Typography>
              </Box>
            }
          />

          {/* Step 2: Audio Test */}
          <SystemCheckStep
            stepNumber={2}
            title={steps[1].title}
            description={steps[1].description}
            status={steps[1].status}
            statusMessage={steps[1].statusMessage}
          >
            {steps[1].status === "inProgress" && (
              <Box>
                <WaveformVisualizer audioLevel={audioLevel} isActive={isRecording} barCount={25} />

                {isRecording && (
                  <Typography
                    variant="body2"
                    sx={{
                      fontSize: "14px",
                      color: "#757575",
                      marginTop: "12px",
                      textAlign: "center",
                    }}
                  >
                    Recording... {3 - recordingTime}s remaining
                  </Typography>
                )}

                {!isRecording && audioUrl && (
                  <Box sx={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
                    <button
                      onClick={playRecording}
                      style={{
                        backgroundColor: "#FFFFFF",
                        color: "#A16AE8",
                        border: "2px solid #A16AE8",
                        borderRadius: "8px",
                        padding: "10px 20px",
                        fontSize: "14px",
                        fontWeight: 600,
                        cursor: "pointer",
                        transition: "all 250ms ease",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = "#F3EBFF"
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = "#FFFFFF"
                      }}
                    >
                      Listen to yourself
                    </button>

                    <Typography
                      variant="body2"
                      sx={{
                        fontSize: "14px",
                        color: "#1A1A1A",
                        fontWeight: 500,
                        textAlign: "center",
                      }}
                    >
                      Did it sound clear?
                    </Typography>

                    <Box sx={{ display: "flex", gap: "12px" }}>
                      <button
                        onClick={() => handleAudioConfirmation(true)}
                        style={{
                          flex: 1,
                          backgroundColor: "#1DD1A1",
                          color: "#FFFFFF",
                          border: "none",
                          borderRadius: "8px",
                          padding: "10px 20px",
                          fontSize: "14px",
                          fontWeight: 600,
                          cursor: "pointer",
                          transition: "background-color 250ms ease",
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = "#17B88D"
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = "#1DD1A1"
                        }}
                      >
                        Yes
                      </button>

                      <button
                        onClick={() => handleAudioConfirmation(false)}
                        style={{
                          flex: 1,
                          backgroundColor: "#FFFFFF",
                          color: "#757575",
                          border: "2px solid #E0E0E0",
                          borderRadius: "8px",
                          padding: "10px 20px",
                          fontSize: "14px",
                          fontWeight: 600,
                          cursor: "pointer",
                          transition: "all 250ms ease",
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = "#F5F6F7"
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = "#FFFFFF"
                        }}
                      >
                        Try again
                      </button>
                    </Box>
                  </Box>
                )}
              </Box>
            )}
          </SystemCheckStep>

          {/* Step 3: Connection Test */}
          <SystemCheckStep
            stepNumber={3}
            title={steps[2].title}
            description={steps[2].description}
            status={steps[2].status}
            statusMessage={steps[2].statusMessage}
            errorMessage={steps[2].errorMessage}
            onRetry={handleRetryConnection}
            troubleshootingContent={
              <Box>
                <Typography variant="body2" sx={{ fontSize: "14px", fontWeight: 600, marginBottom: "8px" }}>
                  Connection tips:
                </Typography>
                <Typography variant="body2" sx={{ fontSize: "13px", color: "#757575", marginBottom: "4px" }}>
                  • Check your internet connection
                </Typography>
                <Typography variant="body2" sx={{ fontSize: "13px", color: "#757575", marginBottom: "4px" }}>
                  • Close other bandwidth-heavy applications
                </Typography>
                <Typography variant="body2" sx={{ fontSize: "13px", color: "#757575" }}>
                  • Try moving closer to your WiFi router
                </Typography>
              </Box>
            }
          />
        </Box>

        {/* Footer CTA */}
        <Box sx={{ marginBottom: "24px" }}>
          <button
            onClick={handleBeginInterview}
            disabled={!allStepsCompleted}
            style={{
              width: "100%",
              backgroundColor: allStepsCompleted ? "#A16AE8" : "#E0E0E0",
              color: "#FFFFFF",
              border: "none",
              borderRadius: "8px",
              padding: "14px 24px",
              fontSize: "16px",
              fontWeight: 600,
              cursor: allStepsCompleted ? "pointer" : "not-allowed",
              transition: "all 250ms ease",
              marginBottom: "12px",
            }}
            onMouseEnter={(e) => {
              if (allStepsCompleted) {
                e.currentTarget.style.backgroundColor = "#8E4FD6"
                e.currentTarget.style.transform = "translateY(-2px)"
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(161, 106, 232, 0.3)"
              }
            }}
            onMouseLeave={(e) => {
              if (allStepsCompleted) {
                e.currentTarget.style.backgroundColor = "#A16AE8"
                e.currentTarget.style.transform = "translateY(0)"
                e.currentTarget.style.boxShadow = "none"
              }
            }}
          >
            {allStepsCompleted ? "Begin Interview" : `Complete system check first (${completedCount}/3)`}
          </button>

          {allStepsCompleted && (
            <Typography
              variant="caption"
              sx={{
                fontSize: "12px",
                color: "#757575",
                textAlign: "center",
                display: "block",
              }}
            >
              Estimated time: 20-30 minutes
            </Typography>
          )}

          {retryCount >= 3 && !allStepsCompleted && (
            <Link
              href="#"
              sx={{
                fontSize: "14px",
                color: "#A16AE8",
                textAlign: "center",
                display: "block",
                marginTop: "12px",
                textDecoration: "none",
                "&:hover": {
                  textDecoration: "underline",
                },
              }}
            >
              Skip Check
            </Link>
          )}
        </Box>

        {/* Support Section */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            paddingTop: "24px",
            borderTop: "1px solid #E0E0E0",
          }}
        >
          <HelpOutlineIcon sx={{ fontSize: "18px", color: "#757575" }} />
          <Typography variant="body2" sx={{ fontSize: "14px", color: "#757575" }}>
            Need help?
          </Typography>
          <Link
            href="mailto:support@teamified.com"
            sx={{
              fontSize: "14px",
              color: "#A16AE8",
              textDecoration: "none",
              fontWeight: 500,
              "&:hover": {
                textDecoration: "underline",
              },
            }}
          >
            Contact Support
          </Link>
        </Box>
      </Box>
    </Box>
  )
}
