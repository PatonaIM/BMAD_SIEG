# 2. Frontend Tech Stack

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Framework** | Next.js | 16+ | Full-stack React framework with App Router | Production-grade SSR/CSR, file-based routing, excellent performance, built-in optimization |
| **React Library** | React | 19+ | UI framework with Server Components | Industry standard, React Server Components support, excellent TypeScript integration |
| **Language** | TypeScript | 5.0+ | Type-safe development | Prevents runtime errors, better IDE support, essential for complex state management |
| **Build Tool** | Next.js Built-in (Turbopack) | Built-in | Fast development and production builds | Instant HMR, optimized builds, integrated with Next.js |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS framework | Fast styling, consistent design, excellent DX, smaller bundle vs CSS-in-JS |
| **UI Library** | Material-UI (MUI) + shadcn/ui | MUI 5.14+, shadcn latest | Component libraries | Accessible components, customizable, production-ready, modern design patterns |
| **State Management** | Zustand + React Context | Zustand 4.4+ | Global and local state | Lightweight, minimal boilerplate, Context for simple cases |
| **Routing** | Next.js App Router | Built-in | File-based routing with SSR/CSR | Zero configuration, automatic code splitting, middleware support |
| **Form Handling** | React Hook Form | 7.48+ | Form state and validation | Performance optimized, minimal re-renders, integrates with validation libraries |
| **Validation** | Zod | 3.22+ | Schema validation | Type-safe validation, works seamlessly with TypeScript and React Hook Form |
| **Data Fetching** | TanStack Query (React Query) | 5.0+ | Server state management and caching | Auto caching, background refetching, optimistic updates, request deduplication |
| **HTTP Client** | Fetch API | Native | HTTP requests | Modern native API, used by TanStack Query, no additional dependencies |
| **Audio Processing** | Web Audio API + MediaRecorder | Native | Real-time audio capture and visualization | Built-in browser APIs, no additional dependencies for core audio features |
| **Speech Integration** | OpenAI Whisper + TTS | API | Speech-to-text and text-to-speech | Primary provider for MVP, flexible architecture supports Azure/GCP alternatives |
| **Testing Framework** | Vitest | 1.0+ | Unit and integration testing | Native Vite integration, Jest-compatible API, faster execution |
| **Testing Library** | React Testing Library | 14.1+ | Component testing | Best practices for user-centric testing, accessibility focus |
| **E2E Testing** | Playwright | 1.40+ | End-to-end testing | Cross-browser, reliable, great for audio/video testing |
| **Animation** | Framer Motion | 10.16+ | UI animations and transitions | Declarative animations, perfect for waveform visualizers and progress indicators |
| **Data Visualization** | Recharts | 2.10+ | Skill maps and analytics charts | React-native, customizable, good for recruiter dashboards |
| **Code Quality** | ESLint + Prettier | Latest | Linting and formatting | Code consistency, catch errors early |
| **Type Checking** | TypeScript ESLint | Latest | TypeScript-specific linting | Enforce TypeScript best practices |
| **Dev Tools** | React DevTools, TanStack Query DevTools | Latest | Development debugging | State inspection, performance profiling, query debugging |

## Key Technology Decisions

### **Next.js 16 App Router over Vite + React Router**
**Migration Rationale (v2.0):**
- **SEO Critical**: Server-rendered pages enable search engine indexing (job listings, company profiles)
- **Performance**: 40-60% faster initial page load with SSR vs client-only SPA
- **Automatic Code Splitting**: Route-based splitting without manual configuration
- **File-Based Routing**: `app/` directory structure eliminates routing configuration
- **Production Ecosystem**: Vercel deployment, preview URLs, edge functions
- **React Server Components**: Reduced JavaScript bundle size for non-interactive pages
- **Image Optimization**: Built-in next/image component with automatic optimization
- **API Routes**: Backend integration within same codebase (optional, we use separate backend)

**Implementation Patterns:**
- Server Components (default): Layouts, static pages, SEO-critical content
- Client Components ("use client"): Forms, state management, real-time features, audio processing
- Hybrid Pages: Server-rendered shell + client-side interactivity

**Migration Impact:**
- Navigation: `useNavigate()` → `useRouter()` from `next/navigation`
- Links: `<Link to>` → `<Link href>`
- Environment Variables: `VITE_*` → `NEXT_PUBLIC_*`
- Preserved: API client, React Query hooks, Zustand stores (no changes)

### **Tailwind CSS over MUI Emotion (Styling Evolution)**
**Added in v2.0:**
- **Utility-First Approach**: Faster styling iteration vs CSS-in-JS
- **Smaller Bundles**: No runtime CSS-in-JS overhead
- **Design Tokens**: Consistent spacing, colors, typography via Tailwind config
- **shadcn/ui Integration**: Pre-built accessible components with Tailwind
- **MUI Coexistence**: Keep MUI for complex components (DataGrid, DatePicker)
- **Performance**: No styled-components re-renders or theme prop drilling

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

## Mock API Mode for UI Development

**New in v2.0:** `NEXT_PUBLIC_MOCK_API` Feature Flag

**Purpose:** Enable UI/UX development and testing without backend dependency

**Implementation:**
```typescript
// src/config/env.ts
export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
  mockApi: process.env.NEXT_PUBLIC_MOCK_API === 'true',
};

// src/services/api/client.ts
if (env.mockApi) {
  await mockDelay(300); // Simulate network latency
  return getMockResponse<T>(endpoint, method);
}
```

**Benefits:**
- UI development without running backend server
- Faster iteration on design and interactions
- Demo-ready builds for stakeholders
- E2E testing with predictable data
- Parallel frontend/backend development

**Mock Data:** `src/services/api/mocks/mockData.ts` contains sample responses

---
