# 3. Project Structure

\`\`\`
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
\`\`\`

## Structure Rationale

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
