# 2. Frontend Tech Stack

## Technology Stack Table

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

## Key Technology Decisions

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
