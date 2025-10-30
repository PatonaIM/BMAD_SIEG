# 17. Build & Deployment Configuration

## 17.1 Vite Configuration

\`\`\`typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          mui: ['@mui/material', '@emotion/react', '@emotion/styled'],
          query: ['@tanstack/react-query'],
          speech: ['microsoft-cognitiveservices-speech-sdk'],
        },
      },
    },
  },
});
\`\`\`

## 17.2 Environment Configuration

\`\`\`typescript
// src/config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url(),
  VITE_AZURE_SPEECH_KEY: z.string().min(1),
  VITE_AZURE_SPEECH_REGION: z.string().min(1),
  VITE_APP_NAME: z.string().default('Teamified'),
  VITE_APP_VERSION: z.string().default('1.0.0'),
  VITE_ENVIRONMENT: z.enum(['development', 'staging', 'production']).default('development'),
});

const validateEnv = () => {
  try {
    return envSchema.parse(import.meta.env);
  } catch (error) {
    console.error('❌ Invalid environment variables:', error);
    throw new Error('Invalid environment configuration');
  }
};

export const env = validateEnv();
\`\`\`

## 17.3 Deployment Checklist

**Pre-Deployment:**
- [ ] Run `npm run type-check` - no TypeScript errors
- [ ] Run `npm run lint` - no linting errors
- [ ] Run `npm run test` - all tests passing
- [ ] Run `npm run build` - successful build
- [ ] Verify environment variables for target environment
- [ ] Test production build locally with `npm run preview`

**Production Optimizations:**
- [ ] Enable compression (gzip/brotli)
- [ ] Configure CDN for static assets
- [ ] Set up proper caching headers
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Set up performance monitoring
- [ ] Configure analytics tracking

---
