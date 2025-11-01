"use client"

import { useEffect, useState } from "react"

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
    fetchHealth()
    const interval = setInterval(fetchHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const isConnected = health !== null && health.status === "healthy"

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Teamified Candidates Portal</h1>
      <h2>Backend Health Check</h2>

      <div
        style={{
          padding: "1.5rem",
          borderRadius: "8px",
          backgroundColor: isConnected ? "#d4edda" : "#f8d7da",
          border: `2px solid ${isConnected ? "#28a745" : "#dc3545"}`,
          marginTop: "1rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <div
            style={{
              width: "12px",
              height: "12px",
              borderRadius: "50%",
              backgroundColor: isConnected ? "#28a745" : "#dc3545",
            }}
          />
          <strong>Status:</strong>
          <span>{isConnected ? "Connected" : "Disconnected"}</span>
        </div>

        {health && (
          <>
            <div style={{ marginTop: "0.5rem" }}>
              <strong>Backend Version:</strong> {health.version}
            </div>
            <div style={{ marginTop: "0.5rem" }}>
              <strong>Backend Timestamp:</strong> {new Date(health.timestamp).toLocaleString()}
            </div>
          </>
        )}

        {error && (
          <div style={{ marginTop: "0.5rem", color: "#721c24" }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {lastChecked && (
          <div style={{ marginTop: "1rem", fontSize: "0.875rem", color: "#666" }}>
            Last checked: {lastChecked.toLocaleTimeString()}
            <span style={{ marginLeft: "0.5rem" }}>(refreshes every 30s)</span>
          </div>
        )}
      </div>

      <div style={{ marginTop: "2rem" }}>
        <button
          onClick={fetchHealth}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Refresh Now
        </button>
      </div>

      <div style={{ marginTop: "2rem", fontSize: "0.875rem", color: "#666" }}>
        <p>Frontend running on: http://localhost:3000</p>
        <p>Backend API: http://localhost:8000</p>
      </div>
    </div>
  )
}
