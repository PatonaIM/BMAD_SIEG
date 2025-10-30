"use client"

import { useEffect, useState } from "react"
import { Box, Container, Typography, Button, Paper } from "@mui/material"

interface HealthCheckResponse {
  status: string
  version: string
  timestamp: string
}

export default function HealthCheckPage() {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  const fetchHealth = async () => {
    try {
      const response = await fetch("http://localhost:8000/health")
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setHealth(data)
      setError(null)
      setLastChecked(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect to backend")
      setHealth(null)
    }
  }

  useEffect(() => {
    // Initial fetch
    fetchHealth()

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000)

    return () => clearInterval(interval)
  }, [])

  const isConnected = health !== null && health.status === "healthy"

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Teamified Candidates Portal
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom color="text.secondary">
          Backend Health Check
        </Typography>

        <Paper
          elevation={3}
          sx={{
            p: 3,
            mt: 3,
            bgcolor: isConnected ? "success.light" : "error.light",
            border: 2,
            borderColor: isConnected ? "success.main" : "error.main",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                bgcolor: isConnected ? "success.main" : "error.main",
              }}
            />
            <Typography variant="body1" fontWeight="bold">
              Status: {isConnected ? "Connected" : "Disconnected"}
            </Typography>
          </Box>

          {health && (
            <>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Backend Version:</strong> {health.version}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Backend Timestamp:</strong> {new Date(health.timestamp).toLocaleString()}
              </Typography>
            </>
          )}

          {error && (
            <Typography variant="body1" color="error.dark" sx={{ mb: 1 }}>
              <strong>Error:</strong> {error}
            </Typography>
          )}

          {lastChecked && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Last checked: {lastChecked.toLocaleTimeString()}
              <span style={{ marginLeft: "0.5rem" }}>(refreshes every 30s)</span>
            </Typography>
          )}
        </Paper>

        <Box sx={{ mt: 3 }}>
          <Button variant="contained" onClick={fetchHealth}>
            Refresh Now
          </Button>
        </Box>

        <Paper elevation={1} sx={{ p: 2, mt: 3, bgcolor: "grey.100" }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Frontend running on: http://localhost:3000
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Backend API: http://localhost:8000
          </Typography>
        </Paper>
      </Box>
    </Container>
  )
}
