# 6. API Integration

## 6.1 TanStack Query Setup

\`\`\`typescript
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
\`\`\`

\`\`\`typescript
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
\`\`\`

## 6.2 API Client with Fetch

\`\`\`typescript
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
\`\`\`

## 6.3 API Endpoints

\`\`\`typescript
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
\`\`\`

## 6.4 Service with TanStack Query

\`\`\`typescript
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
\`\`\`

## 6.5 Query Hooks Pattern

\`\`\`typescript
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
\`\`\`

## 6.6 Using Queries in Components

\`\`\`typescript
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
\`\`\`

\`\`\`typescript
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
\`\`\`

---
