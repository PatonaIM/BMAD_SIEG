# 14. Security Implementation

## 14.1 Authentication Flow

\`\`\`typescript
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
\`\`\`

\`\`\`typescript
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
\`\`\`

## 14.2 Security Best Practices

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
\`\`\`html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data: https:; 
               connect-src 'self' https://api.cognitive.microsoft.com;">
\`\`\`

---
