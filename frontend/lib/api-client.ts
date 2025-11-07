// API Client for Job Postings
// Handles data fetching and type definitions for job posting endpoints

import { ProfileResponseSchema } from '@/lib/schemas/profile.schema';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Job Posting Interface - matches backend JobPostingResponse schema
 */
export interface JobPosting {
  id: string;
  title: string;
  company: string;
  description: string;
  role_category: string;
  tech_stack: string | null;
  employment_type: string;
  work_setup: string;
  experience_level: string;
  location: string;
  salary_range_min: number | null;
  salary_range_max: number | null;
  required_skills: string[] | null;
  preferred_skills: string[] | null;
  benefits: string[] | null;
  posted_at: string;
  closing_at: string | null;
  status: string;
}

/**
 * Job Posting List Response - matches backend pagination schema
 */
export interface JobPostingListResponse {
  jobs: JobPosting[];
  total: number;
  skip: number;
  limit: number;
}

/**
 * Filter parameters for job posting queries
 */
export interface JobPostingFilters {
  role_category?: string;
  tech_stack?: string;
  employment_type?: string;
  work_setup?: string;
  experience_level?: string;
  location?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

/**
 * Job Postings API client
 */
export const jobPostingsApi = {
  /**
   * List job postings with optional filters
   * @param filters - Optional filter parameters for querying job postings
   * @returns Promise resolving to paginated job postings response
   */
  async list(filters?: JobPostingFilters): Promise<JobPostingListResponse> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          params.append(key, String(value));
        }
      });
    }
    const endpoint = `/job-postings${params.toString() ? `?${params.toString()}` : ''}`;
    return fetchApi<JobPostingListResponse>(endpoint);
  },
  
  /**
   * Get a single job posting by ID
   * @param id - Job posting UUID
   * @returns Promise resolving to job posting details
   */
  async getById(id: string): Promise<JobPosting> {
    return fetchApi<JobPosting>(`/job-postings/${id}`);
  },
};

/**
 * Application Status Type - matches backend enum
 */
export type ApplicationStatus =
  | 'applied'
  | 'interview_scheduled'
  | 'interview_completed'
  | 'under_review'
  | 'rejected'
  | 'offered'
  | 'accepted'
  | 'withdrawn';

/**
 * Interview Basic Interface - nested interview data from backend
 */
export interface InterviewBasic {
  id: string; // UUID as string
  status: string; // 'in_progress', 'completed', etc.
  role_type: string; // 'react', 'python', 'javascript', 'fullstack'
}

/**
 * Job Posting Basic Interface - simplified job posting for nested responses
 * Matches backend JobPostingBasicResponse schema
 */
export interface JobPostingBasic {
  id: string;
  title: string;
  company: string;
  role_category: string;
  tech_stack: string | null;
  employment_type: string;
  work_setup: string;
  location: string;
  status: string;
}

/**
 * Application Interface - matches backend ApplicationResponse schema
 */
export interface Application {
  id: string; // UUID as string
  candidate_id: string; // UUID as string
  job_posting_id: string; // UUID as string
  interview_id: string | null; // UUID as string or null
  status: ApplicationStatus;
  applied_at: string; // ISO 8601 datetime string
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
  job_posting: JobPostingBasic; // Nested job posting object
  interview?: InterviewBasic; // Optional nested interview object
}

/**
 * Fetch wrapper with authentication
 * Includes JWT token from localStorage if available
 */
async function fetchApiAuth<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('auth_token');
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear auth and redirect to login on 401
      localStorage.removeItem('auth_token');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Applications API client
 * IMPORTANT: GET /api/v1/applications/me returns Application[] directly (array, not object)
 */
export const applicationsApi = {
  /**
   * Get all applications for the authenticated candidate
   * @returns Promise resolving to array of applications with job details
   */
  async getMyApplications(): Promise<Application[]> {
    return fetchApiAuth<Application[]>('/applications/me');
  },

  /**
   * Get a single application by ID
   * @param id - Application UUID
   * @returns Promise resolving to application details
   */
  async getById(id: string): Promise<Application> {
    return fetchApiAuth<Application>(`/applications/${id}`);
  },

  /**
   * Create a new application for a job posting
   * Automatically creates and starts an AI interview linked to the application.
   * 
   * @param jobPostingId - UUID of the job posting to apply to
   * @returns Promise resolving to created application with job and interview details
   * @throws Error with status 409 if already applied to this job
   * @throws Error with status 404 if job posting not found
   * @throws Error with status 400 if job posting not active
   * @throws Error with status 401 if authentication invalid
   */
  async createApplication(jobPostingId: string): Promise<Application> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}/applications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ job_posting_id: jobPostingId }),
    });

    if (!response.ok) {
      // Handle specific error cases
      if (response.status === 401) {
        localStorage.removeItem('auth_token');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        throw new Error('Authentication required');
      }
      
      if (response.status === 409) {
        throw new Error('Already applied to this job');
      }
      
      if (response.status === 404) {
        throw new Error('Job posting not found');
      }
      
      if (response.status === 400) {
        throw new Error('Job posting is not active');
      }
      
      throw new Error(`Failed to create application: ${response.statusText}`);
    }

    return response.json();
  },
};

/**
 * Profile API client
 * Handles profile management endpoints from Story 4.3
 */
export const profileApi = {
  /**
   * Get the authenticated candidate's profile
   * Validates and normalizes response using Zod schema
   * @returns Promise resolving to profile data with completeness score
   */
  async get(): Promise<import('@/types/profile').ProfileResponse> {
    const rawResponse = await fetchApiAuth<unknown>('/profile');
    // Validate and transform using Zod schema (converts null arrays to empty arrays)
    const validated = ProfileResponseSchema.parse(rawResponse);
    return validated as import('@/types/profile').ProfileResponse;
  },

  /**
   * Update candidate skills
   * Backend normalizes skills to lowercase, trim, deduplicate, and sort
   * @param skills - Array of skill names (raw, backend normalizes)
   * @returns Promise resolving to updated profile
   */
  async updateSkills(skills: string[]): Promise<import('@/types/profile').ProfileResponse> {
    const rawResponse = await fetchApiAuth<unknown>('/profile/skills', {
      method: 'PUT',
      body: JSON.stringify({ skills }),
    });
    // Validate and transform using Zod schema
    const validated = ProfileResponseSchema.parse(rawResponse);
    return validated as import('@/types/profile').ProfileResponse;
  },

  /**
   * Update candidate job preferences
   * @param preferences - Job preferences data
   * @returns Promise resolving to updated profile
   */
  async updatePreferences(preferences: import('@/types/profile').UpdatePreferencesRequest): Promise<import('@/types/profile').ProfileResponse> {
    const rawResponse = await fetchApiAuth<unknown>('/profile/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
    // Validate and transform using Zod schema
    const validated = ProfileResponseSchema.parse(rawResponse);
    return validated as import('@/types/profile').ProfileResponse;
  },
};

/**
 * Resume API client
 * Handles resume parsing status from Story 4.2
 */
export const resumeApi = {
  /**
   * Get resume parsing status
   * Will return 404 if no resume uploaded yet
   * @param resumeId - Resume UUID from profile.resume_id
   * @returns Promise resolving to parsing status
   */
  async getParsingStatus(resumeId: string): Promise<import('@/types/profile').ResumeParsingStatus> {
    return fetchApiAuth<import('@/types/profile').ResumeParsingStatus>(`/resumes/${resumeId}/parsing-status`);
  },
};

/**
 * Matching API client
 * Handles job matching and explanation endpoints from Story 4.5 and 4.6
 */
export const matchingApi = {
  /**
   * Get matched jobs for the authenticated candidate
   * Returns jobs ranked by match score with explanations
   * 
   * @param page - Page number (default: 1)
   * @param limit - Results per page (default: 20, max: 100)
   * @returns Promise resolving to matched jobs with pagination
   * @throws Error with status 401 if authentication invalid
   * @throws Error with status 403 if profile completeness < 40%
   * @throws Error with status 404 if no profile embedding yet
   */
  async getMatches(page: number = 1, limit: number = 20): Promise<import('@/types/matching').JobMatchesResponse> {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    
    const response = await fetchApiAuth<{
      matches: any[];
      total_count: number;
      page: number;
      page_size: number;
    }>(`/matching/jobs?${params.toString()}`);

    // Transform backend response to match frontend type
    return {
      jobs: response.matches,
      total: response.total_count,
      page: response.page,
      limit: response.page_size,
    };
  },

  /**
   * Get match explanation for a specific job
   * Explains why the job matches the candidate's profile
   * 
   * @param jobId - Job posting UUID
   * @returns Promise resolving to match explanation
   * @throws Error with status 401 if authentication invalid
   * @throws Error with status 404 if job not found or match score < 40%
   * @throws Error with status 500 if OpenAI API failure
   */
  async getExplanation(jobId: string): Promise<import('@/types/matching').MatchExplanation> {
    return fetchApiAuth<import('@/types/matching').MatchExplanation>(
      `/matching/jobs/${jobId}/explanation`
    );
  },
};
