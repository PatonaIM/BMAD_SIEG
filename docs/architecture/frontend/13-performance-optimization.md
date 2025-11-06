# 13. Performance Optimization

## 13.1 Code Splitting Strategy

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

**Code Splitting (Next.js App Router):**
```typescript
// app/interview/page.tsx
import dynamic from 'next/dynamic';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';

// Lazy load heavy components
const InterviewInterface = dynamic(
  () => import('@/components/interview/InterviewInterface'),
  { loading: () => <LoadingSpinner /> }
);

const SpeechVisualizer = dynamic(
  () => import('@/components/interview/SpeechVisualizer'),
  { ssr: false } // Disable SSR for client-only components
);
```

**Asset Optimization:**
```typescript
// next.config.mjs
export default {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // Optimize webpack bundles
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            name: 'vendor',
            priority: 10,
          },
          mui: {
            test: /[\\/]node_modules[\\/](@mui|@emotion)[\\/]/,
            name: 'mui',
            priority: 9,
          },
          query: {
            test: /[\\/]node_modules[\\/](@tanstack)[\\/]/,
            name: 'query',
            priority: 8,
          },
        },
      };
    }
    return config;
  },
};
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
