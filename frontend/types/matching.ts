/**
 * Job Matching TypeScript Types
 * Matches backend API responses from Story 4.5 (Job Matching) and Story 4.6 (Match Explanations)
 */

/**
 * Match classification based on match score
 * - Excellent: ≥85%
 * - Great: 70-84%
 * - Good: 55-69%
 * - Fair: 40-54%
 */
export type MatchClassification = 'Excellent' | 'Great' | 'Good' | 'Fair';

/**
 * Preference matches breakdown showing which preferences align
 */
export interface PreferenceMatches {
  location: boolean;
  work_setup: boolean;
  employment_type: boolean;
  salary: boolean;
}

/**
 * Job Match with score and preference data
 * Extends job posting details with matching-specific fields
 */
export interface JobMatch {
  // Job details
  id: string;
  title: string;
  company: string;
  description: string;
  location: string;
  employment_type: string;
  work_setup: string;
  salary_min: number;
  salary_max: number;
  required_skills: string[];
  experience_level: string;
  status: string;
  
  // Match data
  match_score: number;                    // 0-100
  match_classification: MatchClassification;
  preference_matches: PreferenceMatches;
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

/**
 * Job Matches Response with pagination
 * Response from GET /api/v1/matching/jobs
 */
export interface JobMatchesResponse {
  jobs: JobMatch[];
  total: number;
  page: number;
  limit: number;
}

/**
 * Match Explanation with reasoning and factors
 * Response from GET /api/v1/matching/jobs/{job_id}/explanation
 */
export interface MatchExplanation {
  job_id: string;
  candidate_id: string;
  matching_factors: string[];
  missing_requirements: string[];
  overall_reasoning: string;
  confidence_score: number;  // 0-1
  generated_at: string;
}

/**
 * Filter state for matching UI
 */
export interface MatchingFilters {
  location?: string;
  work_setup?: string;
  employment_type?: string;
  salary_min?: number;
  salary_max?: number;
}
