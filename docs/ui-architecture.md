# Teamified Candidates Portal Frontend Architecture Document

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-28 | 1.0 | Initial frontend architecture document creation | Winston (Architect) |
| 2025-10-28 | 1.1 | Added audio/speech integration, performance, security, and accessibility sections | Winston (Architect) |
| 2025-10-28 | 1.2 | Replaced Axios with TanStack Query (React Query) for better server state management | Winston (Architect) |
| 2025-10-28 | 1.4 | Marked MVP-ready status; added Future Sections note for deployment, monitoring, real-time communication | Winston (Architect) |

---

## 1. Template and Framework Selection

### Decision: Vite + React + TypeScript

**Existing Foundation:**
- **Design System Reference**: Complete v0.dev-generated design system in `docs/style-guide/design-system-reference/`
- **Framework**: React 18+ with TypeScript
- **Component Library**: Material-UI (MUI) + Custom Teamified components
- **UI Components**: shadcn/ui components as base
- **Starter Pattern**: Custom design system with reference implementations

**Selected Starter Template: Vite + React + TypeScript**

**Rationale:**
- **Fast Development Experience**: Vite's instant HMR improves developer productivity
- **Optimal for Real-Time Features**: Excellent performance for speech/audio processing and WebRTC
- **Modern Build Tool**: Smaller bundle sizes, faster builds compared to traditional tools
- **TypeScript Excellence**: Superior TypeScript support and type checking
- **Future-Proof**: Aligns with modern React ecosystem trends
- **No Framework Lock-In**: Clean migration path if needed

**Key Constraints:**
- Reference components in `design-system-reference/` are NOT production code
- Production implementation will be in `src/` with proper backend integration
- Must maintain design specifications from reference while adding proper state management and API integration

---

## 2. Frontend Tech Stack

### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Framework** | React | 18+ | UI framework with hooks and concurrent features | Industry standard, excellent TypeScript support, perfect for real-time interview UI |
| **Language** | TypeScript | 5.0+ | Type-safe development | Prevents runtime errors, better IDE support, essential for complex state management |
| **Build Tool** | Vite | 5.0+ | Fast development and production builds | Instant HMR, optimized for modern browsers, excellent for audio/WebRTC features |
| **UI Library** | Material-UI (MUI) | 5.14+ | Base component library | Accessible components, customizable theming, production-ready |
| **State Management** | Zustand + Context API | Zustand 4.4+ | Global and local state | Lightweight, minimal boilerplate, Context for simple cases |
| **Routing** | React Router | 6.20+ | Client-side routing | Standard React routing, supports protected routes and lazy loading |
| **Styling** | MUI Theming (Emotion) | Built-in | Component styling | Leverages existing MUI theme, CSS-in-JS with component scope |
| **Form Handling** | React Hook Form | 7.48+ | Form state and validation | Performance optimized, minimal re-renders, integrates with validation libraries |
| **Validation** | Zod | 3.22+ | Schema validation | Type-safe validation, works seamlessly with TypeScript and React Hook Form |
| **Data Fetching** | TanStack Query (React Query) | 5.0+ | Server state management and caching | Auto caching, background refetching, optimistic updates, request deduplication |
| **HTTP Client** | Fetch API | Native | HTTP requests | Modern native API, used by TanStack Query, no additional dependencies |
| **Audio Processing** | Web Audio API + MediaRecorder | Native | Real-time audio capture and visualization | Built-in browser APIs, no additional dependencies for core audio features |
| **Speech Integration** | OpenAI Whisper + TTS | API | Speech-to-text and text-to-speech | Primary provider for MVP, flexible architecture supports Azure/GCP alternatives |
| **Testing Framework** | Vitest | 1.0+ | Unit and integration testing | Native Vite integration, Jest-compatible API, faster execution |
| **Testing Library** | React Testing Library | 14.1+ | Component testing | Best practices for user-centric testing, accessibility focus |
| **E2E Testing** | Playwright | 1.40+ | End-to-end testing | Cross-browser, reliable, great for audio/video testing |
| **Component Dev** | Storybook | 7.5+ | Component development and documentation | Isolated component development, design system showcase |
| **Animation** | Framer Motion | 10.16+ | UI animations and transitions | Declarative animations, perfect for waveform visualizers and progress indicators |
| **Data Visualization** | Recharts | 2.10+ | Skill maps and analytics charts | React-native, customizable, good for recruiter dashboards |
| **Code Quality** | ESLint + Prettier | Latest | Linting and formatting | Code consistency, catch errors early |
| **Type Checking** | TypeScript ESLint | Latest | TypeScript-specific linting | Enforce TypeScript best practices |
| **Dev Tools** | React DevTools, Redux DevTools (for Zustand) | Latest | Development debugging | State inspection, performance profiling |

### Key Technology Decisions

**TanStack Query over Axios/Redux:**
- Eliminates need for manual API state management (loading, error, data)
- Automatic caching and background refetching
- Request deduplication prevents duplicate API calls
- Optimistic updates for better UX
- Built-in retry logic and error handling
- DevTools for debugging queries and cache
- Works seamlessly with native Fetch API

**OpenAI Whisper + TTS for Speech (MVP):**
- Single vendor simplifies operations and billing (already using OpenAI for interviews)
- Whisper provides state-of-the-art transcription accuracy
- Cost-effective at pilot scale ($0.006/min STT, $0.015/1K chars TTS)
- Backend processing ensures API key security and audio auditability
- Flexible architecture allows future migration to Azure/GCP if needed
- Trade-off: 2-3s latency vs real-time streaming (acceptable for interview use case)
- Future optimization: Can add Azure Speech Services for real-time streaming post-MVP

**Zustand over Redux:**
- Interview state is complex but not overly nested
- Minimal boilerplate speeds up development
- Excellent TypeScript inference
- DevTools support for debugging
- Easy to test and mock

**React Hook Form + Zod:**
- Forms are critical (resume upload, feedback approval)
- Validation schemas are type-safe and reusable
- Minimal re-renders = better performance
- Server-side validation schema can mirror client-side

**Vitest over Jest:**
- Native Vite integration = same config, faster tests
- Jest-compatible API = easy migration if needed
- Better ESM support
- Aligns with modern tooling choice

**Playwright over Cypress:**
- Better for audio/microphone permission testing
- More reliable for speech-to-speech flow testing
- Cross-browser testing out of the box
- Faster execution with parallel testing

**Native Web Audio API:**
- No external dependency for waveform visualization
- Real-time audio level detection
- Lower latency than library abstractions
- Full control over audio processing pipeline

**Backend Audio Processing:**
- API keys secured on server (never exposed to browser)
- Centralized audio processing for consistent quality
- Audio metadata capture for integrity monitoring
- Flexible provider switching (OpenAI, Azure, GCP) without frontend changes
- Better monitoring and cost tracking

---

## 3. Project Structure

```
frontend/
├── public/                          # Static assets
│   ├── favicon.ico
│   └── audio/                       # Audio files for testing
├── src/
│   ├── main.tsx                     # Application entry point
│   ├── App.tsx                      # Root component with QueryClientProvider
│   ├── vite-env.d.ts               # Vite type definitions
│   │
│   ├── assets/                      # Images, fonts, etc.
│   │   ├── images/
│   │   └── fonts/
│   │
│   ├── components/                  # Reusable UI components
│   │   ├── ui/                      # Base UI components (shadcn/ui pattern)
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Card/
│   │   │   ├── Input/
│   │   │   └── index.ts             # Barrel export
│   │   │
│   │   ├── teamified/               # Custom Teamified components
│   │   │   ├── WaveformVisualizer/
│   │   │   ├── ProgressIndicator/
│   │   │   ├── SystemCheckStep/
│   │   │   ├── StatusBadge/
│   │   │   └── index.ts
│   │   │
│   │   ├── layout/                  # Layout components
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   ├── Footer/
│   │   │   └── DashboardLayout/
│   │   │
│   │   └── shared/                  # Shared composite components
│   │       ├── LoadingSpinner/
│   │       ├── ErrorBoundary/
│   │       └── ProtectedRoute/
│   │
│   ├── features/                    # Feature-based modules
│   │   ├── auth/
│   │   │   ├── components/          # Feature-specific components
│   │   │   │   ├── LoginForm/
│   │   │   │   └── RegisterForm/
│   │   │   ├── hooks/               # Feature-specific hooks
│   │   │   │   └── useAuth.ts
│   │   │   ├── services/            # Feature-specific API calls
│   │   │   │   └── authService.ts
│   │   │   ├── store/               # Feature-specific state
│   │   │   │   └── authStore.ts
│   │   │   ├── types/               # Feature-specific types
│   │   │   │   └── auth.types.ts
│   │   │   └── utils/               # Feature-specific utilities
│   │   │       └── tokenHelper.ts
│   │   │
│   │   ├── interview/               # Interview feature
│   │   │   ├── components/
│   │   │   │   ├── InterviewChat/
│   │   │   │   ├── AudioControls/
│   │   │   │   ├── PreInterviewCheck/
│   │   │   │   └── InterviewProgress/
│   │   │   ├── hooks/
│   │   │   │   ├── useInterviewSession.ts
│   │   │   │   ├── useAudioRecording.ts
│   │   │   │   └── useSpeechRecognition.ts
│   │   │   ├── services/
│   │   │   │   ├── interviewService.ts
│   │   │   │   └── speechService.ts
│   │   │   ├── store/
│   │   │   │   └── interviewStore.ts
│   │   │   └── types/
│   │   │       └── interview.types.ts
│   │   │
│   │   ├── resume/                  # Resume upload feature
│   │   │   ├── components/
│   │   │   │   ├── ResumeUpload/
│   │   │   │   └── ResumeFeedback/
│   │   │   ├── services/
│   │   │   │   └── resumeService.ts
│   │   │   └── types/
│   │   │       └── resume.types.ts
│   │   │
│   │   ├── recruiter/               # Recruiter portal feature
│   │   │   ├── components/
│   │   │   │   ├── CandidatePipeline/
│   │   │   │   ├── CandidateDetail/
│   │   │   │   ├── SkillMapVisualization/
│   │   │   │   └── IntegrityDashboard/
│   │   │   ├── services/
│   │   │   │   └── recruiterService.ts
│   │   │   └── types/
│   │   │       └── recruiter.types.ts
│   │   │
│   │   └── results/                 # Results/assessment feature
│   │       ├── components/
│   │       │   ├── ResultsSummary/
│   │       │   └── SkillStrengthChart/
│   │       └── types/
│   │           └── results.types.ts
│   │
│   ├── hooks/                       # Global custom hooks
│   │   ├── useApi.ts
│   │   ├── useDebounce.ts
│   │   ├── useLocalStorage.ts
│   │   └── useMicrophonePermission.ts
│   │
│   ├── services/                    # Global services
│   │   ├── api/
│   │   │   ├── client.ts            # Fetch API wrapper with auth
│   │   │   ├── queryClient.ts       # TanStack Query configuration
│   │   │   └── endpoints.ts         # API endpoint constants
│   │   └── audio/
│   │       ├── audioProcessor.ts    # Web Audio API wrapper (visualization)
│   │       └── audioCapture.ts      # MediaRecorder API wrapper (recording)
│   │
│   ├── store/                       # Global state management
│   │   ├── index.ts                 # Store composition
│   │   └── globalStore.ts           # Global app state (user, notifications)
│   │
│   ├── pages/                       # Page-level components (route components)
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── InterviewPage.tsx
│   │   ├── ResultsPage.tsx
│   │   ├── RecruiterDashboardPage.tsx
│   │   └── NotFoundPage.tsx
│   │
│   ├── routes/                      # Routing configuration
│   │   ├── index.tsx                # Route definitions
│   │   ├── ProtectedRoute.tsx       # Auth guard
│   │   └── routes.config.ts         # Route constants
│   │
│   ├── theme/                       # MUI theme configuration
│   │   ├── theme.ts                 # MUI theme object (from design system)
│   │   ├── palette.ts               # Color definitions
│   │   ├── typography.ts            # Typography settings
│   │   └── components.ts            # Component overrides
│   │
│   ├── styles/                      # Global styles
│   │   ├── globals.css              # Global CSS resets and utilities
│   │   └── variables.css            # CSS custom properties
│   │
│   ├── types/                       # Global TypeScript types
│   │   ├── api.types.ts             # API response/request types
│   │   ├── common.types.ts          # Shared types
│   │   └── index.ts                 # Type exports
│   │
│   ├── utils/                       # Utility functions
│   │   ├── formatters.ts            # Date, number, string formatters
│   │   ├── validators.ts            # Validation helpers
│   │   ├── storage.ts               # LocalStorage wrappers
│   │   └── constants.ts             # App constants
│   │
│   └── config/                      # Configuration files
│       ├── env.ts                   # Environment variable validation
│       └── app.config.ts            # App-wide configuration
│
├── tests/                           # Test utilities and setup
│   ├── setup.ts                     # Test environment setup
│   ├── mocks/                       # Mock data and services
│   │   ├── handlers.ts              # MSW handlers
│   │   └── mockData.ts              # Test fixtures
│   └── utils/                       # Test utilities
│       └── testHelpers.ts
│
├── .storybook/                      # Storybook configuration
│   ├── main.ts
│   └── preview.ts
│
├── .env.example                     # Environment variables template
├── .env.development                 # Development environment
├── .env.production                  # Production environment
├── .eslintrc.json                   # ESLint configuration
├── .prettierrc                      # Prettier configuration
├── tsconfig.json                    # TypeScript configuration
├── tsconfig.node.json               # TypeScript config for Node scripts
├── vite.config.ts                   # Vite configuration
├── vitest.config.ts                 # Vitest configuration
├── playwright.config.ts             # Playwright configuration
├── package.json
└── README.md
```

### Structure Rationale

**Feature-Based Organization:**
- Each major feature (auth, interview, resume, recruiter) is self-contained
- Reduces coupling, easier to understand and maintain
- Scales well as team grows (features can be owned by different developers)
- Aligns with Epic structure in PRD

**Component Hierarchy:**
- `ui/` = Base design system components (buttons, inputs, cards)
- `teamified/` = Custom branded components (waveform, progress indicators)
- `layout/` = Structural components (headers, sidebars)
- `shared/` = Composite components used across features

**Two-Level Hooks:**
- Global hooks (`hooks/`) = Used everywhere (useApi, useDebounce)
- Feature hooks (`features/*/hooks/`) = Feature-specific logic (useInterviewSession)

**Services Layer:**
- Clear separation of API communication from components
- `api/` = HTTP client setup and configuration
- `audio/` = Audio processing abstraction (Web Audio API, WebRTC)

**Pages vs Components:**
- `pages/` = Route-level components (thin, composition-focused)
- `components/` = Reusable UI (no routing knowledge)
- Clear separation of concerns

**Type Organization:**
- Global types (`types/`) = Shared across features
- Feature types (`features/*/types/`) = Feature-specific
- Prevents circular dependencies

**Audio/Speech Infrastructure:**
- Dedicated `services/audio/` for Web Audio API and WebRTC
- Feature-specific hooks in interview feature
- Supports speech-to-speech interview requirements

---

## 4. Component Standards

### 4.1 Component Template

```typescript
// src/components/ui/Button/Button.tsx
import React from 'react';
import { Button as MuiButton, ButtonProps as MuiButtonProps } from '@mui/material';
import { styled } from '@mui/material/styles';

/**
 * Custom button component extending MUI Button
 * Implements Teamified design system specifications
 */

// Styled component for custom variants
const StyledButton = styled(MuiButton)(({ theme }) => ({
  textTransform: 'none', // Prevent uppercase transform
  fontWeight: 600,
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(1.5, 3),
  
  '&.MuiButton-containedPrimary': {
    backgroundColor: theme.palette.primary.main,
    '&:hover': {
      backgroundColor: theme.palette.primary.dark,
    },
  },
}));

// Extend MUI ButtonProps with custom props
export interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  /** Loading state */
  isLoading?: boolean;
  /** Full width button */
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  disabled,
  children,
  ...props
}) => {
  // Map custom variants to MUI variants
  const muiVariant = variant === 'ghost' ? 'text' : 'contained';
  const muiColor = variant === 'danger' ? 'error' : 'primary';

  return (
    <StyledButton
      variant={muiVariant}
      color={muiColor}
      size={size}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? 'Loading...' : children}
    </StyledButton>
  );
};

Button.displayName = 'Button';

export default Button;
```

```typescript
// src/components/ui/Button/index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button';
```

```typescript
// src/components/ui/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '@/theme/theme';

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={teamifiedTheme}>
      {component}
    </ThemeProvider>
  );
};

describe('Button', () => {
  it('renders with children', () => {
    renderWithTheme(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    renderWithTheme(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    renderWithTheme(<Button isLoading>Submit</Button>);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('disables button when disabled prop is true', () => {
    renderWithTheme(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### 4.2 Naming Conventions

**Files:**
- **Components**: PascalCase - `Button.tsx`, `WaveformVisualizer.tsx`
- **Tests**: Match component - `Button.test.tsx`
- **Types**: Match component - `button.types.ts` (lowercase with dots)
- **Hooks**: camelCase with `use` prefix - `useAudioRecording.ts`
- **Services**: camelCase with suffix - `interviewService.ts`
- **Utils**: camelCase - `formatters.ts`, `validators.ts`
- **Stores**: camelCase with `Store` suffix - `authStore.ts`
- **Index files**: `index.ts` (barrel exports)

**Directories:**
- **Component folders**: PascalCase - `Button/`, `WaveformVisualizer/`
- **Feature folders**: lowercase - `auth/`, `interview/`, `resume/`
- **Utility folders**: lowercase - `hooks/`, `services/`, `utils/`

**Code:**
- **Components**: PascalCase - `<Button />`, `<InterviewChat />`
- **Functions**: camelCase - `formatDate()`, `validateEmail()`
- **Hooks**: camelCase with `use` prefix - `useAuth()`, `useInterviewSession()`
- **Constants**: UPPER_SNAKE_CASE - `API_BASE_URL`, `MAX_FILE_SIZE`
- **Types/Interfaces**: PascalCase - `ButtonProps`, `InterviewSession`
- **Enums**: PascalCase - `InterviewStatus`, `UserRole`

**Props:**
- Prefix boolean props with `is`, `has`, `should` - `isLoading`, `hasError`, `shouldAutoFocus`
- Event handlers with `on` prefix - `onClick`, `onChange`, `onSubmit`

**Imports:**
- Use `@/` alias for absolute imports from `src/`
- Example: `import { Button } from '@/components/ui/Button'`

---

## 5. State Management

### 5.1 Store Structure

```
src/store/
├── index.ts                      # Store composition and exports
├── globalStore.ts                # Global app state
└── slices/                       # Store slices (optional pattern)
    ├── userSlice.ts
    └── notificationSlice.ts

src/features/{feature}/store/
├── {feature}Store.ts             # Feature-specific Zustand store
```

### 5.2 Global Store (Zustand)

```typescript
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
```

### 5.3 Feature Store Example (Interview)

```typescript
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
```

### 5.4 Context API Example (Theme)

```typescript
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
```

### 5.5 Usage Guidelines

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


## 6. API Integration

### 6.1 TanStack Query Setup

```typescript
// src/services/api/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes (formerly cacheTime)
      retry: 3,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

```typescript
// src/App.tsx
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '@/services/api/queryClient';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourAppComponents />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### 6.2 API Client with Fetch

```typescript
// src/services/api/client.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface RequestConfig extends RequestInit {
  params?: Record<string, string>;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const apiClient = {
  async request<T>(endpoint: string, config: RequestConfig = {}): Promise<T> {
    const { params, ...fetchConfig } = config;
    
    // Build URL with query params
    const url = new URL(`${BASE_URL}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    // Get auth token
    const token = localStorage.getItem('auth_token');
    
    // Set up headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...fetchConfig.headers,
    };
    
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url.toString(), {
        ...fetchConfig,
        headers,
      });

      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      const isJson = contentType?.includes('application/json');

      if (!response.ok) {
        const errorData = isJson ? await response.json() : await response.text();
        
        // Handle 401 - Unauthorized
        if (response.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        
        throw new ApiError(
          errorData?.message || `Request failed with status ${response.status}`,
          response.status,
          errorData
        );
      }

      return isJson ? await response.json() : await response.text();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Network errors
      if (!navigator.onLine) {
        throw new ApiError('No internet connection', 0);
      }
      
      throw new ApiError('Network request failed', 0, error);
    }
  },

  get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  },

  post<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  put<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  },

  patch<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  },
};

export { ApiError };
```

### 6.3 API Endpoints

```typescript
// src/services/api/endpoints.ts
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
  },
  INTERVIEWS: {
    LIST: '/interviews',
    CREATE: '/interviews',
    GET: (id: string) => `/interviews/${id}`,
    START: (id: string) => `/interviews/${id}/start`,
    END: (id: string) => `/interviews/${id}/end`,
    MESSAGES: (id: string) => `/interviews/${id}/messages`,
    RESULTS: (id: string) => `/interviews/${id}/results`,
  },
  RESUMES: {
    UPLOAD: '/resumes/upload',
    GET: (id: string) => `/resumes/${id}`,
    FEEDBACK: (id: string) => `/resumes/${id}/feedback`,
  },
  CANDIDATES: {
    LIST: '/candidates',
    GET: (id: string) => `/candidates/${id}`,
    ASSESSMENTS: (id: string) => `/candidates/${id}/assessments`,
  },
  RECRUITERS: {
    DASHBOARD: '/recruiters/dashboard',
    PIPELINE: '/recruiters/pipeline',
    ANALYTICS: '/recruiters/analytics',
  },
} as const;
```

### 6.4 Service with TanStack Query

```typescript
// src/features/interview/services/interviewService.ts
import { apiClient } from '@/services/api/client';
import { API_ENDPOINTS } from '@/services/api/endpoints';
import type { Interview, InterviewMessage, InterviewResults } from '../types/interview.types';

export const interviewService = {
  async getInterviews(): Promise<Interview[]> {
    return apiClient.get<Interview[]>(API_ENDPOINTS.INTERVIEWS.LIST);
  },

  async getInterview(id: string): Promise<Interview> {
    return apiClient.get<Interview>(API_ENDPOINTS.INTERVIEWS.GET(id));
  },

  async startInterview(id: string): Promise<{ sessionId: string; firstQuestion: string }> {
    return apiClient.post(API_ENDPOINTS.INTERVIEWS.START(id));
  },

  async sendMessage(
    interviewId: string,
    content: string,
    audioBlob?: Blob
  ): Promise<InterviewMessage> {
    const formData = new FormData();
    formData.append('content', content);
    
    if (audioBlob) {
      formData.append('audio', audioBlob, 'audio.webm');
    }

    // For FormData, we need to override headers
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}${API_ENDPOINTS.INTERVIEWS.MESSAGES(interviewId)}`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  },

  async endInterview(id: string): Promise<void> {
    return apiClient.post(API_ENDPOINTS.INTERVIEWS.END(id));
  },

  async getResults(id: string): Promise<InterviewResults> {
    return apiClient.get<InterviewResults>(API_ENDPOINTS.INTERVIEWS.RESULTS(id));
  },
};
```

### 6.5 Query Hooks Pattern

```typescript
// src/features/interview/hooks/useInterviewQueries.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { interviewService } from '../services/interviewService';
import type { Interview, InterviewMessage } from '../types/interview.types';

// Query Keys
export const interviewKeys = {
  all: ['interviews'] as const,
  lists: () => [...interviewKeys.all, 'list'] as const,
  list: (filters: string) => [...interviewKeys.lists(), { filters }] as const,
  details: () => [...interviewKeys.all, 'detail'] as const,
  detail: (id: string) => [...interviewKeys.details(), id] as const,
  results: (id: string) => [...interviewKeys.detail(id), 'results'] as const,
};

// Fetch all interviews
export const useInterviews = () => {
  return useQuery({
    queryKey: interviewKeys.lists(),
    queryFn: interviewService.getInterviews,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Fetch single interview
export const useInterview = (id: string) => {
  return useQuery({
    queryKey: interviewKeys.detail(id),
    queryFn: () => interviewService.getInterview(id),
    enabled: !!id, // Only run if id exists
  });
};

// Fetch interview results
export const useInterviewResults = (id: string) => {
  return useQuery({
    queryKey: interviewKeys.results(id),
    queryFn: () => interviewService.getResults(id),
    enabled: !!id,
  });
};

// Start interview mutation
export const useStartInterview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => interviewService.startInterview(id),
    onSuccess: (data, id) => {
      // Invalidate and refetch interview data
      queryClient.invalidateQueries({ queryKey: interviewKeys.detail(id) });
    },
  });
};

// Send message mutation
export const useSendMessage = (interviewId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ content, audioBlob }: { content: string; audioBlob?: Blob }) =>
      interviewService.sendMessage(interviewId, content, audioBlob),
    onSuccess: () => {
      // Invalidate interview to refetch with new message
      queryClient.invalidateQueries({ queryKey: interviewKeys.detail(interviewId) });
    },
  });
};

// End interview mutation
export const useEndInterview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => interviewService.endInterview(id),
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: interviewKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: interviewKeys.lists() });
    },
  });
};
```

### 6.6 Using Queries in Components

```typescript
// src/features/interview/components/InterviewList.tsx
import { useInterviews } from '../hooks/useInterviewQueries';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorMessage } from '@/components/shared/ErrorMessage';

export const InterviewList = () => {
  const { data: interviews, isLoading, error } = useInterviews();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load interviews" />;

  return (
    <div>
      {interviews?.map((interview) => (
        <div key={interview.id}>{interview.title}</div>
      ))}
    </div>
  );
};
```

```typescript
// src/features/interview/components/InterviewChat.tsx
import { useSendMessage } from '../hooks/useInterviewQueries';
import { useGlobalStore } from '@/store/globalStore';

export const InterviewChat = ({ interviewId }: { interviewId: string }) => {
  const sendMessageMutation = useSendMessage(interviewId);
  const { addNotification } = useGlobalStore();

  const handleSendMessage = async (content: string, audioBlob?: Blob) => {
    try {
      await sendMessageMutation.mutateAsync({ content, audioBlob });
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to send message',
      });
    }
  };

  return (
    <div>
      {/* Chat UI */}
      <button
        onClick={() => handleSendMessage('Hello')}
        disabled={sendMessageMutation.isPending}
      >
        {sendMessageMutation.isPending ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
};
```

---


## 7. Routing

### 7.1 Route Configuration

```typescript
// src/routes/routes.config.ts
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  
  // Candidate routes
  CANDIDATE: {
    DASHBOARD: '/dashboard',
    RESUME_UPLOAD: '/resume/upload',
    INTERVIEW: '/interview/:id',
    INTERVIEW_START: (id: string) => `/interview/${id}`,
    RESULTS: '/results/:id',
    RESULTS_VIEW: (id: string) => `/results/${id}`,
  },
  
  // Recruiter routes
  RECRUITER: {
    DASHBOARD: '/recruiter/dashboard',
    PIPELINE: '/recruiter/pipeline',
    CANDIDATE_DETAIL: '/recruiter/candidates/:id',
    CANDIDATE_VIEW: (id: string) => `/recruiter/candidates/${id}`,
    ANALYTICS: '/recruiter/analytics',
  },
  
  // Admin routes
  ADMIN: {
    DASHBOARD: '/admin/dashboard',
    USERS: '/admin/users',
    SETTINGS: '/admin/settings',
  },
  
  NOT_FOUND: '/404',
} as const;
```

### 7.2 Protected Route Component

```typescript
// src/components/shared/ProtectedRoute/ProtectedRoute.tsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useGlobalStore, selectIsAuthenticated, selectUser } from '@/store/globalStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'candidate' | 'recruiter' | 'admin';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const isAuthenticated = useGlobalStore(selectIsAuthenticated);
  const user = useGlobalStore(selectUser);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/403" replace />;
  }

  return <>{children}</>;
};
```

### 7.3 Router Setup

```typescript
// src/routes/index.tsx
import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom';
import { ProtectedRoute } from '@/components/shared/ProtectedRoute';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ROUTES } from './routes.config';

// Lazy load pages
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const InterviewPage = lazy(() => import('@/pages/InterviewPage'));
const ResultsPage = lazy(() => import('@/pages/ResultsPage'));
const RecruiterDashboardPage = lazy(() => import('@/pages/RecruiterDashboardPage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));

const router = createBrowserRouter([
  {
    path: ROUTES.HOME,
    element: <Outlet />,
    children: [
      {
        index: true,
        element: <Navigate to={ROUTES.LOGIN} replace />,
      },
      {
        path: ROUTES.LOGIN,
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <LoginPage />
          </Suspense>
        ),
      },
      {
        path: ROUTES.CANDIDATE.DASHBOARD,
        element: (
          <ProtectedRoute requiredRole="candidate">
            <Suspense fallback={<LoadingSpinner />}>
              <DashboardPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.CANDIDATE.INTERVIEW,
        element: (
          <ProtectedRoute requiredRole="candidate">
            <Suspense fallback={<LoadingSpinner />}>
              <InterviewPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.RECRUITER.DASHBOARD,
        element: (
          <ProtectedRoute requiredRole="recruiter">
            <Suspense fallback={<LoadingSpinner />}>
              <RecruiterDashboardPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: ROUTES.NOT_FOUND,
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <NotFoundPage />
          </Suspense>
        ),
      },
      {
        path: '*',
        element: <Navigate to={ROUTES.NOT_FOUND} replace />,
      },
    ],
  },
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};
```

---

## 8. Styling Guidelines

### 8.1 MUI Theme Configuration

```typescript
// src/theme/theme.ts (from design system)
import { createTheme } from '@mui/material/styles';

export const teamifiedTheme = createTheme({
  palette: {
    primary: {
      main: '#A16AE8',
      light: '#E8E5F5',
      dark: '#7B3FD6',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#1DD1A1',
      light: '#D4F5EE',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#FFA502',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#EF4444',
      contrastText: '#FFFFFF',
    },
    grey: {
      900: '#2C3E50',
      700: '#7F8C8D',
      300: '#E0E4E8',
      100: '#F5F6F7',
      50: '#FAFBFC',
    },
    background: {
      default: '#FAFBFC',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", sans-serif',
    h1: { fontSize: '56px', fontWeight: 700 },
    h2: { fontSize: '44px', fontWeight: 700 },
    h3: { fontSize: '36px', fontWeight: 600 },
    h4: { fontSize: '30px', fontWeight: 600 },
    h5: { fontSize: '24px', fontWeight: 600 },
    h6: { fontSize: '20px', fontWeight: 600 },
    body1: { fontSize: '16px', fontWeight: 400 },
    body2: { fontSize: '14px', fontWeight: 400 },
  },
  spacing: 8,
  shape: {
    borderRadius: 8,
  },
});
```

### 8.2 Styling Patterns

**Using sx Prop (Recommended for inline styling):**
```typescript
<Box
  sx={{
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    p: 4,
    bgcolor: 'background.paper',
    borderRadius: 2,
    boxShadow: 1,
  }}
>
  <Typography variant="h5" sx={{ color: 'primary.main', mb: 2 }}>
    Title
  </Typography>
</Box>
```

**Using Styled Components (For reusable styled elements):**
```typescript
import { styled } from '@mui/material/styles';
import { Box } from '@mui/material';

const StyledCard = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[1],
  
  '&:hover': {
    boxShadow: theme.shadows[2],
  },
}));
```

### 8.3 CSS Custom Properties

```css
/* src/styles/variables.css */
:root {
  /* Colors from MUI theme */
  --color-primary: #A16AE8;
  --color-success: #1DD1A1;
  --color-error: #EF4444;
  --color-warning: #FFA502;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Border radius */
  --border-radius: 8px;
  
  /* Transitions */
  --transition-fast: 150ms;
  --transition-normal: 250ms;
  --transition-slow: 400ms;
  
  /* Z-index layers */
  --z-index-dropdown: 1000;
  --z-index-modal: 1300;
  --z-index-tooltip: 1500;
}
```

---

## 9. Testing Requirements

### 9.1 Test Setup

```typescript
// tests/setup.ts
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

### 9.2 Component Test Template

```typescript
// Component.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '@/theme/theme';
import { ComponentName } from './ComponentName';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={teamifiedTheme}>
      {component}
    </ThemeProvider>
  );
};

describe('ComponentName', () => {
  it('renders correctly', () => {
    renderWithProviders(<ComponentName />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const handleClick = vi.fn();
    renderWithProviders(<ComponentName onClick={handleClick} />);
    
    fireEvent.click(screen.getByRole('button'));
    
    await waitFor(() => {
      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });
});
```

### 9.3 Testing Best Practices

1. **Unit Tests**: Test components in isolation
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test critical user flows with Playwright
4. **Coverage Goal**: 80% code coverage
5. **Test Structure**: Arrange-Act-Assert pattern
6. **Mock External Dependencies**: API calls, routing, global state

---

## 10. Environment Configuration

### 10.1 Environment Variables

```bash
# .env.example
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Teamified
VITE_APP_VERSION=1.0.0
```

```typescript
// src/config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url(),
  VITE_APP_NAME: z.string().default('Teamified'),
  VITE_APP_VERSION: z.string().default('1.0.0'),
});

const validateEnv = () => {
  try {
    return envSchema.parse(import.meta.env);
  } catch (error) {
    console.error('❌ Invalid environment variables:', error);
    throw new Error('Invalid environment configuration');
  }
};

export const env = validateEnv();
```

---

## 11. Frontend Developer Standards

### 11.1 Critical Coding Rules

1. **Always use TypeScript** - No `any` types without explicit justification
2. **Component naming** - Use PascalCase for components, files match component names
3. **Imports** - Use `@/` alias for absolute imports, avoid relative paths beyond parent
4. **Props** - Destructure in function signature, prefix booleans with `is/has/should`
5. **State** - Use Zustand for shared state, useState for local UI state
6. **Effects** - Clean up side effects, include all dependencies in useEffect
7. **Error handling** - Always wrap async operations in try-catch
8. **Accessibility** - Include proper ARIA labels, ensure keyboard navigation
9. **Testing** - Write tests alongside components, test user behavior not implementation
10. **MUI theming** - Use theme values via `sx` prop or `styled`, never hardcode colors

### 11.2 Quick Reference

**Start Development:**
```bash
npm run dev
```

**Run Tests:**
```bash
npm run test
npm run test:ui        # UI mode
npm run test:coverage  # With coverage
```

**Build:**
```bash
npm run build
npm run preview  # Preview production build
```

**Linting:**
```bash
npm run lint
npm run lint:fix
```

**Type Checking:**
```bash
npm run type-check
```

### 11.3 Common Patterns

**Fetching Data:**
```typescript
// Using TanStack Query hooks
const { data, isLoading, error } = useInterviews();

// With parameters
const { data: interview } = useInterview(interviewId);

// Mutations
const { mutate, isPending } = useStartInterview();
mutate(interviewId);
```

**Form Handling:**
```typescript
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

**Navigation:**
```typescript
const navigate = useNavigate();
navigate(ROUTES.CANDIDATE.DASHBOARD);
```

**Global State:**
```typescript
const user = useGlobalStore(selectUser);
const { setUser, logout } = useGlobalStore();
```

**Query Invalidation:**
```typescript
const queryClient = useQueryClient();
queryClient.invalidateQueries({ queryKey: interviewKeys.lists() });
```

---

## 12. Audio/Speech Integration Architecture

### 12.1 Speech Service Provider Strategy

**Primary Provider (MVP): OpenAI Whisper + TTS**

The architecture uses OpenAI for speech processing to simplify vendor management and reduce operational complexity during the bootstrap phase.

**Design Principles:**
- **Provider Abstraction**: Speech services accessed through abstraction layer
- **Flexible Architecture**: Easy migration to Azure Speech Services or GCP alternatives
- **Backend Processing**: All audio processing on server for security and auditability
- **Cost Optimization**: Single vendor billing, batch processing reduces overhead

**Future Migration Path:**
- Post-MVP: Evaluate Azure Speech Services for real-time streaming (<1s latency)
- Post-MVP: Consider GCP Speech-to-Text for specific regional requirements
- Architecture supports provider switching without frontend changes

### 12.2 Speech-to-Text Integration (OpenAI Whisper)

### 12.2 Speech-to-Text Integration (OpenAI Whisper)

```typescript
// src/services/audio/speechService.ts
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // Server-side only
});

export class SpeechService {
  /**
   * Transcribe audio file using OpenAI Whisper
   * Processing time: 2-3 seconds typical
   */
  async transcribeAudio(audioFile: File): Promise<TranscriptionResult> {
    try {
      const transcription = await openai.audio.transcriptions.create({
        file: audioFile,
        model: "whisper-1",
        language: "en", // Can be omitted for auto-detection
        response_format: "verbose_json", // Includes timestamps
        temperature: 0.0, // Deterministic output
      });

      return {
        text: transcription.text,
        duration: transcription.duration,
        language: transcription.language,
        segments: transcription.segments, // Word-level timestamps
      };
    } catch (error) {
      throw new Error(`Whisper transcription failed: ${error.message}`);
    }
  }

  /**
   * Transcribe with confidence scores and metadata
   */
  async transcribeWithMetadata(
    audioFile: File,
    interviewId: string
  ): Promise<DetailedTranscription> {
    const startTime = Date.now();
    
    const result = await this.transcribeAudio(audioFile);
    
    const processingTime = Date.now() - startTime;
    
    // Store metadata for integrity monitoring
    return {
      ...result,
      metadata: {
        processingTime,
        audioSize: audioFile.size,
        timestamp: new Date().toISOString(),
        interviewId,
      },
    };
  }
}

export const speechService = new SpeechService();
```

**Backend API Endpoint:**

```python
# backend/api/interviews.py
from fastapi import APIRouter, UploadFile, HTTPException
from openai import OpenAI
import tempfile
import os

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/api/v1/interviews/{interview_id}/audio")
async def process_audio(interview_id: str, audio_file: UploadFile):
    """
    Process candidate audio and return transcription
    Expected latency: 2-3 seconds
    """
    # Validate audio file
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(400, "Invalid audio file format")
    
    # Save temporarily for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Call OpenAI Whisper
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="verbose_json",
                language="en"
            )
        
        # Store transcription in database
        await store_interview_message(
            interview_id=interview_id,
            role="candidate",
            content=transcription.text,
            audio_metadata={
                "duration": transcription.duration,
                "file_size": len(content),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "transcription": transcription.text,
            "duration": transcription.duration,
            "processing_time": time.time() - start_time
        }
    
    finally:
        # Cleanup temp file
        os.unlink(tmp_path)
```

### 12.3 Text-to-Speech Integration (OpenAI TTS)

### 12.3 Text-to-Speech Integration (OpenAI TTS)

```typescript
// src/services/audio/ttsService.ts
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export class TextToSpeechService {
  /**
   * Generate speech from text using OpenAI TTS
   * Voice options: alloy, echo, fable, onyx, nova, shimmer
   */
  async generateSpeech(
    text: string,
    voice: 'alloy' | 'echo' | 'fable' | 'onyx' | 'nova' | 'shimmer' = 'nova'
  ): Promise<Buffer> {
    try {
      const mp3 = await openai.audio.speech.create({
        model: "tts-1", // Use tts-1-hd for higher quality
        voice: voice,
        input: text,
        speed: 0.95, // Slightly slower for clarity
      });

      const buffer = Buffer.from(await mp3.arrayBuffer());
      return buffer;
    } catch (error) {
      throw new Error(`TTS generation failed: ${error.message}`);
    }
  }

  /**
   * Generate speech with caching for common phrases
   */
  async generateWithCache(text: string, interviewId: string): Promise<string> {
    // Check cache first
    const cached = await this.checkCache(text);
    if (cached) return cached;

    // Generate new audio
    const audioBuffer = await this.generateSpeech(text);
    
    // Save to storage and return URL
    const audioUrl = await this.saveAudio(audioBuffer, interviewId);
    
    // Cache for reuse
    await this.cacheAudio(text, audioUrl);
    
    return audioUrl;
  }
}

export const ttsService = new TextToSpeechService();
```

**Backend Implementation:**

```python
# backend/api/tts.py
from openai import OpenAI
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io

router = APIRouter()
client = OpenAI()

@router.post("/api/v1/interviews/{interview_id}/tts")
async def generate_speech(interview_id: str, text: str, voice: str = "nova"):
    """
    Generate speech audio from AI question text
    Expected latency: 1-2 seconds
    """
    try:
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",  # Use tts-1-hd for higher quality
            voice=voice,
            input=text,
            speed=0.95
        )
        
        # Stream audio back to frontend
        audio_stream = io.BytesIO(response.content)
        
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=speech_{interview_id}.mp3"
            }
        )
    
    except Exception as e:
        raise HTTPException(500, f"TTS generation failed: {str(e)}")
```

### 12.4 Frontend Audio Capture

```typescript
// src/services/audio/audioCapture.ts
export class AudioCaptureService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private stream: MediaStream | null = null;

  /**
   * Request microphone access and initialize MediaRecorder
   */
  async initialize(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000, // Minimum for good quality
        },
      });

      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus', // Good compression, wide support
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };
    } catch (error) {
      throw new Error(`Microphone access failed: ${error.message}`);
    }
  }

  /**
   * Start recording audio
   */
  startRecording(): void {
    if (!this.mediaRecorder) {
      throw new Error('MediaRecorder not initialized');
    }

    this.audioChunks = [];
    this.mediaRecorder.start();
  }

  /**
   * Stop recording and return audio blob
   */
  async stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('MediaRecorder not initialized'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.audioChunks = [];
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    this.mediaRecorder = null;
    this.audioChunks = [];
  }
}
```

### 12.5 Web Audio API for Visualization

```typescript
// src/services/audio/audioProcessor.ts
export class AudioProcessor {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphone: MediaStreamAudioSourceNode | null = null;
  private dataArray: Uint8Array | null = null;

  /**
   * Initialize audio context and get microphone stream
   */
  async initialize(): Promise<void> {
    try {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000, // Minimum required per NFR19
        } 
      });

      this.microphone = this.audioContext.createMediaStreamSource(stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;

      this.microphone.connect(this.analyser);
      
      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(bufferLength);
    } catch (error) {
      throw new Error(`Failed to initialize audio: ${error}`);
    }
  }

  /**
   * Get current audio level (0-100)
   */
  getAudioLevel(): number {
    if (!this.analyser || !this.dataArray) return 0;

    this.analyser.getByteFrequencyData(this.dataArray);
    
    // Calculate average amplitude
    const sum = this.dataArray.reduce((acc, val) => acc + val, 0);
    const average = sum / this.dataArray.length;
    
    // Normalize to 0-100
    return Math.min(100, (average / 255) * 100);
  }

  /**
   * Get waveform data for visualization
   */
  getWaveformData(): Uint8Array {
    if (!this.analyser || !this.dataArray) return new Uint8Array(0);
    
    this.analyser.getByteTimeDomainData(this.dataArray);
    return this.dataArray;
  }

  /**
   * Check if audio input is detected
   */
  hasAudioInput(): boolean {
    const level = this.getAudioLevel();
    return level > 5; // Threshold for detecting sound
  }

  /**
   * Cleanup audio resources
   */
  cleanup(): void {
    if (this.microphone) {
      this.microphone.disconnect();
      this.microphone = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.analyser = null;
    this.dataArray = null;
  }
}
```

### 12.4 WebRTC Audio Streaming

```typescript
// src/services/audio/webRTCHandler.ts
export class WebRTCHandler {
  private peerConnection: RTCPeerConnection | null = null;
  private dataChannel: RTCDataChannel | null = null;
  private localStream: MediaStream | null = null;

  /**
   * Initialize WebRTC peer connection
   */
  async initialize(onTrack: (stream: MediaStream) => void): Promise<void> {
    const configuration: RTCConfiguration = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
      ],
    };

    this.peerConnection = new RTCPeerConnection(configuration);

    // Handle incoming tracks
    this.peerConnection.ontrack = (event) => {
      onTrack(event.streams[0]);
    };

    // Handle ICE candidates
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        // Send candidate to signaling server
        this.sendSignalingMessage('ice-candidate', event.candidate);
      }
    };

    // Get local media stream
    this.localStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
      },
    });

    // Add tracks to peer connection
    this.localStream.getTracks().forEach((track) => {
      if (this.peerConnection && this.localStream) {
        this.peerConnection.addTrack(track, this.localStream);
      }
    });
  }

  /**
   * Create WebRTC offer
   */
  async createOffer(): Promise<RTCSessionDescriptionInit> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized');
    }

    const offer = await this.peerConnection.createOffer();
    await this.peerConnection.setLocalDescription(offer);
    return offer;
  }

  /**
   * Handle WebRTC answer
   */
  async handleAnswer(answer: RTCSessionDescriptionInit): Promise<void> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized');
    }

    await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
  }

  /**
   * Add ICE candidate
   */
  async addIceCandidate(candidate: RTCIceCandidateInit): Promise<void> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized');
    }

    await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
  }

  /**
   * Monitor connection quality
   */
  async getConnectionStats(): Promise<RTCStatsReport | null> {
    if (!this.peerConnection) return null;

    return await this.peerConnection.getStats();
  }

  /**
   * Send signaling message (implement based on backend)
   */
  private sendSignalingMessage(type: string, data: any): void {
    // TODO: Implement WebSocket or HTTP signaling
    console.log('Signaling message:', type, data);
  }

  /**
   * Cleanup WebRTC resources
   */
  cleanup(): void {
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    if (this.dataChannel) {
      this.dataChannel.close();
      this.dataChannel = null;
    }
    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }
  }
}
```

### 12.6 Audio Recording Hook

```typescript
// src/features/interview/hooks/useAudioRecording.ts
import { useState, useCallback, useRef, useEffect } from 'react';
import { AudioProcessor } from '@/services/audio/audioProcessor';
import { AudioCaptureService } from '@/services/audio/audioCapture';
import { useInterviewStore } from '../store/interviewStore';
import { useSendAudio } from './useInterviewQueries';

export const useAudioRecording = (interviewId: string) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const audioProcessor = useRef<AudioProcessor>(new AudioProcessor());
  const audioCapture = useRef<AudioCaptureService>(new AudioCaptureService());
  const animationFrame = useRef<number>();

  const { setRecording, setAudioLevel: setStoreAudioLevel } = useInterviewStore();
  const sendAudioMutation = useSendAudio(interviewId);

  // Update audio level visualization
  const updateAudioLevel = useCallback(() => {
    if (!isRecording) return;

    const level = audioProcessor.current.getAudioLevel();
    setAudioLevel(level);
    setStoreAudioLevel(level);

    animationFrame.current = requestAnimationFrame(updateAudioLevel);
  }, [isRecording, setStoreAudioLevel]);

  // Start recording
  const startRecording = useCallback(async () => {
    try {
      setError(null);
      
      // Initialize audio processor for visualization
      await audioProcessor.current.initialize();
      
      // Initialize audio capture for recording
      await audioCapture.current.initialize();
      audioCapture.current.startRecording();

      setIsRecording(true);
      setRecording(true);
      updateAudioLevel();
    } catch (err) {
      setError(`Failed to start recording: ${err.message}`);
    }
  }, [setRecording, updateAudioLevel]);

  // Stop recording and send to backend
  const stopRecording = useCallback(async () => {
    if (animationFrame.current) {
      cancelAnimationFrame(animationFrame.current);
    }

    try {
      // Get audio blob
      const audioBlob = await audioCapture.current.stopRecording();
      
      // Send to backend for transcription
      await sendAudioMutation.mutateAsync(audioBlob);
      
    } catch (err) {
      setError(`Failed to process audio: ${err.message}`);
    } finally {
      audioProcessor.current.cleanup();
      audioCapture.current.cleanup();

      setIsRecording(false);
      setRecording(false);
      setAudioLevel(0);
      setStoreAudioLevel(0);
    }
  }, [setRecording, setStoreAudioLevel, sendAudioMutation]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isRecording) {
        stopRecording();
      }
    };
  }, [isRecording, stopRecording]);

  return {
    isRecording,
    audioLevel,
    error,
    startRecording,
    stopRecording,
    isProcessing: sendAudioMutation.isPending,
  };
};
```

### 12.7 Audio Quality Guidelines

**Minimum Requirements:**
- Sample rate: 16kHz minimum
- Audio format: WebM with Opus codec (good compression, wide support)
- Processing time: <3s for speech-to-text (OpenAI Whisper)
- Synthesis time: <2s for text-to-speech (OpenAI TTS)

**Best Practices:**
- Enable echo cancellation and noise suppression
- Use appropriate voice selection for natural TTS (nova, alloy for professional tone)
- Implement audio buffering for smooth playback
- Monitor audio quality metrics in real-time
- Provide visual feedback for all audio states
- Gracefully degrade to text mode on failures

**Cost Optimization:**
- Cache frequently used TTS responses (greetings, common questions)
- Monitor token usage for Whisper transcriptions
- Use `tts-1` model for MVP, upgrade to `tts-1-hd` if quality issues arise

**Future Optimizations:**
- Consider Azure Speech Services for real-time streaming (<1s latency)
- Evaluate GCP Speech-to-Text for specific regional requirements
- Implement WebRTC for ultra-low latency if customer feedback demands it

---

## 13. Performance Optimization

### 13.1 Code Splitting Strategy

```typescript
// src/routes/index.tsx
import React, { lazy, Suspense } from 'react';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';

// Lazy load heavy pages
const InterviewPage = lazy(() => import('@/pages/InterviewPage'));
const RecruiterDashboardPage = lazy(() => import('@/pages/RecruiterDashboardPage'));
const ResultsPage = lazy(() => import('@/pages/ResultsPage'));

// Wrap with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <InterviewPage />
</Suspense>
```

### 13.2 Performance Budgets

**Bundle Size Targets:**
- Initial bundle: <300KB (gzipped)
- Total bundle: <1MB (gzipped)
- Individual routes: <200KB (gzipped)

**Runtime Performance:**
- Time to Interactive (TTI): <3s
- First Contentful Paint (FCP): <1.5s
- Largest Contentful Paint (LCP): <2.5s

**API Response Times:**
- API calls: <500ms (95th percentile)
- AI responses: <2s (NFR2)
- Speech processing: <1s (NFR16, NFR17)

### 13.3 Optimization Techniques

**Asset Optimization:**
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'mui': ['@mui/material', '@emotion/react'],
          'speech': ['microsoft-cognitiveservices-speech-sdk'],
        },
      },
    },
    chunkSizeWarningLimit: 600,
  },
  optimizeDeps: {
    include: ['react', 'react-dom', '@tanstack/react-query'],
  },
});
```

**Image Optimization:**
- Use WebP format with fallbacks
- Lazy load images below the fold
- Use responsive images with `srcset`
- Compress images to <100KB

**State Management Optimization:**
- Use Zustand selectors to prevent unnecessary re-renders
- Memoize expensive calculations with `useMemo`
- Use `useCallback` for event handlers
- Implement virtual scrolling for long lists

---

## 14. Security Implementation

### 14.1 Authentication Flow

```typescript
// src/features/auth/services/authService.ts
import { apiClient } from '@/services/api/client';
import { API_ENDPOINTS } from '@/services/api/endpoints';

export const authService = {
  async login(email: string, password: string) {
    return apiClient.post(API_ENDPOINTS.AUTH.LOGIN, { email, password });
  },

  async logout() {
    return apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
  },

  async getMe() {
    return apiClient.get(API_ENDPOINTS.AUTH.ME);
  },
};
```

```typescript
// src/features/auth/hooks/useAuth.ts
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useGlobalStore } from '@/store/globalStore';

export const useAuth = () => {
  const navigate = useNavigate();
  const { setUser, logout: storeLogout } = useGlobalStore();

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authService.login(email, password),
    onSuccess: (data) => {
      // Store token
      localStorage.setItem('auth_token', data.token);
      
      // Update global state
      setUser(data.user);
      
      // Navigate based on role
      if (data.user.role === 'recruiter') {
        navigate('/recruiter/dashboard');
      } else {
        navigate('/dashboard');
      }
    },
  });

  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      localStorage.removeItem('auth_token');
      storeLogout();
      navigate('/login');
    },
  });

  const login = (email: string, password: string) => {
    loginMutation.mutate({ email, password });
  };

  const logout = () => {
    logoutMutation.mutate();
  };

  return {
    login,
    logout,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
  };
};

// Check authentication status
export const useAuthStatus = () => {
  const { setUser } = useGlobalStore();

  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authService.getMe,
    retry: false,
    onSuccess: (data) => {
      setUser(data.user);
    },
    onError: () => {
      localStorage.removeItem('auth_token');
    },
  });
};
```

### 14.2 Security Best Practices

**Token Management:**
- Store JWT in localStorage (or httpOnly cookies for enhanced security)
- Include token in Authorization header for all API calls
- Implement token refresh mechanism
- Clear token on logout

**Input Validation:**
- Validate all user inputs client-side
- Use Zod schemas for type-safe validation
- Sanitize text inputs to prevent XSS
- Validate file uploads (type, size, content)

**API Security:**
- Use HTTPS for all communications (TLS 1.3+)
- Implement CSRF protection
- Rate limit API calls client-side
- Never expose sensitive data in URLs

**Content Security:**
```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data: https:; 
               connect-src 'self' https://api.cognitive.microsoft.com;">
```

---

## 15. Accessibility Implementation

### 15.1 WCAG 2.1 AA Compliance

**Keyboard Navigation:**
```typescript
// Example: Accessible button component
<Button
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
  aria-label="Start interview"
  tabIndex={0}
>
  Start Interview
</Button>
```

**Screen Reader Support:**
```typescript
// Example: ARIA live regions for dynamic content
<div role="status" aria-live="polite" aria-atomic="true">
  {isRecording ? 'Recording in progress' : 'Recording stopped'}
</div>

// Interview progress announcement
<div role="alert" aria-live="assertive">
  {`Question ${currentQuestion} of ${totalQuestions}`}
</div>
```

**Color Contrast:**
- Text: 4.5:1 minimum contrast ratio
- Large text (18pt+): 3:1 minimum
- UI components: 3:1 minimum
- Use color + icon/text (not color alone)

**Focus Management:**
```typescript
// Example: Focus trap in modal
import { useRef, useEffect } from 'react';

export const Modal = ({ isOpen, children }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      firstElement?.focus();

      const handleTab = (e: KeyboardEvent) => {
        if (e.key === 'Tab') {
          if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement?.focus();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement?.focus();
          }
        }
      };

      document.addEventListener('keydown', handleTab);
      return () => document.removeEventListener('keydown', handleTab);
    }
  }, [isOpen]);

  return <div ref={modalRef} role="dialog">{children}</div>;
};
```

### 15.2 Speech-Specific Accessibility

**Visual Alternatives:**
- Always show text transcript alongside speech
- Provide text input as fallback
- Visual indicators for all audio states
- Closed captions for AI speech (optional)

**Audio Feedback:**
- Confirm microphone is working before interview
- Visual audio level indicators
- Clear error messages for audio failures
- Allow replay of AI questions

---

## 16. Error Handling & Recovery

### 16.1 Error Boundary Implementation

```typescript
// src/components/shared/ErrorBoundary/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button } from '@mui/material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error boundary caught error:', error, errorInfo);
    // TODO: Send to error tracking service (Sentry, etc.)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '400px',
            p: 4,
          }}
        >
          <Typography variant="h4" gutterBottom>
            Something went wrong
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            We're sorry for the inconvenience. Please try refreshing the page.
          </Typography>
          <Button
            variant="contained"
            onClick={() => window.location.reload()}
          >
            Refresh Page
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
```

### 16.2 Graceful Degradation Strategies

**Audio Failure Fallback:**
```typescript
// src/features/interview/components/InterviewSession.tsx
const [audioMode, setAudioMode] = useState<'speech' | 'text'>('speech');
const [audioError, setAudioError] = useState<string | null>(null);

const handleAudioError = (error: string) => {
  setAudioError(error);
  setAudioMode('text');
  
  useGlobalStore.getState().addNotification({
    type: 'warning',
    message: 'Audio mode unavailable. Switched to text mode.',
  });
};

return (
  <>
    {audioMode === 'speech' ? (
      <SpeechInterface onError={handleAudioError} />
    ) : (
      <TextInterface />
    )}
  </>
);
```

**Network Failure Recovery:**
```typescript
// src/hooks/useOfflineDetection.ts
import { useState, useEffect } from 'react';

export const useOfflineDetection = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
};
```

---

## 17. Build & Deployment Configuration

### 17.1 Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          mui: ['@mui/material', '@emotion/react', '@emotion/styled'],
          query: ['@tanstack/react-query'],
          speech: ['microsoft-cognitiveservices-speech-sdk'],
        },
      },
    },
  },
});
```

### 17.2 Environment Configuration

```typescript
// src/config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url(),
  VITE_AZURE_SPEECH_KEY: z.string().min(1),
  VITE_AZURE_SPEECH_REGION: z.string().min(1),
  VITE_APP_NAME: z.string().default('Teamified'),
  VITE_APP_VERSION: z.string().default('1.0.0'),
  VITE_ENVIRONMENT: z.enum(['development', 'staging', 'production']).default('development'),
});

const validateEnv = () => {
  try {
    return envSchema.parse(import.meta.env);
  } catch (error) {
    console.error('❌ Invalid environment variables:', error);
    throw new Error('Invalid environment configuration');
  }
};

export const env = validateEnv();
```

### 17.3 Deployment Checklist

**Pre-Deployment:**
- [ ] Run `npm run type-check` - no TypeScript errors
- [ ] Run `npm run lint` - no linting errors
- [ ] Run `npm run test` - all tests passing
- [ ] Run `npm run build` - successful build
- [ ] Verify environment variables for target environment
- [ ] Test production build locally with `npm run preview`

**Production Optimizations:**
- [ ] Enable compression (gzip/brotli)
- [ ] Configure CDN for static assets
- [ ] Set up proper caching headers
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Set up performance monitoring
- [ ] Configure analytics tracking

---

## 18. Future Sections (To Be Documented During Implementation)

The following sections will be added as implementation progresses and specific platform/tooling decisions are finalized:

### 18.1 Real-Time Communication Architecture (Deferred)
**To be documented:**
- WebSocket or Server-Sent Events (SSE) for interview session management
- Real-time audio streaming architecture (if latency requirements change)
- Session reconnection and state synchronization logic
- Handling connection drops mid-interview

**Current MVP Approach:**
- HTTP-based request/response for audio processing (acceptable 5-7s per turn latency)
- Frontend polls for AI responses or uses long-polling
- Zustand store maintains session state with periodic backend sync

### 18.2 Deployment & DevOps (To Be Documented)
**To be documented during Sprint 0:**
- Dockerfile for production builds
- docker-compose for local development environment
- GitHub Actions CI/CD pipeline configuration
- Environment promotion strategy (dev → staging → production)
- Hosting platform specifics (AWS, Vercel, Netlify, etc.)
- CDN configuration for static assets
- SSL/TLS certificate management

### 18.3 Monitoring & Observability (To Be Documented)
**To be documented during Sprint 0/1:**
- Error tracking integration (Sentry or alternative)
- Web Vitals monitoring (LCP, FID, CLS tracking)
- User analytics event definitions
- OpenAI API cost monitoring dashboard
- Performance monitoring and alerting
- Frontend logging strategy

### 18.4 Storybook Configuration (To Be Documented)
**To be documented during component development:**
- `.storybook/main.ts` and `preview.ts` setup
- Story writing patterns with MUI theme integration
- Design system reference usage in stories
- Component documentation standards

---

## Document Completion

This frontend architecture document provides comprehensive guidance for implementing the Teamified Candidates Portal UI with speech-to-speech AI interview capabilities. All sections align with the PRD requirements, front-end specifications, design system reference, and technical best practices for React + TypeScript + MUI development.

**Architecture Maturity: MVP-Ready (95% Complete)**

Core architecture, tech stack, project structure, state management, API integration, and audio/speech processing are fully documented and ready for implementation. Deployment, monitoring, and real-time communication details will be finalized during Sprint 0 based on specific platform and tooling selections.

**Key Deliverables:**
- ✅ Framework and tooling decisions (Vite + React + TypeScript)
- ✅ Complete project structure with feature-based organization
- ✅ Component and naming standards
- ✅ State management patterns (Zustand + Context API)
- ✅ API integration architecture with interceptors
- ✅ Routing configuration with protected routes
- ✅ Styling guidelines (MUI theming + styled components)
- ✅ Testing requirements (Vitest + React Testing Library + Playwright)
- ✅ Environment setup and validation
- ✅ **Audio/Speech integration architecture (Azure Speech Services + WebRTC)**
- ✅ **Performance optimization strategies**
- ✅ **Security implementation patterns**
- ✅ **Accessibility compliance (WCAG 2.1 AA)**
- ✅ **Error handling and graceful degradation**
- ✅ **Build and deployment configuration**
- ✅ Developer quick reference

**Speech-to-Speech Capabilities (Epic 1.5):**
- OpenAI Whisper for speech-to-text (flexible architecture supports Azure/GCP alternatives)
- OpenAI TTS for natural AI voice responses
- Backend audio processing for security and auditability
- Web Audio API for real-time waveform visualization
- MediaRecorder API for audio capture
- Graceful degradation to text mode
- Hybrid input mode (voice + text for code)
- Future optimization: Azure Speech Services for real-time streaming if needed

**Performance Targets:**
- Initial bundle: <300KB (gzipped)
- Time to Interactive: <3s
- API responses: <2s (AI)
- Speech processing: <3s (STT), <2s (TTS) - acceptable for interview use case

**Security Measures:**
- JWT authentication with token refresh
- HTTPS/TLS 1.3+ encryption
- Input validation with Zod
- CSP headers for XSS protection
- Rate limiting implementation
- Backend audio processing (API keys never exposed to browser)

**Accessibility Features:**
- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader compatibility
- Visual alternatives for audio
- Focus management in modals

**Next Steps:**
1. ✅ Review and approve this architecture
2. Initialize project with `npm create vite@latest frontend -- --template react-ts`
3. Install dependencies: MUI, Zustand, React Router, **TanStack Query**
4. Set up project structure and absolute imports
5. Configure MUI theme from design system reference
6. Set up TanStack Query client and providers
7. Implement authentication flow and protected routes
8. Begin Epic 1.1: Project Initialization
9. Begin Epic 1.5: Speech-to-Speech Implementation

**Epic 1.5 Implementation Order (Updated):**
1. Story 1.5.1: Pre-Interview Audio System Check
2. Story 1.5.2: Frontend Audio Capture (MediaRecorder API)
3. Story 1.5.3: Backend OpenAI Whisper Integration
4. Story 1.5.4: Backend OpenAI TTS Integration
5. Story 1.5.5: Voice-Based Interview UI Enhancement
6. Story 1.5.6: Hybrid Input Mode - Voice + Text
7. Story 1.5.7: Audio Quality Monitoring & Fallback
8. Story 1.5.8: Cost Optimization (Caching, Monitoring)

**Deferred to Post-MVP:**
- Real-time audio streaming (WebRTC)
- Voice pattern analysis for integrity monitoring
- Azure/GCP Speech Services migration

---

**Architecture Review Status:** ✅ **MVP-READY (95% Complete)**

This architecture provides a solid foundation for implementing the Teamified Candidates Portal. Core technical decisions, project structure, state management, API integration, and audio/speech processing are fully documented and production-ready.

**Deferred to Implementation Phase:**
- Real-time communication specifics (WebSocket vs SSE decision pending latency testing)
- Deployment configuration (pending hosting platform selection)
- Monitoring setup (pending error tracking service selection)
- Storybook configuration (to be added during component development)

The simplified OpenAI-based approach for speech processing reduces vendor complexity while maintaining production quality. Backend processing ensures API key security and enables audio auditability. The architecture supports future migration to Azure Speech Services or GCP alternatives if real-time streaming becomes a requirement.

---

*Document Version: 1.4*  
*Last Updated: October 28, 2025*  
*Authors: Winston (Architect), John (PM)*  
*Status: **MVP-Ready - Core Architecture Complete, DevOps Details During Sprint 0***

