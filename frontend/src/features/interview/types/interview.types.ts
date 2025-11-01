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

export type InterviewFlowState = 'ai_speaking' | 'ai_listening' | 'candidate_speaking' | 'processing';
export type InputMode = 'voice' | 'text';
export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface InterviewState {
  sessionId: string | null;
  messages: Message[];
  currentQuestion: number;
  totalQuestions: number;
  isAiTyping: boolean;
  status: InterviewStatus;
  isCompleted: boolean;
  completionData: CompletionData | null;
  // Audio recording state
  isRecording: boolean;
  audioPermissionGranted: boolean;
  recordingError: string | null;
  // Voice interview state
  interviewState: InterviewFlowState;
  inputMode: InputMode;
  currentAudioUrl: string | null;
  // Realtime mode state
  useRealtimeMode: boolean;
  connectionState: ConnectionState;
  realtimeLatency: number | null;
  audioLevel: number;
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
  // Audio recording actions
  setRecording: (isRecording: boolean) => void;
  setAudioPermission: (granted: boolean) => void;
  setRecordingError: (error: string | null) => void;
  // Voice interview actions
  setInterviewState: (state: InterviewFlowState) => void;
  setInputMode: (mode: InputMode) => void;
  setCurrentAudioUrl: (url: string | null) => void;
  // Realtime mode actions
  toggleRealtimeMode: () => void;
  setConnectionState: (state: ConnectionState) => void;
  updateLatency: (latency: number) => void;
  setAudioLevel: (level: number) => void;
}

export type InterviewStore = InterviewState & InterviewActions;
