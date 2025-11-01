import { mockAuthResponse, mockInterviewResponse, mockInterviewMessages, mockSendMessageResponse } from "./mockData"

const sessionProgress = new Map<string, number>()

/**
 * Mock response router
 * Maps API endpoints to mock data responses
 */
export function getMockResponse<T>(endpoint: string, method: string): T {
  console.log("[v0] Mock API - Endpoint:", endpoint, "Method:", method)

  // Auth endpoints
  if (endpoint === "/candidates/register" && method === "POST") {
    return mockAuthResponse as T
  }

  if (endpoint === "/auth/login" && method === "POST") {
    return mockAuthResponse as T
  }

  // Interview endpoints
  if (endpoint === "/interviews/start" && method === "POST") {
    return mockInterviewResponse as T
  }

  if (endpoint.match(/\/interviews\/([^/]+)\/messages$/) && method === "GET") {
    return mockInterviewMessages as T
  }

  if (endpoint.match(/\/interviews\/([^/]+)\/messages$/) && method === "POST") {
    const sessionId = endpoint.match(/\/interviews\/([^/]+)\/messages$/)?.[1] || "default"

    // Get current question number for this session (default to 1)
    const currentQuestion = (sessionProgress.get(sessionId) || 0) + 1
    sessionProgress.set(sessionId, currentQuestion)

    const totalQuestions = 5 // Set to 5 questions for easier testing

    console.log(`[v0] Mock interview progress: ${currentQuestion}/${totalQuestions}`)

    return {
      ...mockSendMessageResponse,
      question_number: currentQuestion,
      total_questions: totalQuestions,
      ai_response:
        currentQuestion >= totalQuestions
          ? "Thank you for completing the interview! Your responses have been recorded."
          : `Question ${currentQuestion}: ${mockSendMessageResponse.ai_response}`,
    } as T
  }

  if (endpoint.match(/\/interviews\/[^/]+\/complete$/) && method === "POST") {
    const sessionId = endpoint.match(/\/interviews\/([^/]+)\/complete$/)?.[1]
    if (sessionId) {
      // Reset progress for this session
      sessionProgress.delete(sessionId)
    }
    return {
      success: true,
      completed_at: new Date().toISOString(),
    } as T
  }

  // Default fallback
  console.warn("[v0] Mock API - No mock data found for:", endpoint, method)
  return {} as T
}
