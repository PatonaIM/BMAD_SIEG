"use client"
import { Box } from "@mui/material"

interface WaveformVisualizerProps {
  audioLevel: number
  isActive: boolean
  barCount?: number
}

export function WaveformVisualizer({ audioLevel, isActive, barCount = 25 }: WaveformVisualizerProps) {
  // Generate random heights based on audio level for visualization
  const bars = Array.from({ length: barCount }, (_, i) => {
    if (!isActive) return 8

    // Create wave pattern with audio level influence
    const baseHeight = Math.sin(i * 0.5) * 20 + 30
    const audioInfluence = audioLevel * 40
    const randomVariation = Math.random() * 10

    return Math.max(8, Math.min(60, baseHeight + audioInfluence + randomVariation))
  })

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "4px",
        height: "60px",
        width: "100%",
        backgroundColor: "#F5F6F7",
        borderRadius: "8px",
        padding: "8px",
      }}
    >
      {bars.map((height, index) => (
        <Box
          key={index}
          sx={{
            width: "4px",
            height: `${height}px`,
            backgroundColor: isActive ? "#1DD1A1" : "#E0E0E0",
            borderRadius: "2px",
            transition: "height 100ms linear, background-color 250ms ease",
          }}
        />
      ))}
    </Box>
  )
}
