/**
 * Zod schemas for profile data validation and normalization
 * Ensures type safety and handles null/undefined values from backend
 */

import { z } from 'zod';

/**
 * Work setup enum schema
 */
export const WorkSetupSchema = z.enum(['remote', 'hybrid', 'onsite', 'any']);

/**
 * Backend Job Preferences Schema (nested structure)
 */
const JobPreferencesSchema = z.object({
  locations: z.array(z.string()).nullable().optional(),
  employment_types: z.array(z.string()).nullable().optional(),
  work_setups: z.array(z.string()).nullable().optional(),
  salary_min: z.number().nullable().optional(),
  salary_max: z.number().nullable().optional(),
  role_categories: z.array(z.string()).nullable().optional(),
}).nullable().optional();

/**
 * Profile Response Schema
 * Transforms backend format (nested job_preferences) to frontend format (flat fields)
 * Also transforms null/undefined arrays to empty arrays for type safety
 */
export const ProfileResponseSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  full_name: z.string(),
  phone: z.string().optional().nullable(),
  
  // Array fields: transform null/undefined to empty array
  skills: z.array(z.string())
    .nullable()
    .optional()
    .transform(v => v ?? []),
  
  experience_years: z.number().optional().nullable(),
  
  // Backend uses nested job_preferences, flatten for frontend
  job_preferences: JobPreferencesSchema,
  
  profile_completeness_score: z.number().min(0).max(100).nullable().optional().transform(v => v ?? 0),
  resume_id: z.string().optional().nullable(),
  
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
}).transform((data) => {
  // Flatten job_preferences into top-level fields for frontend
  const prefs = data.job_preferences || {};
  
  return {
    id: data.id,
    email: data.email,
    full_name: data.full_name,
    phone: data.phone,
    skills: data.skills,
    experience_years: data.experience_years,
    
    // Flatten preferences
    preferred_job_types: prefs.employment_types ?? [],
    preferred_locations: prefs.locations ?? [],
    preferred_work_setup: (prefs.work_setups?.[0] as any) ?? 'any',
    salary_expectation_min: prefs.salary_min ?? undefined,
    salary_expectation_max: prefs.salary_max ?? undefined,
    salary_currency: 'USD', // Backend doesn't store this yet
    
    profile_completeness_score: data.profile_completeness_score,
    resume_id: data.resume_id,
    created_at: data.created_at,
    updated_at: data.updated_at,
  };
});

/**
 * Update Skills Request Schema
 */
export const UpdateSkillsRequestSchema = z.object({
  skills: z.array(z.string()),
});

/**
 * Update Preferences Request Schema
 */
export const UpdatePreferencesRequestSchema = z.object({
  preferred_job_types: z.array(z.string()),
  preferred_locations: z.array(z.string()),
  preferred_work_setup: WorkSetupSchema,
  salary_expectation_min: z.number().optional(),
  salary_expectation_max: z.number().optional(),
  salary_currency: z.string(),
});

/**
 * Resume Parsing Status Schema
 */
export const ParsingStatusSchema = z.enum(['pending', 'processing', 'completed', 'failed']);

export const ParsedDataSchema = z.object({
  skills: z.array(z.string()).optional(),
  experience_years: z.number().optional(),
  education: z.array(z.string()).optional(),
  previous_roles: z.array(z.string()).optional(),
});

export const ResumeParsingStatusSchema = z.object({
  resume_id: z.string(),
  status: ParsingStatusSchema,
  parsed_data: ParsedDataSchema.optional(),
  error_message: z.string().optional(),
});

// Export inferred types
export type ProfileResponseValidated = z.infer<typeof ProfileResponseSchema>;
export type UpdateSkillsRequest = z.infer<typeof UpdateSkillsRequestSchema>;
export type UpdatePreferencesRequest = z.infer<typeof UpdatePreferencesRequestSchema>;
export type ResumeParsingStatus = z.infer<typeof ResumeParsingStatusSchema>;
