/**
 * Interview Feature Type Definitions
 */

export type InterviewStatus = 
  | 'not_started'
  | 'in_progress'
  | 'completed'
  | 'abandoned';

export interface Message {
  id: string;
  role: 'ai' | 'candidate';
  content: string;
  timestamp: number;
}

export interface CompletionData {
  interview_id: string;
  completed_at: string;
  duration_seconds: number;
  questions_answered: number;
  skill_boundaries_identified: number;
  message: string;
}

export interface InterviewState {
  sessionId: string | null;
  messages: Message[];
  currentQuestion: number;
  totalQuestions: number;
  isAiTyping: boolean;
  status: InterviewStatus;
  isCompleted: boolean;
  completionData: CompletionData | null;
}

export interface InterviewActions {
  setSessionId: (sessionId: string) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setMessages: (messages: Message[]) => void;
  clearMessages: () => void;
  setAiTyping: (isTyping: boolean) => void;
  updateProgress: (current: number, total: number) => void;
  setStatus: (status: InterviewStatus) => void;
  setCompleted: (isCompleted: boolean) => void;
  setCompletionData: (completionData: CompletionData) => void;
  reset: () => void;
}

export type InterviewStore = InterviewState & InterviewActions;
