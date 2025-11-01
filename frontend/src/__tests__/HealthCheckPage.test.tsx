import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import HealthCheckPage from "../../app/health/page"

global.fetch = vi.fn()

describe("HealthCheckPage", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders page title and heading", () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: "healthy",
        version: "1.0.0",
        timestamp: "2025-10-29T00:00:00Z",
      }),
    } as Response)

    render(<HealthCheckPage />)

    expect(screen.getByText("Teamified Candidates Portal")).toBeInTheDocument()
    expect(screen.getByText("Backend Health Check")).toBeInTheDocument()
  })

  it("displays connected status when backend is healthy", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: "healthy",
        version: "1.0.0",
        timestamp: "2025-10-29T00:00:00Z",
      }),
    } as Response)

    render(<HealthCheckPage />)

    await waitFor(() => {
      expect(screen.getByText("Connected")).toBeInTheDocument()
    })
  })

  it("displays backend version when connected", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: "healthy",
        version: "1.0.0",
        timestamp: "2025-10-29T00:00:00Z",
      }),
    } as Response)

    render(<HealthCheckPage />)

    await waitFor(() => {
      expect(screen.getByText(/Backend Version:/)).toBeInTheDocument()
      expect(screen.getByText(/1.0.0/)).toBeInTheDocument()
    })
  })

  it("displays disconnected status when backend fails", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"))

    render(<HealthCheckPage />)

    await waitFor(() => {
      expect(screen.getByText("Disconnected")).toBeInTheDocument()
    })
  })

  it("displays error message when backend is unreachable", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Failed to connect"))

    render(<HealthCheckPage />)

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument()
      expect(screen.getByText(/Failed to connect/)).toBeInTheDocument()
    })
  })

  it("has a refresh button that fetches health status", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "healthy",
        version: "1.0.0",
        timestamp: "2025-10-29T00:00:00Z",
      }),
    } as Response)

    render(<HealthCheckPage />)

    const refreshButton = await screen.findByText("Refresh Now")
    expect(refreshButton).toBeInTheDocument()

    // Click the refresh button
    await userEvent.click(refreshButton)

    // Should call fetch at least twice (initial + manual refresh)
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2)
    })
  })
})
