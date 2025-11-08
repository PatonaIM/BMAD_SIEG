// Resume Upload & Analysis API Client

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Resume Upload Response - matches backend ResumeUploadResponse schema
 */
export interface ResumeUploadResponse {
  id: string;
  file_name: string;
  file_size: number;
  uploaded_at: string;
  storage_url: string;
  is_active: boolean;
}

/**
 * Resume Metadata Response - matches backend ResumeResponse schema
 */
export interface ResumeResponse {
  id: string;
  file_name: string;
  file_size: number;
  uploaded_at: string;
  is_active: boolean;
  parsing_status?: string;
}

/**
 * Resume Analysis Response - matches backend ResumeAnalysisResponse schema
 */
export interface ResumeAnalysisResponse {
  id: string;
  resume_id: string;
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  keywords_missing: string[];
  analysis_model: string;
  analyzed_at: string;
}

/**
 * Resumes API client
 */
export const resumesApi = {
  /**
   * Upload a resume PDF file
   * @param file - PDF file to upload
   * @returns Promise resolving to resume upload response
   */
  async upload(file: File): Promise<ResumeUploadResponse> {
    const token = getAuthToken();
    if (!token) throw new Error('Authentication required');

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/resumes/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || `Upload failed: ${response.status}`);
    }

    return response.json();
  },

  /**
   * List all resumes for current candidate
   * @returns Promise resolving to array of resumes
   */
  async list(): Promise<ResumeResponse[]> {
    const token = getAuthToken();
    if (!token) throw new Error('Authentication required');

    const response = await fetch(`${API_BASE_URL}/resumes`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch resumes: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Get single resume details
   * @param resumeId - UUID of the resume
   * @returns Promise resolving to resume details
   */
  async get(resumeId: string): Promise<ResumeResponse> {
    const token = getAuthToken();
    if (!token) throw new Error('Authentication required');

    const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch resume: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Get AI analysis for a resume
   * @param resumeId - UUID of the resume
   * @returns Promise resolving to analysis results or null if not ready
   */
  async getAnalysis(resumeId: string): Promise<ResumeAnalysisResponse | null> {
    const token = getAuthToken();
    if (!token) throw new Error('Authentication required');

    const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}/analysis`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 404) {
      // Analysis not ready yet
      return null;
    }

    if (!response.ok) {
      throw new Error(`Failed to fetch analysis: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Set a resume as active
   * @param resumeId - UUID of the resume
   * @returns Promise resolving to updated resume
   */
  async activate(resumeId: string): Promise<ResumeResponse> {
    const token = getAuthToken();
    if (!token) throw new Error('Authentication required');

    const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}/activate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to activate resume: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Delete a resume
   * @param resumeId - UUID of the resume
   * @returns Promise resolving when deleted
   */
  async delete(resumeId: string): Promise<void> {
    const token = getAuthToken();
    if (!token) throw new Error('Authentication required');

    const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete resume: ${response.status}`);
    }
  },

  /**
   * Get signed URL for resume download
   * @param resumeId - UUID of the resume
   * @returns Promise resolving to signed URL
   */
  async getDownloadUrl(resumeId: string): Promise<string> {
    const token = getAuthToken();
    if (!token) throw new Error('Authentication required');

    const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}/download`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get download URL: ${response.status}`);
    }

    const data = await response.json();
    return data.signed_url;
  },
};
