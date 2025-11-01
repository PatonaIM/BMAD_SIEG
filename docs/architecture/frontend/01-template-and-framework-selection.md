# 1. Template and Framework Selection

## Decision: Next.js 16 App Router + React + TypeScript

**Migration History:**
- **Initial (v1.0-1.4)**: Vite + React Router SPA (Client-Side Only)
- **Current (v2.0+)**: Next.js 16 App Router (SSR/CSR Hybrid)

**Existing Foundation:**
- **Design System Reference**: Complete v0.dev-generated design system in `docs/style-guide/design-system-reference/`
- **Framework**: React 19+ with TypeScript
- **Component Library**: Material-UI (MUI) + Custom Teamified components + shadcn/ui
- **UI Components**: shadcn/ui components as base with Tailwind CSS
- **Rendering**: Hybrid Server-Side Rendering (SSR) + Client-Side Rendering (CSR)
- **Starter Pattern**: Next.js App Router with custom design system

**Selected Framework: Next.js 16 App Router**

**Rationale for Migration:**
- **SEO Optimization**: Server-rendered pages improve search engine visibility (critical for public job listings)
- **Performance**: Faster initial page load with SSR, code-split by route automatically
- **File-Based Routing**: Zero-configuration routing via `app/` directory structure
- **Hybrid Rendering**: Server Components for static content, Client Components for interactive features
- **Production-Ready**: Battle-tested framework with excellent deployment ecosystem (Vercel, AWS)
- **Developer Experience**: Built-in API routes, middleware, image optimization
- **Modern React**: Full support for React Server Components and Suspense
- **Better Bundle Optimization**: Automatic code splitting and tree shaking

**Migration Benefits Over Vite SPA:**
1. **SEO**: Public pages (job listings, company profiles) now crawlable
2. **Initial Load Speed**: 40-60% faster first contentful paint with SSR
3. **Code Splitting**: Automatic route-based splitting (no manual configuration)
4. **API Integration**: Middleware layer for authentication and request handling
5. **Production Deployment**: First-class Vercel integration with preview deployments

**Trade-offs:**
- **Learning Curve**: App Router patterns differ from React Router
- **Complexity**: SSR/CSR boundary requires "use client" directives
- **Build Time**: Slightly slower builds vs Vite (acceptable trade-off)

**Key Implementation Patterns:**
- **Server Components**: Layouts, static pages, data fetching (default)
- **Client Components**: Forms, state management, real-time features (marked with "use client")
- **Navigation**: `useRouter` from `next/navigation` (replaces `useNavigate`)
- **Environment Variables**: `NEXT_PUBLIC_*` prefix for client-side access

**Key Constraints:**
- Reference components in `design-system-reference/` are NOT production code
- Production implementation in `app/` (App Router) and `src/` with proper backend integration
- Must maintain design specifications from reference while adding proper state management and API integration
- Mock API mode (`NEXT_PUBLIC_MOCK_API=true`) enables UI development without backend

---
