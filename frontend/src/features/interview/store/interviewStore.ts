import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { InterviewStore, Message } from '../types/interview.types';

const initialState = {
  sessionId: null,
  messages: [],
  currentQuestion: 0,
  totalQuestions: 0,
  isAiTyping: false,
  status: 'not_started' as const,
  isCompleted: false,
  completionData: null,
  // Audio recording state
  isRecording: false,
  audioPermissionGranted: false,
  recordingError: null,
  // Voice interview state
  interviewState: 'ai_listening' as const,
  inputMode: (typeof window !== 'undefined' 
    ? (localStorage.getItem('interview_input_mode') as 'voice' | 'text') 
    : 'voice') || 'voice',
  currentAudioUrl: null,
  // Realtime mode state
  useRealtimeMode: typeof window !== 'undefined' 
    ? (localStorage.getItem('interview_realtime_mode') !== 'false') 
    : true,
  connectionState: 'disconnected' as const,
  realtimeLatency: null,
  audioLevel: 0,
  // Caption state (Story 2.4)
  currentCaption: null,
  captionsEnabled: typeof window !== 'undefined'
    ? (localStorage.getItem('interview_captions_enabled') !== 'false')
    : true,
  showCaption: false,
  selfViewVisible: typeof window !== 'undefined'
    ? (localStorage.getItem('interview_self_view_visible') !== 'false')
    : true,
  // Camera enabled state (Story 2.5)
  cameraEnabled: typeof window !== 'undefined'
    ? (localStorage.getItem('interview_camera_enabled') !== 'false')
    : true,
};

/**
 * Interview Store
 * Manages interview session state, messages, and progress
 */
export const useInterviewStore = create<InterviewStore>()(
  devtools(
    (set) => ({
      ...initialState,

      setSessionId: (sessionId: string) =>
        set({ sessionId }, false, 'setSessionId'),

      addMessage: (message: Omit<Message, 'id' | 'timestamp'>) =>
        set(
          (state) => ({
            messages: [
              ...state.messages,
              {
                ...message,
                id: crypto.randomUUID(),
                timestamp: Date.now(),
              },
            ],
          }),
          false,
          'addMessage'
        ),

      setMessages: (messages: Message[]) =>
        set({ messages }, false, 'setMessages'),

      clearMessages: () =>
        set({ messages: [] }, false, 'clearMessages'),

      setAiTyping: (isTyping: boolean) =>
        set({ isAiTyping: isTyping }, false, 'setAiTyping'),

      updateProgress: (current: number, total: number) =>
        set(
          { currentQuestion: current, totalQuestions: total },
          false,
          'updateProgress'
        ),

      setStatus: (status) => set({ status }, false, 'setStatus'),

      setCompleted: (isCompleted: boolean) =>
        set({ isCompleted, status: isCompleted ? 'completed' : 'in_progress' }, false, 'setCompleted'),

      setCompletionData: (completionData) =>
        set({ completionData, isCompleted: true, status: 'completed' }, false, 'setCompletionData'),

      // Audio recording actions
      setRecording: (isRecording: boolean) =>
        set({ isRecording }, false, 'setRecording'),

      setAudioPermission: (granted: boolean) =>
        set({ audioPermissionGranted: granted }, false, 'setAudioPermission'),

      setRecordingError: (error: string | null) =>
        set({ recordingError: error }, false, 'setRecordingError'),

      // Voice interview actions
      setInterviewState: (interviewState) =>
        set({ interviewState }, false, 'setInterviewState'),

      setInputMode: (inputMode) =>
        set({ inputMode }, false, 'setInputMode'),

      setCurrentAudioUrl: (currentAudioUrl) =>
        set({ currentAudioUrl }, false, 'setCurrentAudioUrl'),

      // Realtime mode actions
      toggleRealtimeMode: () =>
        set((state) => {
          const newMode = !state.useRealtimeMode;
          if (typeof window !== 'undefined') {
            localStorage.setItem('interview_realtime_mode', String(newMode));
          }
          return { useRealtimeMode: newMode };
        }, false, 'toggleRealtimeMode'),

      setConnectionState: (connectionState) =>
        set({ connectionState }, false, 'setConnectionState'),

      updateLatency: (realtimeLatency) =>
        set({ realtimeLatency }, false, 'updateLatency'),

      setAudioLevel: (audioLevel) =>
        set({ audioLevel }, false, 'setAudioLevel'),

      // Caption actions (Story 2.4)
      setCurrentCaption: (currentCaption) =>
        set({ currentCaption }, false, 'setCurrentCaption'),

      setCaptionsEnabled: (captionsEnabled) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('interview_captions_enabled', String(captionsEnabled));
        }
        return set({ captionsEnabled }, false, 'setCaptionsEnabled');
      },

      setShowCaption: (showCaption) =>
        set({ showCaption }, false, 'setShowCaption'),

      setSelfViewVisible: (selfViewVisible) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('interview_self_view_visible', String(selfViewVisible));
        }
        return set({ selfViewVisible }, false, 'setSelfViewVisible');
      },

      setCameraEnabled: (cameraEnabled) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('interview_camera_enabled', String(cameraEnabled));
        }
        return set({ cameraEnabled }, false, 'setCameraEnabled');
      },

      reset: () => set(initialState, false, 'reset'),
    }),
    { name: 'InterviewStore' }
  )
);
