# 5. State Management

## 5.1 Store Structure

\`\`\`
src/store/
├── index.ts                      # Store composition and exports
├── globalStore.ts                # Global app state
└── slices/                       # Store slices (optional pattern)
    ├── userSlice.ts
    └── notificationSlice.ts

src/features/{feature}/store/
├── {feature}Store.ts             # Feature-specific Zustand store
\`\`\`

## 5.2 Global Store (Zustand)

\`\`\`typescript
// src/store/globalStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'candidate' | 'recruiter' | 'admin';
}

interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  timestamp: number;
}

interface GlobalState {
  user: User | null;
  isAuthenticated: boolean;
  notifications: Notification[];
  
  setUser: (user: User | null) => void;
  logout: () => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useGlobalStore = create<GlobalState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        isAuthenticated: false,
        notifications: [],

        setUser: (user) =>
          set({ user, isAuthenticated: !!user }, false, 'setUser'),

        logout: () =>
          set({ user: null, isAuthenticated: false }, false, 'logout'),

        addNotification: (notification) =>
          set(
            (state) => ({
              notifications: [
                ...state.notifications,
                {
                  ...notification,
                  id: crypto.randomUUID(),
                  timestamp: Date.now(),
                },
              ],
            }),
            false,
            'addNotification'
          ),

        removeNotification: (id) =>
          set(
            (state) => ({
              notifications: state.notifications.filter((n) => n.id !== id),
            }),
            false,
            'removeNotification'
          ),

        clearNotifications: () =>
          set({ notifications: [] }, false, 'clearNotifications'),
      }),
      {
        name: 'teamified-global-store',
        partialize: (state) => ({ 
          user: state.user, 
          isAuthenticated: state.isAuthenticated 
        }),
      }
    ),
    { name: 'GlobalStore' }
  )
);

// Selectors for optimized re-renders
export const selectUser = (state: GlobalState) => state.user;
export const selectIsAuthenticated = (state: GlobalState) => state.isAuthenticated;
export const selectNotifications = (state: GlobalState) => state.notifications;
\`\`\`

## 5.3 Feature Store Example (Interview)

\`\`\`typescript
// src/features/interview/store/interviewStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export enum InterviewStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

interface Message {
  id: string;
  role: 'ai' | 'candidate';
  content: string;
  timestamp: number;
}

interface InterviewState {
  sessionId: string | null;
  status: InterviewStatus;
  currentQuestion: number;
  totalQuestions: number;
  messages: Message[];
  isRecording: boolean;
  isSpeaking: boolean;
  audioLevel: number;
  
  startInterview: (sessionId: string) => void;
  endInterview: () => void;
  pauseInterview: () => void;
  resumeInterview: () => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateProgress: (current: number, total: number) => void;
  setRecording: (isRecording: boolean) => void;
  setSpeaking: (isSpeaking: boolean) => void;
  setAudioLevel: (level: number) => void;
  reset: () => void;
}

const initialState = {
  sessionId: null,
  status: InterviewStatus.NOT_STARTED,
  currentQuestion: 0,
  totalQuestions: 0,
  messages: [],
  isRecording: false,
  isSpeaking: false,
  audioLevel: 0,
};

export const useInterviewStore = create<InterviewState>()(
  devtools(
    (set) => ({
      ...initialState,

      startInterview: (sessionId) =>
        set({ sessionId, status: InterviewStatus.IN_PROGRESS }, false, 'startInterview'),

      endInterview: () =>
        set({ status: InterviewStatus.COMPLETED }, false, 'endInterview'),

      pauseInterview: () =>
        set({ status: InterviewStatus.PAUSED }, false, 'pauseInterview'),

      resumeInterview: () =>
        set({ status: InterviewStatus.IN_PROGRESS }, false, 'resumeInterview'),

      addMessage: (message) =>
        set(
          (state) => ({
            messages: [
              ...state.messages,
              { ...message, id: crypto.randomUUID(), timestamp: Date.now() },
            ],
          }),
          false,
          'addMessage'
        ),

      updateProgress: (current, total) =>
        set({ currentQuestion: current, totalQuestions: total }, false, 'updateProgress'),

      setRecording: (isRecording) => set({ isRecording }, false, 'setRecording'),
      setSpeaking: (isSpeaking) => set({ isSpeaking }, false, 'setSpeaking'),
      setAudioLevel: (audioLevel) => set({ audioLevel }, false, 'setAudioLevel'),
      reset: () => set(initialState, false, 'reset'),
    }),
    { name: 'InterviewStore' }
  )
);
\`\`\`

## 5.4 Context API Example (Theme)

\`\`\`typescript
// src/theme/ThemeContext.tsx
import React, { createContext, useContext, useState, useCallback } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from './theme';

interface ThemeContextValue {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = useCallback(() => {
    setIsDarkMode((prev) => !prev);
  }, []);

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
      <MuiThemeProvider theme={teamifiedTheme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
\`\`\`

## 5.5 Usage Guidelines

**Use TanStack Query for:**
- All server state (API data fetching, caching, synchronization)
- Data that needs to be shared across components
- Background refetching and cache invalidation
- Optimistic updates for better UX
- Request deduplication
- Automatic retry logic

**Use Zustand for:**
- Complex client state with multiple actions (interview session state)
- UI state shared across multiple components
- State needing DevTools debugging
- State requiring persistence (localStorage)
- Feature-specific state (auth, UI preferences)

**Use Context API for:**
- Simple state (theme, locale, feature flags)
- State that doesn't change frequently
- Provider pattern for app/feature wrappers
- Minimal performance concerns

**Use Component State for:**
- UI-only state (modal visibility, form inputs)
- State used by single component
- Temporary state without persistence needs

**Clear Separation:**
- **Server State** (TanStack Query): Data from backend, caching, synchronization
- **Client State** (Zustand/Context): Application UI state, user preferences
- **Component State** (useState): Local component UI state

---
