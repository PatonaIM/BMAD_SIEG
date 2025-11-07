# Zod Schemas

This directory contains Zod schemas for runtime validation and data normalization.

## Why Zod?

Zod provides **runtime type safety** and **data transformation** at the API boundary, ensuring:

1. **Type Safety**: Validates data structure at runtime, not just compile time
2. **Null Safety**: Transforms `null` arrays to empty arrays automatically
3. **Data Transformation**: Converts backend format to frontend-friendly format
4. **Single Source of Truth**: API responses are validated and normalized in one place
5. **Better DX**: No need for optional chaining (`?.`) throughout the codebase

## Profile Schema

The `ProfileResponseSchema` handles two critical transformations:

### 1. Backend Format → Frontend Format

Backend returns nested `job_preferences`:
```typescript
{
  skills: null,
  job_preferences: {
    locations: ['New York'],
    employment_types: ['Full-time'],
    work_setups: ['remote'],
    salary_min: 80000,
    salary_max: 120000
  }
}
```

Frontend receives flat structure:
```typescript
{
  skills: [],
  preferred_locations: ['New York'],
  preferred_job_types: ['Full-time'],
  preferred_work_setup: 'remote',
  salary_expectation_min: 80000,
  salary_expectation_max: 120000
}
```

### 2. Null/Undefined → Empty Arrays

```typescript
// Backend returns:
{
  skills: null,
  job_preferences: null
}

// After Zod transformation:
{
  skills: [],
  preferred_locations: [],
  preferred_job_types: [],
  preferred_work_setup: 'any'
}
```

This means frontend code can safely use `.length`, `.map()`, etc. without null checks.

## Usage

Schemas are automatically applied in `lib/api-client.ts`:

```typescript
async get(): Promise<ProfileResponse> {
  const rawResponse = await fetchApiAuth<unknown>('/profile');
  // Validates, transforms, and normalizes the response
  return ProfileResponseSchema.parse(rawResponse);
}
```

## Adding New Schemas

1. Define the backend schema structure
2. Create transformation logic if backend/frontend formats differ
3. Add `.nullable().optional().transform(v => v ?? [])` for array fields
4. Export inferred type: `export type MyType = z.infer<typeof MySchema>;`
5. Use in API client to validate responses

## Benefits Over Alternatives

- **vs Optional Chaining**: Cleaner code, validation happens once at boundary
- **vs Backend Changes**: Works with any backend format, no coordination needed
- **vs Manual Normalization**: Declarative, type-safe, less error-prone
- **vs Adapter Pattern**: Built-in validation + transformation in one step
