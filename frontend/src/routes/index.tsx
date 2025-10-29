import { createBrowserRouter, Navigate } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import InterviewStartPage from '../pages/InterviewStartPage';
import InterviewPage from '../pages/InterviewPage';
import HealthCheckPage from '../pages/HealthCheckPage';
import { ProtectedRoute } from './ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" replace />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/interview/start',
    element: (
      <ProtectedRoute>
        <InterviewStartPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/interview/:sessionId',
    element: (
      <ProtectedRoute>
        <InterviewPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/health',
    element: <HealthCheckPage />,
  },
]);
