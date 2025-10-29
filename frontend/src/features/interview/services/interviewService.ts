import { apiClient } from '../../../services/api/client';

/**
 * Interview API Service
 * Handles communication with interview endpoints
 */

export interface SendMessageRequest {
  session_id: string;
  message_text: string;
}

export interface SendMessageResponse {
  message_id: string;
  ai_response: string;
  question_number: number;
  total_questions: number;
}

/**
 * Send candidate message and receive AI response
 * Endpoint: POST /api/v1/interviews/{id}/messages
 * Note: Currently mocked via MSW, real implementation in Story 1.7
 */
export const sendInterviewMessage = async (
  sessionId: string,
  messageText: string
): Promise<SendMessageResponse> => {
  const response = await apiClient.post<SendMessageResponse>(
    `/interviews/${sessionId}/messages`,
    { message_text: messageText }
  );
  
  return response;
};
