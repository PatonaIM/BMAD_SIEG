/**
 * Profile utility functions
 * Helper functions for profile completeness calculations and formatting
 */

import type { ProfileResponse, ProfileCompletenessBreakdown } from '@/types/profile';

/**
 * Format enum values for display (e.g., "permanent" -> "Permanent")
 */
export function formatEnumValue(value: string): string {
  return value
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Format array of enum values for display
 */
export function formatEnumArray(values: string[]): string {
  return values.map(formatEnumValue).join(', ');
}

/**
 * Calculate profile completeness breakdown
 * Matches backend algorithm from Story 4.3
 * 
 * Base Info (Email + Full Name): 20%
 * Phone: 10%
 * Skills: 20% (0% empty, 10% for 1-3 skills, 20% for 4+)
 * Experience Years: 15%
 * Job Preferences: 20% (incremental: locations 5%, employment types 5%, work setups 5%, salary 5%)
 * Resume: 15%
 * 
 * @param profile - Profile data
 * @returns Completeness breakdown with component percentages
 */
export function calculateProfileCompleteness(profile: ProfileResponse): ProfileCompletenessBreakdown {
  let baseInfo = 0;
  let phone = 0;
  let skills = 0;
  let experience = 0;
  let preferences = 0;
  let resume = 0;

  // Base Info: Email (10%) + Full Name (10%) = 20%
  if (profile.email) baseInfo += 10;
  if (profile.full_name) baseInfo += 10;

  // Phone: 10%
  if (profile.phone) phone = 10;

  // Skills: 20% (graduated)
  if (profile.skills.length === 0) {
    skills = 0;
  } else if (profile.skills.length >= 1 && profile.skills.length <= 3) {
    skills = 10;
  } else {
    skills = 20;
  }

  // Experience Years: 15%
  if (profile.experience_years !== undefined && profile.experience_years !== null) {
    experience = 15;
  }

  // Job Preferences: 20% (redistributed after removing locations)
  // Each criterion is worth ~6.67% to maintain 20% total
  if (profile.preferred_job_types.length > 0) {
    preferences += 7;
  }
  if (profile.preferred_work_setup && profile.preferred_work_setup !== 'any') {
    preferences += 7;
  }
  if (profile.salary_expectation_min && profile.salary_expectation_max) {
    preferences += 6;
  }

  // Resume: 15%
  if (profile.resume_id) {
    resume = 15;
  }

  const total = baseInfo + phone + skills + experience + preferences + resume;

  return {
    baseInfo,
    phone,
    skills,
    experience,
    preferences,
    resume,
    total,
  };
}

/**
 * Get missing profile sections for completion prompts
 * @param breakdown - Profile completeness breakdown
 * @returns Array of missing section names
 */
export function getMissingSections(breakdown: ProfileCompletenessBreakdown): string[] {
  const missing: string[] = [];

  if (breakdown.baseInfo < 20) missing.push('Basic Information');
  if (breakdown.phone === 0) missing.push('Phone Number');
  if (breakdown.skills < 20) missing.push('Skills');
  if (breakdown.experience === 0) missing.push('Experience');
  if (breakdown.preferences < 20) missing.push('Job Preferences');
  if (breakdown.resume === 0) missing.push('Resume');

  return missing;
}
