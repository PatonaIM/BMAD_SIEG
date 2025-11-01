import { apiClient } from "../../../services/api/client"

/**
 * Interview API Service
 * Handles communication with interview endpoints
 */

export interface StartInterviewRequest {
  role_type: string
  resume_id?: string | null
}

export interface InterviewResponse {
  id: string
  candidate_id: string
  resume_id: string | null
  role_type: string
  status: string
  started_at: string | null
  completed_at: string | null
  duration_seconds: number | null
  ai_model_used: string | null
  total_tokens_used: number
  created_at: string
}

export interface SendMessageRequest {
  session_id: string
  message_text: string
}

export interface SendMessageResponse {
  message_id: string
  ai_response: string
  question_number: number
  total_questions: number
  interview_complete?: boolean
  session_state: {
    current_difficulty: string
    skill_boundaries: Record<string, string>
    questions_asked?: number
  }
}

export interface InterviewMessage {
  id: string
  sequence_number: number
  message_type: "ai_question" | "candidate_response"
  content_text: string
  created_at: string
}

export interface InterviewMessagesResponse {
  interview_id: string
  total_count: number
  skip: number
  limit: number
  messages: InterviewMessage[]
}

/**
 * Start a new interview
 * Endpoint: POST /api/v1/interviews/start
 * Returns interview with first AI question already generated
 */
export const startInterview = async (data: StartInterviewRequest): Promise<InterviewResponse> => {
  const response = await apiClient.post<InterviewResponse>("/interviews/start", data)

  return response
}

/**
 * Get interview messages (conversation history)
 * Endpoint: GET /api/v1/interviews/{id}/messages
 */
export const getInterviewMessages = async (interviewId: string): Promise<InterviewMessagesResponse> => {
  const response = await apiClient.get<InterviewMessagesResponse>(`/interviews/${interviewId}/messages`)

  return response
}

/**
 * Send candidate message and receive AI response
 * Endpoint: POST /api/v1/interviews/{id}/messages
 * Connected to real backend API (Story 1.7)
 */
export const sendInterviewMessage = async (sessionId: string, messageText: string): Promise<SendMessageResponse> => {
  const response = await apiClient.post<SendMessageResponse>(`/interviews/${sessionId}/messages`, {
    message_text: messageText,
  })

  return response
}

/**
 * Complete an interview
 * Endpoint: POST /api/v1/interviews/{id}/complete
 * Marks the interview as completed and returns completion metrics
 */
export interface InterviewCompleteResponse {
  interview_id: string
  completed_at: string
  duration_seconds: number
  questions_answered: number
  skill_boundaries_identified: number
  message: string
}

export const completeInterview = async (interviewId: string): Promise<InterviewCompleteResponse> => {
  const response = await apiClient.post<InterviewCompleteResponse>(`/interviews/${interviewId}/complete`, {})

  return response
}

/**
 * Get interview transcript
 * Endpoint: GET /api/v1/interviews/{id}/transcript
 * Returns full conversation history with all messages
 */
export interface TranscriptMessage {
  sequence_number: number
  message_type: "ai_question" | "candidate_response"
  content_text: string
  created_at: string
  audio_url?: string | null
}

export interface InterviewTranscriptResponse {
  interview_id: string
  started_at: string
  completed_at: string | null
  duration_seconds: number | null
  messages: TranscriptMessage[]
}

export const getInterviewTranscript = async (interviewId: string): Promise<InterviewTranscriptResponse> => {
  const response = await apiClient.get<InterviewTranscriptResponse>(`/interviews/${interviewId}/transcript`)

  return response
}
