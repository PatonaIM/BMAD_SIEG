import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
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

      reset: () => set(initialState, false, 'reset'),
    }),
    { name: 'InterviewStore' }
  )
);
