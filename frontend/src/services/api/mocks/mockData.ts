import type { AuthTokenResponse } from "../../../features/auth/types/auth.types"
import type {
  InterviewResponse,
  InterviewMessagesResponse,
  SendMessageResponse,
} from "../../../features/interview/services/interviewService"

/**
 * Mock data for API responses
 * Used when NEXT_PUBLIC_MOCK_API=true
 */

export const mockAuthResponse: AuthTokenResponse = {
  token: "mock-jwt-token-12345",
  candidate_id: "mock-candidate-id-001",
  email: "demo@example.com",
}

export const mockInterviewResponse: InterviewResponse = {
  id: "mock-interview-001",
  candidate_id: "mock-candidate-id-001",
  resume_id: null,
  role_type: "Software Engineer",
  status: "in_progress",
  started_at: new Date().toISOString(),
  completed_at: null,
  duration_seconds: null,
  ai_model_used: "gpt-4",
  total_tokens_used: 0,
  created_at: new Date().toISOString(),
}

export const mockInterviewMessages: InterviewMessagesResponse = {
  interview_id: "mock-interview-001",
  total_count: 2,
  skip: 0,
  limit: 50,
  messages: [
    {
      id: "msg-001",
      sequence_number: 1,
      message_type: "ai_question",
      content_text:
        "Hello! Welcome to your technical interview. Can you tell me about your experience with React and modern web development?",
      created_at: new Date().toISOString(),
    },
    {
      id: "msg-002",
      sequence_number: 2,
      message_type: "candidate_response",
      content_text: "I have 3 years of experience working with React, building scalable web applications.",
      created_at: new Date().toISOString(),
    },
  ],
}

export const mockSendMessageResponse: SendMessageResponse = {
  message_id: "msg-003",
  ai_response: "That's great! Can you describe a challenging problem you solved using React hooks?",
  question_number: 2,
  total_questions: 10,
  session_state: {
    current_difficulty: "medium",
    skill_boundaries: {
      react: "intermediate",
      javascript: "advanced",
    },
  },
}

// Helper to simulate network delay
export const mockDelay = (ms = 500) => new Promise((resolve) => setTimeout(resolve, ms))
