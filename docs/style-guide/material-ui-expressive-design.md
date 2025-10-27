# Material UI Expressive Design

# Material-UI 3 Expressive Design System

## Overview

This document defines the Material-UI 3 Expressive Design system for the Teamified Portal. This design system emphasizes bold simplicity, intuitive navigation, and accessibility-driven design while maintaining a professional and modern aesthetic.

## Design Principles

### Core Principles

* **Bold Simplicity**: Clean, uncluttered interfaces with purposeful elements
* **Intuitive Navigation**: Clear information hierarchy and logical user flows
* **Accessibility-First**: WCAG 2.1 AA compliant design with inclusive practices
* **Expressive Design**: Dynamic typography, generous spacing, and thoughtful micro-interactions
* **Brand Consistency**: Unified visual language across all touchpoints

### Material-UI 3 Expressive Characteristics

* **Generous Spacing**: 8px base unit with breathing room between elements
* **Rounded Corners**: 16px+ border radius for modern, friendly appearance
* **Layered Shadows**: Subtle depth and elevation for visual hierarchy
* **Dynamic Typography**: Expressive font sizes and weights for better readability
* **Smooth Animations**: 0.2s cubic-bezier transitions for polished interactions

## Color System

### Brand Colors

```typescript
// Primary Brand Colors

primary: {
  main: '#A16AE8',    // Brand Purple
  light: '#C4A5F0',   // Light Purple
  dark: '#7B3FD6',    // Dark Purple
  contrastText: '#FFFFFF'
}

secondary: {
  main: '#8096FD',    // Brand Blue
  light: '#A3B2FE',   // Light Blue
  dark: '#5A7AFC',    // Dark Blue
  contrastText: '#FFFFFF'
}
```

### Semantic Colors

```typescript
// Status Colors

success: {
  main: '#10B981',    // Success Green
  light: '#34D399',
  dark: '#059669'
}

warning: {
  main: '#F59E0B',    // Warning Orange
  light: '#FBBF24',
  dark: '#D97706'
}

error: {
  main: '#EF4444',    // Error Red
  light: '#F87171',
  dark: '#DC2626'
}

info: {
  main: '#3B82F6',    // Info Blue
  light: '#60A5FA',
  dark: '#2563EB'
}
```

### Neutral Colors

```typescript
// Gray Scale

grey: {
  50: '#FAFBFC',      // Background
  100: '#F4F6F8',     // Light Background
  200: '#E8EBF0',     // Border Light
  300: '#D1D7E0',     // Border
  400: '#9AA0AC',     // Placeholder
  500: '#6B7280',     // Text Secondary
  600: '#4B5563',     // Text
  700: '#374151',     // Text Primary
  800: '#1F2937',     // Text Dark
  900: '#111827'      // Text Darkest
}

// Background Colors

background: {
  default: '#FAFBFC', // Page Background
  paper: '#FFFFFF'    // Card/Paper Background
}

// Text Colors

text: {
  primary: '#1A1A1A',   // Primary Text
  secondary: '#5A5A5A'  // Secondary Text
}
```

## Typography

### Font Family

```typescript

fontFamily: '"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
```

### Type Scale

```typescript
// Headings

h1: {
  fontSize: '3.5rem',    // 56px
  lineHeight: 1.1,
  fontWeight: 700,
  letterSpacing: '-0.02em'
}

h2: {
  fontSize: '2.75rem',   // 44px
  lineHeight: 1.2,
  fontWeight: 600,
  letterSpacing: '-0.01em'
}

h3: {
  fontSize: '2.25rem',   // 36px
  lineHeight: 1.25,
  fontWeight: 600,
  letterSpacing: '-0.01em'
}

h4: {
  fontSize: '1.875rem',  // 30px
  lineHeight: 1.3,
  fontWeight: 600
}

h5: {
  fontSize: '1.5rem',    // 24px
  lineHeight: 1.35,
  fontWeight: 600
}

h6: {
  fontSize: '1.25rem',   // 20px
  lineHeight: 1.4,
  fontWeight: 600
}

// Body Text

body1: {
  fontSize: '1rem',      // 16px
  lineHeight: 1.6,
  fontWeight: 400
}

body2: {
  fontSize: '0.875rem',  // 14px
  lineHeight: 1.5,
  fontWeight: 400
}

// Specialized Text

subtitle1: {
  fontSize: '1.125rem',  // 18px
  lineHeight: 1.5,
  fontWeight: 500
}

subtitle2: {
  fontSize: '1rem',      // 16px
  lineHeight: 1.5,
  fontWeight: 500
}

caption: {
  fontSize: '0.75rem',   // 12px
  lineHeight: 1.4,
  fontWeight: 500
}

overline: {
  fontSize: '0.75rem',   // 12px
  lineHeight: 1.4,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.1em'
}
```

## Spacing System

### Base Unit

* **Base Unit**: 8px
* **Spacing Scale**: Multiples of 8px (8, 16, 24, 32, 40, 48, 56, 64, 72, 80)

### Common Spacing Values

```typescript
// Component Spacing

xs: 4,    // 4px - Tight spacing

sm: 8,    // 8px - Small spacing

md: 16,   // 16px - Medium spacing

lg: 24,   // 24px - Large spacing

xl: 32,   // 32px - Extra large spacing

xxl: 48,  // 48px - Section spacing

xxxl: 64, // 64px - Page spacing
```

### Layout Spacing

* **Page Margins**: 24px (mobile), 32px (tablet), 48px (desktop)
* **Card Padding**: 24px
* **Form Field Spacing**: 16px vertical
* **Button Padding**: 14px vertical, 28px horizontal

## Border Radius

### Radius Scale

```typescript
// Component Border Radius

shape: {
  borderRadius: 16  // Base radius for most components
}

// Specific Component Radius

Button: 16px

TextField: 16px

Card: 20px

Dialog: 24px

Menu: 16px

TableContainer: 16px

Chip: 12px

IconButton: 12px
```

## Shadows & Elevation

### Shadow System

```typescript
// Elevation Levels

elevation1: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
elevation2: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
elevation3: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'

// Special Shadows

dialog: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
buttonHover: '0 8px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
cardHover: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
```

## Component Specifications

### Buttons

#### Primary Button

```typescript
// Styling

borderRadius: 16px

padding: '14px 28px'
fontSize: '0.875rem'
fontWeight: 600

textTransform: 'none'
boxShadow: 'none'

// Hover Effects

transform: 'translateY(-1px)'
boxShadow: '0 8px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'

// Sizes

sizeLarge: '16px 32px', fontSize: '1rem'
sizeSmall: '10px 20px', fontSize: '0.75rem'
```

#### Outlined Button

```typescript

borderWidth: '2px'
// Hover maintains 2px border width
```

### Text Fields

#### Input Styling

```typescript

borderRadius: 16px

transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'

// Hover State

borderColor: '#A16AE8'
borderWidth: '2px'

// Focus State

borderColor: '#A16AE8'
borderWidth: '2px'
boxShadow: '0 0 0 3px rgba(161, 106, 232, 0.1)'
```

### Cards

#### Card Styling

```typescript

borderRadius: 20px

boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'

// Hover Effect

transform: 'translateY(-2px)'
boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
```

### Chips

#### Chip Styling

```typescript

borderRadius: 12px

fontWeight: 500
```

### Icon Buttons

#### Icon Button Styling

```typescript

borderRadius: 12px

transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'

// Hover Effect

transform: 'scale(1.05)'
backgroundColor: 'rgba(161, 106, 232, 0.08)'
```

## Layout System

### LayoutMUI Component

```typescript
// Main Layout Wrapper
<ThemeProvider theme={muiTheme}>
  <Box sx={{ display: 'flex', height: '100vh' }}>
    <SidebarMUI />
    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      <AppBar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        {children}
      </Box>
    </Box>
  </Box>
</ThemeProvider>
```

### SidebarMUI Component

```typescript
// Sidebar Specifications

width: 280px (expanded)
width: 72px (collapsed)
transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)'

// Mobile Behavior

drawer: true (mobile)
persistent: true (desktop)
```

### Responsive Breakpoints

```typescript
// Material-UI Breakpoints

xs: 0px      // Extra small devices

sm: 600px    // Small devices

md: 900px    // Medium devices

lg: 1200px   // Large devices

xl: 1536px   // Extra large devices

// Custom Breakpoints

mobile: 'lg' // Below 1200px is considered mobile
```

## Animation & Transitions

### Transition Timing

```typescript
// Standard Transition

transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'

// Hover Transitions

buttonHover: '0.2s cubic-bezier(0.4, 0, 0.2, 1)'
cardHover: '0.2s cubic-bezier(0.4, 0, 0.2, 1)'
sidebarTransition: '0.3s cubic-bezier(0.4, 0, 0.2, 1)'
```

### Transform Effects

```typescript
// Button Hover

transform: 'translateY(-1px)'

// Card Hover

transform: 'translateY(-2px)'

// Icon Button Hover

transform: 'scale(1.05)'
```

## Accessibility Standards

### WCAG 2.1 AA Compliance

* **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
* **Focus Indicators**: Clear focus states for all interactive elements
* **Keyboard Navigation**: Full keyboard accessibility
* **Screen Reader Support**: Proper ARIA labels and semantic HTML

### Accessibility Features

```typescript
// Focus Management

focusVisible: true

focusRipple: true

// ARIA Support

ariaLabel: 'descriptive label'
ariaDescribedBy: 'helper text id'
role: 'button' | 'link' | 'tab' | etc.

// Color Contrast
// All color combinations meet WCAG AA standards
```

## Usage Guidelines

### Component Usage


1. **Always use ThemeProvider**: Wrap all components with the muiTheme
2. **Consistent Spacing**: Use the 8px spacing system
3. **Proper Typography**: Use semantic heading levels and appropriate variants
4. **Accessibility First**: Include proper ARIA labels and keyboard support
5. **Responsive Design**: Test on all breakpoints

### Code Examples

#### Basic Page Structure

```typescript

import { ThemeProvider } from '@mui/material/styles';
import { muiTheme } from '../theme/muiTheme';
import LayoutMUI from '../components/LayoutMUI';

const MyPage = () => {
  return (
    <ThemeProvider theme={muiTheme}>
      <LayoutMUI>
        <Typography variant="h1" color="primary">
          Page Title
        </Typography>
        <Card sx={{ p: 3, mt: 2 }}>
          <Typography variant="body1">
            Page content goes here
          </Typography>
        </Card>
      </LayoutMUI>
    </ThemeProvider>
  );
};
```

#### Button Usage

```typescript
// Primary Button
<Button variant="contained" color="primary" size="large">
  Primary Action
</Button>

// Outlined Button
<Button variant="outlined" color="secondary">
  Secondary Action
</Button>

// Text Button
<Button variant="text" color="primary">
  Text Action
</Button>
```

#### Form Usage

```typescript
<TextField
  label="Email Address"
  type="email"
  variant="outlined"
  fullWidth
  required
  sx={{ mb: 2 }}
/>
```


## File References

### Theme Configuration

* `frontend/src/theme/muiTheme.ts` - Complete theme configuration

### Layout Components

* `frontend/src/components/LayoutMUI.tsx` - Main layout wrapper
* `frontend/src/components/SidebarMUI.tsx` - Sidebar navigation

### Example Implementations

* `frontend/src/pages/ProfilePage.tsx` - Profile page implementation
* `frontend/src/pages/DashboardPageMUI.tsx` - Dashboard implementation
* `frontend/src/pages/EmploymentRecordsPage.tsx` - Employment records implementation