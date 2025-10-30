# 9. Testing Requirements

## 9.1 Test Setup

\`\`\`typescript
// tests/setup.ts
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
\`\`\`

## 9.2 Component Test Template

\`\`\`typescript
// Component.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '@/theme/theme';
import { ComponentName } from './ComponentName';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={teamifiedTheme}>
      {component}
    </ThemeProvider>
  );
};

describe('ComponentName', () => {
  it('renders correctly', () => {
    renderWithProviders(<ComponentName />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const handleClick = vi.fn();
    renderWithProviders(<ComponentName onClick={handleClick} />);
    
    fireEvent.click(screen.getByRole('button'));
    
    await waitFor(() => {
      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });
});
\`\`\`

## 9.3 Testing Best Practices

1. **Unit Tests**: Test components in isolation
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test critical user flows with Playwright
4. **Coverage Goal**: 80% code coverage
5. **Test Structure**: Arrange-Act-Assert pattern
6. **Mock External Dependencies**: API calls, routing, global state

---
