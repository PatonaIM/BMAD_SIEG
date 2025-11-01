export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1",
  mockApi: process.env.NEXT_PUBLIC_MOCK_API === "true",
} as const
