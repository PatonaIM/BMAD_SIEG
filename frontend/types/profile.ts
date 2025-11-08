/**
 * Profile TypeScript Types
 * Matches backend API responses from Story 4.3 - Profile Management APIs
 */

/**
 * Work setup preference type
 */
export type WorkSetup = 'remote' | 'hybrid' | 'onsite' | 'any';

/**
 * Profile Response - matches backend ProfileResponse schema
 */
export interface ProfileResponse {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  skills: string[];
  experience_years?: number;
  preferred_job_types: string[];
  preferred_locations: string[];
  preferred_work_setup: WorkSetup;
  salary_expectation_min?: number;
  salary_expectation_max?: number;
  salary_currency: string;
  salary_period?: string; // 'monthly' | 'annually'
  profile_completeness_score: number;
  resume_id?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Skills Update Request - for PUT /api/v1/profile/skills
 */
export interface UpdateSkillsRequest {
  skills: string[];
}

/**
 * Basic Info Update Request - for PUT /api/v1/profile/basic-info
 */
export interface UpdateBasicInfoRequest {
  full_name?: string;
  phone?: string;
  experience_years?: number;
}

/**
 * Preferences Update Request - for PUT /api/v1/profile/preferences
 */
export interface UpdatePreferencesRequest {
  preferred_job_types: string[];
  preferred_locations: string[];
  preferred_work_setup: WorkSetup;
  salary_expectation_min?: number;
  salary_expectation_max?: number;
  salary_currency: string;
  salary_period?: string; // 'monthly' | 'annually'
}

/**
 * Resume parsing status type
 */
export type ParsingStatus = 'pending' | 'processing' | 'completed' | 'failed';

/**
 * Parsed resume data
 */
export interface ParsedData {
  skills: string[];
  experience_years?: number;
  education?: string[];
  previous_roles?: string[];
}

/**
 * Resume Parsing Status Response - for GET /api/v1/resumes/{resume_id}/parsing-status
 */
export interface ResumeParsingStatus {
  resume_id: string;
  status: ParsingStatus;
  parsed_data?: ParsedData;
  error_message?: string;
}

/**
 * Profile completeness breakdown - used for UI display
 */
export interface ProfileCompletenessBreakdown {
  baseInfo: number;      // Email + Full Name: 20%
  phone: number;         // Phone: 10%
  skills: number;        // Skills: 20% (graduated)
  experience: number;    // Experience Years: 15%
  preferences: number;   // Job Preferences: 20% (incremental)
  resume: number;        // Resume: 15%
  total: number;         // Total: 0-100%
}
