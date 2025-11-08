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

export interface SkillAssessment {
  skill_area: string;
  proficiency_level: "novice" | "intermediate" | "proficient" | "expert";
  display_name: string;
}

export interface InterviewHighlight {
  title: string;
  description: string;
  skill_area: string | null;
}

export interface GrowthArea {
  skill_area: string;
  suggestion: string;
  display_name: string;
}

export interface CompletionData {
  interview_id: string;
  completed_at: string;
  duration_seconds: number;
  questions_answered: number;
  skill_boundaries_identified: number;
  message: string;
  skill_assessments?: SkillAssessment[];
  highlights?: InterviewHighlight[];
  growth_areas?: GrowthArea[];
}

export type InterviewFlowState = 'ai_speaking' | 'ai_listening' | 'candidate_speaking' | 'processing';
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
  // Realtime mode state
  useRealtimeMode: boolean;
  connectionState: ConnectionState;
  realtimeLatency: number | null;
  audioLevel: number;
  // Caption state (Story 2.4)
  currentCaption: string | null;
  captionsEnabled: boolean;
  showCaption: boolean;
  selfViewVisible: boolean;
  // Camera state (Story 2.5)
  cameraEnabled: boolean;
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
  // Realtime mode actions
  toggleRealtimeMode: () => void;
  setConnectionState: (state: ConnectionState) => void;
  updateLatency: (latency: number) => void;
  setAudioLevel: (level: number) => void;
  // Caption actions (Story 2.4)
  setCurrentCaption: (text: string | null) => void;
  setCaptionsEnabled: (enabled: boolean) => void;
  setShowCaption: (show: boolean) => void;
  setSelfViewVisible: (visible: boolean) => void;
  // Camera actions (Story 2.5)
  setCameraEnabled: (enabled: boolean) => void;
}

export type InterviewStore = InterviewState & InterviewActions;
