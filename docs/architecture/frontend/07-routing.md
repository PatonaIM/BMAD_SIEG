# 7. Routing

## 7.1 Route Configuration

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

## 7.2 Protected Route Component

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

## 7.3 Router Setup

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
