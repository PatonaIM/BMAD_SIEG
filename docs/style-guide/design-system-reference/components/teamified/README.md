# Teamified Design System

A professional design system for the Teamified Candidates Portal, built with React 18+, TypeScript, and Material-UI v3.

## Installation

This design system requires the following dependencies:

\`\`\`bash
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
\`\`\`

## Setup

### 1. Apply the Theme

Wrap your application with the `ThemeProvider` and apply the Teamified theme:

\`\`\`tsx
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { teamifiedTheme } from './lib/theme';

function App() {
  return (
    <ThemeProvider theme={teamifiedTheme}>
      <CssBaseline />
      {/* Your app content */}
    </ThemeProvider>
  );
}
\`\`\`

### 2. Import Components

\`\`\`tsx
import { Button, Card, StatusBadge, Input, ProgressIndicator } from './components/teamified';
\`\`\`

## Components

### Button

A versatile button component with multiple variants and states.

**Variants:** `primary`, `secondary`, `danger`, `ghost`  
**Sizes:** `standard` (44px), `compact` (36px)

\`\`\`tsx
import { Button } from './components/teamified';
import { Send } from '@mui/icons-material';

// Primary button
<Button variant="primary" onClick={() => console.log('Clicked')}>
  Submit Application
</Button>

// Secondary button with icon
<Button variant="secondary" startIcon={<Send />}>
  Send Message
</Button>

// Loading state
<Button variant="primary" loading>
  Processing...
</Button>

// Danger button
<Button variant="danger" onClick={handleDelete}>
  Delete Account
</Button>

// Ghost button
<Button variant="ghost">
  Cancel
</Button>
\`\`\`

### Card

A flexible card container with interactive and selected states.

**Variants:** `default`, `interactive`, `selected`

\`\`\`tsx
import { Card } from './components/teamified';

// Default card
<Card>
  <h3>Interview Details</h3>
  <p>Your interview is scheduled for tomorrow at 2 PM.</p>
</Card>

// Interactive card (clickable)
<Card variant="interactive" onClick={() => console.log('Card clicked')}>
  <h3>View Profile</h3>
</Card>

// Selected card
<Card variant="selected">
  <h3>Active Interview</h3>
</Card>
\`\`\`

### StatusBadge

A pill-shaped badge for displaying status information.

**Variants:** `success`, `warning`, `error`, `info`

\`\`\`tsx
import { StatusBadge } from './components/teamified';
import { CheckCircle, Warning } from '@mui/icons-material';

// Success badge
<StatusBadge variant="success" icon={<CheckCircle />}>
  Completed
</StatusBadge>

// Warning badge
<StatusBadge variant="warning" icon={<Warning />}>
  Pending Review
</StatusBadge>

// Error badge
<StatusBadge variant="error">
  Failed
</StatusBadge>

// Info badge
<StatusBadge variant="info">
  In Progress
</StatusBadge>
\`\`\`

### Input

A comprehensive input component with text, textarea, and password variants.

**Variants:** `text`, `textarea`, `password`

\`\`\`tsx
import { Input } from './components/teamified';
import { useState } from 'react';

function MyForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [bio, setBio] = useState('');

  return (
    <>
      {/* Text input */}
      <Input
        variant="text"
        label="Email Address"
        placeholder="Enter your email"
        value={email}
        onChange={setEmail}
        required
        helpText="We'll never share your email"
      />

      {/* Password input with show/hide toggle */}
      <Input
        variant="password"
        label="Password"
        placeholder="Enter your password"
        value={password}
        onChange={setPassword}
        required
        error={password.length < 8 ? 'Password must be at least 8 characters' : undefined}
      />

      {/* Textarea */}
      <Input
        variant="textarea"
        label="Bio"
        placeholder="Tell us about yourself"
        value={bio}
        onChange={setBio}
        rows={6}
        helpText="Maximum 500 characters"
      />
    </>
  );
}
\`\`\`

### ProgressIndicator

A multi-purpose progress component with linear, circular, and stepper variants.

**Variants:** `linear`, `circular`, `stepper`

\`\`\`tsx
import { ProgressIndicator } from './components/teamified';

// Linear progress bar
<ProgressIndicator variant="linear" value={65} />

// Circular spinner (standard size)
<ProgressIndicator variant="circular" size="standard" />

// Small circular spinner
<ProgressIndicator variant="circular" size="small" />

// Stepper (e.g., multi-step form)
<ProgressIndicator 
  variant="stepper" 
  steps={4} 
  currentStep={2} 
/>
\`\`\`

## Design Tokens

### Colors

- **Primary:** `#A16AE8` (Brand Purple)
- **Success:** `#1DD1A1` (Teal)
- **Warning:** `#FFA502` (Orange)
- **Error:** `#EF4444` (Red)
- **Info:** `#3B82F6` (Blue)
- **Text Primary:** `#2C3E50` (Dark Gray)
- **Text Secondary:** `#7F8C8D` (Medium Gray)
- **Border:** `#E0E4E8` (Light Gray)
- **Background:** `#FAFBFC` (Off-white)

### Typography

- **Font Family:** Plus Jakarta Sans, Inter, system fonts
- **Font Weights:** 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Spacing

Based on 8px baseline grid. Use MUI's `theme.spacing()` function:
- `theme.spacing(1)` = 8px
- `theme.spacing(2)` = 16px
- `theme.spacing(3)` = 24px

### Border Radius

- **Small (badges):** 16px
- **Medium (buttons/inputs):** 8px
- **Large (cards):** 12px

## Accessibility

All components follow WCAG 2.1 AA guidelines:
- Minimum 44x44px touch targets
- Proper ARIA labels and roles
- Keyboard navigation support
- 4.5:1 color contrast ratios
- Focus indicators

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
