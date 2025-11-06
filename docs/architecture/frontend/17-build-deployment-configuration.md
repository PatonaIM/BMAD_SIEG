# 17. Build & Deployment Configuration

## 17.1 Next.js Configuration

```typescript
// next.config.mjs
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Path aliases
  webpack: (config) => {
    config.resolve.alias['@'] = join(__dirname, '.');
    return config;
  },
  
  // Environment variables validation
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
    NEXT_PUBLIC_MOCK_API: process.env.NEXT_PUBLIC_MOCK_API,
  },
  
  // Optimize builds
  swcMinify: true,
  
  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
    domains: [], // Add your CDN domains here
  },
  
  // Production optimizations
  productionBrowserSourceMaps: false,
  compress: true,
};

export default nextConfig;
```

## 17.2 Environment Configuration

```typescript
// config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z.string().url(),
  NEXT_PUBLIC_AZURE_SPEECH_KEY: z.string().min(1).optional(),
  NEXT_PUBLIC_AZURE_SPEECH_REGION: z.string().min(1).optional(),
  NEXT_PUBLIC_APP_NAME: z.string().default('Teamified'),
  NEXT_PUBLIC_APP_VERSION: z.string().default('1.0.0'),
  NEXT_PUBLIC_ENVIRONMENT: z.enum(['development', 'staging', 'production']).default('development'),
  NEXT_PUBLIC_MOCK_API: z.string().transform(val => val === 'true').default('false'),
});

const validateEnv = () => {
  try {
    return envSchema.parse(process.env);
  } catch (error) {
    console.error('❌ Invalid environment variables:', error);
    throw new Error('Invalid environment configuration');
  }
};

export const env = validateEnv();
```

## 17.3 Deployment Checklist

**Pre-Deployment:**
- [ ] Run `pnpm type-check` or `pnpm build` - no TypeScript errors
- [ ] Run `pnpm lint` - no linting errors
- [ ] Run `pnpm test` - all tests passing
- [ ] Run `pnpm build` - successful build
- [ ] Verify environment variables for target environment
- [ ] Test production build locally with `pnpm start`

**Production Optimizations:**
- [ ] Enable compression (Next.js does this automatically)
- [ ] Configure CDN for static assets (Vercel does this automatically)
- [ ] Set up proper caching headers (configured in `next.config.mjs`)
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Set up performance monitoring
- [ ] Configure analytics tracking (@vercel/analytics already installed)

---
