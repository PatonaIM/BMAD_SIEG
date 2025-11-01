import "@testing-library/jest-dom"
import { vi, beforeEach } from "vitest"

// Mock fetch for tests
global.fetch = vi.fn()

// Helper to setup fetch mock responses
export const mockFetchResponse = (data: any, status = 200) => {
  ;(global.fetch as any).mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
  })
}

// Helper to setup fetch mock error
export const mockFetchError = (error: string) => {
  ;(global.fetch as any).mockRejectedValueOnce(new Error(error))
}

// Reset mocks before each test
beforeEach(() => {
  vi.clearAllMocks()
})
