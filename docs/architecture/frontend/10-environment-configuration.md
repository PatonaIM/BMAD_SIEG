# 10. Environment Configuration

## 10.1 Environment Variables

```bash
# .env.example
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=Teamified
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_MOCK_API=false
```

```typescript
// config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z.string().url(),
  NEXT_PUBLIC_APP_NAME: z.string().default('Teamified'),
  NEXT_PUBLIC_APP_VERSION: z.string().default('1.0.0'),
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

---
