# 16. Error Handling & Recovery

## 16.1 Error Boundary Implementation

```typescript
// src/components/shared/ErrorBoundary/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button } from '@mui/material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error boundary caught error:', error, errorInfo);
    // TODO: Send to error tracking service (Sentry, etc.)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '400px',
            p: 4,
          }}
        >
          <Typography variant="h4" gutterBottom>
            Something went wrong
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            We're sorry for the inconvenience. Please try refreshing the page.
          </Typography>
          <Button
            variant="contained"
            onClick={() => window.location.reload()}
          >
            Refresh Page
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
```

## 16.2 Graceful Degradation Strategies

**Audio Failure Fallback:**
```typescript
// src/features/interview/components/InterviewSession.tsx
const [audioMode, setAudioMode] = useState<'speech' | 'text'>('speech');
const [audioError, setAudioError] = useState<string | null>(null);

const handleAudioError = (error: string) => {
  setAudioError(error);
  setAudioMode('text');
  
  useGlobalStore.getState().addNotification({
    type: 'warning',
    message: 'Audio mode unavailable. Switched to text mode.',
  });
};

return (
  <>
    {audioMode === 'speech' ? (
      <SpeechInterface onError={handleAudioError} />
    ) : (
      <TextInterface />
    )}
  </>
);
```

**Network Failure Recovery:**
```typescript
// src/hooks/useOfflineDetection.ts
import { useState, useEffect } from 'react';

export const useOfflineDetection = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
};
```

---
