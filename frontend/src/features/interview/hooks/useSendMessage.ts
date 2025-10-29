import { useMutation } from '@tanstack/react-query';
import { sendInterviewMessage } from '../services/interviewService';
import type { SendMessageResponse } from '../services/interviewService';
import { useInterviewStore } from '../store/interviewStore';

interface UseSendMessageParams {
  sessionId: string;
}

/**
 * Custom hook for sending interview messages
 * Uses TanStack Query for mutation management
 * Updates interview store on success
 */
export function useSendMessage({ sessionId }: UseSendMessageParams) {
  const { addMessage, setAiTyping, updateProgress } = useInterviewStore();

  return useMutation<SendMessageResponse, Error, string>({
    mutationFn: (messageText: string) =>
      sendInterviewMessage(sessionId, messageText),
    
    onMutate: async (messageText: string) => {
      // Optimistic update: Add candidate message immediately
      addMessage({
        role: 'candidate',
        content: messageText,
      });
      
      // Show typing indicator
      setAiTyping(true);
    },
    
    onSuccess: (data) => {
      // Add AI response to messages
      addMessage({
        role: 'ai',
        content: data.ai_response,
      });
      
      // Update progress
      updateProgress(data.question_number, data.total_questions);
      
      // Hide typing indicator
      setAiTyping(false);
    },
    
    onError: (error) => {
      // Hide typing indicator on error
      setAiTyping(false);
      
      // Log error (in production, show notification to user)
      console.error('Failed to send message:', error);
    },
  });
}
