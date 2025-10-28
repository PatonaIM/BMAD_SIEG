# 4. Component Standards

## 4.1 Component Template

```typescript
// src/components/ui/Button/Button.tsx
import React from 'react';
import { Button as MuiButton, ButtonProps as MuiButtonProps } from '@mui/material';
import { styled } from '@mui/material/styles';

/**
 * Custom button component extending MUI Button
 * Implements Teamified design system specifications
 */

// Styled component for custom variants
const StyledButton = styled(MuiButton)(({ theme }) => ({
  textTransform: 'none', // Prevent uppercase transform
  fontWeight: 600,
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(1.5, 3),
  
  '&.MuiButton-containedPrimary': {
    backgroundColor: theme.palette.primary.main,
    '&:hover': {
      backgroundColor: theme.palette.primary.dark,
    },
  },
}));

// Extend MUI ButtonProps with custom props
export interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  /** Loading state */
  isLoading?: boolean;
  /** Full width button */
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  disabled,
  children,
  ...props
}) => {
  // Map custom variants to MUI variants
  const muiVariant = variant === 'ghost' ? 'text' : 'contained';
  const muiColor = variant === 'danger' ? 'error' : 'primary';

  return (
    <StyledButton
      variant={muiVariant}
      color={muiColor}
      size={size}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? 'Loading...' : children}
    </StyledButton>
  );
};

Button.displayName = 'Button';

export default Button;
```

```typescript
// src/components/ui/Button/index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button';
```

```typescript
// src/components/ui/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '@/theme/theme';

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={teamifiedTheme}>
      {component}
    </ThemeProvider>
  );
};

describe('Button', () => {
  it('renders with children', () => {
    renderWithTheme(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    renderWithTheme(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    renderWithTheme(<Button isLoading>Submit</Button>);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('disables button when disabled prop is true', () => {
    renderWithTheme(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

## 4.2 Naming Conventions

**Files:**
- **Components**: PascalCase - `Button.tsx`, `WaveformVisualizer.tsx`
- **Tests**: Match component - `Button.test.tsx`
- **Types**: Match component - `button.types.ts` (lowercase with dots)
- **Hooks**: camelCase with `use` prefix - `useAudioRecording.ts`
- **Services**: camelCase with suffix - `interviewService.ts`
- **Utils**: camelCase - `formatters.ts`, `validators.ts`
- **Stores**: camelCase with `Store` suffix - `authStore.ts`
- **Index files**: `index.ts` (barrel exports)

**Directories:**
- **Component folders**: PascalCase - `Button/`, `WaveformVisualizer/`
- **Feature folders**: lowercase - `auth/`, `interview/`, `resume/`
- **Utility folders**: lowercase - `hooks/`, `services/`, `utils/`

**Code:**
- **Components**: PascalCase - `<Button />`, `<InterviewChat />`
- **Functions**: camelCase - `formatDate()`, `validateEmail()`
- **Hooks**: camelCase with `use` prefix - `useAuth()`, `useInterviewSession()`
- **Constants**: UPPER_SNAKE_CASE - `API_BASE_URL`, `MAX_FILE_SIZE`
- **Types/Interfaces**: PascalCase - `ButtonProps`, `InterviewSession`
- **Enums**: PascalCase - `InterviewStatus`, `UserRole`

**Props:**
- Prefix boolean props with `is`, `has`, `should` - `isLoading`, `hasError`, `shouldAutoFocus`
- Event handlers with `on` prefix - `onClick`, `onChange`, `onSubmit`

**Imports:**
- Use `@/` alias for absolute imports from `src/`
- Example: `import { Button } from '@/components/ui/Button'`

---
