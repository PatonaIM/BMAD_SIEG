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
 * Profile Response Schema
 * Backend now sends flattened preference fields directly (no nested job_preferences)
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
  
  // Flattened preference fields (from backend Pydantic transformation)
  preferred_job_types: z.array(z.string())
    .nullable()
    .optional()
    .transform(v => v ?? []),
  preferred_work_setup: z.string().optional().default('any'),
  salary_expectation_min: z.number().optional().nullable(),
  salary_expectation_max: z.number().optional().nullable(),
  salary_currency: z.string().optional().default('USD'),
  salary_period: z.string().optional().default('annually'),
  
  profile_completeness_score: z.number().min(0).max(100).nullable().optional().transform(v => v ?? 0),
  resume_id: z.string().optional().nullable(),
  
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
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
  preferred_work_setup: WorkSetupSchema,
  salary_expectation_min: z.number().optional(),
  salary_expectation_max: z.number().optional(),
  salary_currency: z.string(),
  salary_period: z.string().optional(),
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
