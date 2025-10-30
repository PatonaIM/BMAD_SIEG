# 13. Performance Optimization

## 13.1 Code Splitting Strategy

\`\`\`typescript
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
\`\`\`

## 13.2 Performance Budgets

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

## 13.3 Optimization Techniques

**Asset Optimization:**
\`\`\`typescript
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
\`\`\`

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
