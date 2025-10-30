# 10. Environment Configuration

## 10.1 Environment Variables

```bash
# .env.example
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Teamified
VITE_APP_VERSION=1.0.0
```

```typescript
// src/config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url(),
  VITE_APP_NAME: z.string().default('Teamified'),
  VITE_APP_VERSION: z.string().default('1.0.0'),
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
```

---
