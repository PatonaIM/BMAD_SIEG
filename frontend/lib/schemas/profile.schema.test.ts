import { describe, it, expect } from 'vitest';
import { ProfileResponseSchema } from './profile.schema';

describe('ProfileResponseSchema', () => {
  it('transforms backend format to frontend format with null job_preferences', () => {
    const rawData = {
      id: '123',
      email: 'test@example.com',
      full_name: 'Test User',
      phone: null,
      skills: null,
      experience_years: null,
      job_preferences: null,
      profile_completeness_score: 20,
      resume_id: null,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    };

    const result = ProfileResponseSchema.parse(rawData);

    // Arrays should be empty, not null
    expect(result.skills).toEqual([]);
    expect(result.preferred_job_types).toEqual([]);
    expect(result.preferred_locations).toEqual([]);
    expect(result.preferred_work_setup).toBe('any');
    
    // Other fields should remain as is
    expect(result.email).toBe('test@example.com');
    expect(result.full_name).toBe('Test User');
  });

  it('transforms backend format with nested job_preferences', () => {
    const rawData = {
      id: '123',
      email: 'test@example.com',
      full_name: 'Test User',
      skills: ['JavaScript', 'TypeScript'],
      job_preferences: {
        locations: ['New York', 'Remote'],
        employment_types: ['Permanent', 'Contract'],
        work_setups: ['remote'],
        salary_min: 80000,
        salary_max: 120000,
      },
      profile_completeness_score: 80,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    };

    const result = ProfileResponseSchema.parse(rawData);

    // Check flattened preferences
    expect(result.preferred_locations).toEqual(['New York', 'Remote']);
    expect(result.preferred_job_types).toEqual(['Permanent', 'Contract']);
    expect(result.preferred_work_setup).toBe('remote');
    expect(result.salary_expectation_min).toBe(80000);
    expect(result.salary_expectation_max).toBe(120000);
    
    // Check other fields
    expect(result.skills).toEqual(['JavaScript', 'TypeScript']);
  });

  it('handles minimal backend response', () => {
    const rawData = {
      id: '123',
      email: 'test@example.com',
      full_name: 'Test User',
    };

    const result = ProfileResponseSchema.parse(rawData);

    // Arrays should be empty
    expect(result.skills).toEqual([]);
    expect(result.preferred_job_types).toEqual([]);
    expect(result.preferred_locations).toEqual([]);
    expect(result.preferred_work_setup).toBe('any');
    expect(result.profile_completeness_score).toBe(0);
  });
});
