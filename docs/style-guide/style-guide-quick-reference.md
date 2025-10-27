# Style Guide Quick Reference

# Material-UI 3 Expressive Design - Quick Reference

## 🎨 Color Palette

### Brand Colors

```typescript

primary: '#A16AE8'    // Brand Purple

secondary: '#8096FD'  // Brand Blue
```

### Status Colors

```typescript

success: '#10B981'    // Green

warning: '#F59E0B'    // Orange

error: '#EF4444'      // Red

info: '#3B82F6'       // Blue
```

## 📝 Typography

### Headings

```typescript
<Typography variant="h1">Main Title (56px)</Typography>
<Typography variant="h2">Section Title (44px)</Typography>
<Typography variant="h3">Subsection (36px)</Typography>
<Typography variant="h4">Card Title (30px)</Typography>
<Typography variant="h5">Small Title (24px)</Typography>
<Typography variant="h6">Label (20px)</Typography>
```

### Body Text

```typescript
<Typography variant="body1">Regular text (16px)</Typography>
<Typography variant="body2">Small text (14px)</Typography>
<Typography variant="subtitle1">Medium text (18px)</Typography>
<Typography variant="caption">Caption (12px)</Typography>
```

## 🎯 Components

### Buttons

```typescript
// Primary Button
<Button variant="contained" color="primary">
  Primary Action
</Button>

// Secondary Button
<Button variant="outlined" color="secondary">
  Secondary Action
</Button>

// Text Button
<Button variant="text" color="primary">
  Text Action
</Button>
```

### Cards

```typescript
<Card sx={{ p: 3, mb: 2 }}>
  <CardContent>
    <Typography variant="h5" gutterBottom>
      Card Title
    </Typography>
    <Typography variant="body1">
      Card content
    </Typography>
  </CardContent>
</Card>
```

### Forms

```typescript
<TextField
  label="Field Label"
  variant="outlined"
  fullWidth
  required
  sx={{ mb: 2 }}
/>
```

## 📐 Spacing

### Spacing Scale (8px base)

```typescript

sx={{ p: 1 }}  // 8px padding

sx={{ p: 2 }}  // 16px padding

sx={{ p: 3 }}  // 24px padding

sx={{ p: 4 }}  // 32px padding

sx={{ m: 2 }}  // 16px margin

sx={{ mb: 3 }} // 24px margin bottom
```

### Common Spacing Patterns

```typescript
// Page padding

sx={{ p: 3 }}                    // 24px all around

// Card padding

sx={{ p: 3 }}                    // 24px all around

// Form field spacing

sx={{ mb: 2 }}                   // 16px bottom margin

// Section spacing

sx={{ mt: 4, mb: 4 }}           // 32px top and bottom
```

## 🎭 Layout

### Page Structure

```typescript

import { ThemeProvider } from '@mui/material/styles';
import { muiTheme } from '../theme/muiTheme';
import LayoutMUI from '../components/LayoutMUI';

const MyPage = () => {
  return (
    <ThemeProvider theme={muiTheme}>
      <LayoutMUI>
        {/* Page content */}
      </LayoutMUI>
    </ThemeProvider>
  );
};
```

### Responsive Breakpoints

```typescript
// Mobile first approach

sx={{ 
  display: { xs: 'block', md: 'flex' },
  flexDirection: { xs: 'column', md: 'row' }
}}
```

## 🎨 Styling Patterns

### Hover Effects

```typescript
// Button hover (built-in)
<Button variant="contained">Hover me</Button>

// Card hover (built-in)
<Card>Hover me</Card>

// Custom hover

sx={{
  '&:hover': {
    transform: 'scale(1.05)',
    backgroundColor: 'rgba(161, 106, 232, 0.08)'
  }
}}
```

### Color Usage

```typescript
// Text colors

color="primary"     // Brand purple

color="secondary"   // Brand blue

color="text.primary"    // Dark text

color="text.secondary"  // Light text

// Background colors

sx={{ bgcolor: 'primary.main' }}      // Brand purple

sx={{ bgcolor: 'secondary.main' }}    // Brand blue

sx={{ bgcolor: 'background.paper' }}  // White

sx={{ bgcolor: 'background.default' }} // Light gray
```

## ♿ Accessibility

### Required Attributes

```typescript
// Buttons
<Button aria-label="Close dialog">
  <CloseIcon />
</Button>

// Form fields
<TextField
  label="Email"
  aria-describedby="email-helper"
  required
/>
<Typography id="email-helper" variant="caption">
  We'll never share your email
</Typography>

// Images
<img src="..." alt="Descriptive text" />
```

### Focus Management

```typescript
// Focus visible (built-in)
<Button variant="contained">
  Focus me with keyboard
</Button>
```

## 📱 Responsive Design

### Common Patterns

```typescript
// Stack on mobile, row on desktop

sx={{
  display: 'flex',
  flexDirection: { xs: 'column', md: 'row' },
  gap: 2
}}

// Hide on mobile

sx={{ display: { xs: 'none', md: 'block' }}}

// Show only on mobile

sx={{ display: { xs: 'block', md: 'none' }}}
```

## 🚀 Quick Start Template

```typescript

import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField
} from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { muiTheme } from '../theme/muiTheme';
import LayoutMUI from '../components/LayoutMUI';

const MyPage = () => {
  return (
    <ThemeProvider theme={muiTheme}>
      <LayoutMUI>
        <Box sx={{ p: 3 }}>
          <Typography variant="h1" color="primary" gutterBottom>
            Page Title
          </Typography>
          
          <Card sx={{ p: 3, mb: 3 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Card Title
              </Typography>
              <TextField
                label="Input Field"
                variant="outlined"
                fullWidth
                sx={{ mb: 2 }}
              />
              <Button variant="contained" color="primary">
                Submit
              </Button>
            </CardContent>
          </Card>
        </Box>
      </LayoutMUI>
    </ThemeProvider>
  );
};

export default MyPage;
```

## 📚 Resources

* **Full Style Guide**: `docs/style-guide/material-ui-3-expressive-design.md`
* **Theme Config**: `frontend/src/theme/muiTheme.ts`
* **Layout Component**: `frontend/src/components/LayoutMUI.tsx`
* **Sidebar Component**: `frontend/src/components/SidebarMUI.tsx`

## 🎯 Best Practices


1. **Always use ThemeProvider** - Wrap components with muiTheme
2. **Use semantic HTML** - Proper heading hierarchy and form structure
3. **Include accessibility** - ARIA labels, keyboard support, focus management
4. **Test responsive** - Check all breakpoints (mobile, tablet, desktop)
5. **Follow spacing system** - Use 8px base unit consistently
6. **Use theme colors** - Don't hardcode colors, use theme.palette
7. **Leverage built-in animations** - Use Material-UI's smooth transitions

## 🎯 Established Design Patterns

### **Page Layout Patterns**

```typescript
// Header Section Pattern
<Paper elevation={0} sx={{ 
  p: 3, 
  mb: 4, 
  borderRadius: 3, 
  border: '1px solid #E5E7EB',
  background: 'linear-gradient(135deg, rgba(161, 106, 232, 0.05) 0%, rgba(128, 150, 253, 0.05) 100%)'
}}>
  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
    Page Title
  </Typography>
  <Typography variant="h6" sx={{ color: 'text.secondary' }}>
    Page description
  </Typography>
</Paper>

// Section Header Pattern
<Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
  Section Title
</Typography>
<Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
  Section description
</Typography>
```

### **Form Patterns**

```typescript
// Always-Visible Form Pattern
<Paper elevation={0} sx={{ p: 3, mb: 4, borderRadius: 3, border: '1px solid #E5E7EB' }}>
  <Box sx={{ mb: 3 }}>
    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
      Form Title
    </Typography>
    <Typography variant="body2" color="text.secondary">
      Form description
    </Typography>
  </Box>
  
  <Box>
    {/* Form content here - always visible */}
  </Box>
</Paper>
```

### **Button Patterns**

```typescript
// Primary Button Pattern
<Button
  variant="contained"
  sx={{
    borderRadius: 2,
    px: 3,
    py: 1.5,
    fontWeight: 600,
    textTransform: 'none',
    background: 'linear-gradient(135deg, #A16AE8 0%, #8096FD 100%)',
    boxShadow: '0 4px 15px rgba(161, 106, 232, 0.3)',
    '&:hover': {
      background: 'linear-gradient(135deg, #8B5AE8 0%, #6B86FD 100%)',
      boxShadow: '0 6px 20px rgba(161, 106, 232, 0.4)',
    },
  }}
>
  Primary Action
</Button>

// Secondary Button Pattern
<Button
  variant="outlined"
  sx={{
    borderRadius: 2,
    px: 3,
    py: 1.5,
    fontWeight: 600,
    textTransform: 'none',
    borderColor: 'rgba(161, 106, 232, 0.5)',
    color: 'primary.main',
    '&:hover': {
      borderColor: 'primary.main',
      backgroundColor: 'rgba(161, 106, 232, 0.04)',
      boxShadow: '0 2px 8px rgba(161, 106, 232, 0.2)',
    },
  }}
>
  Secondary Action
</Button>

// Text Button Pattern
<Button
  variant="text"
  sx={{
    textTransform: 'none',
    p: 1,
    minWidth: 'auto',
    fontWeight: 600,
    borderRadius: 1,
    '&:hover': {
      backgroundColor: 'rgba(161, 106, 232, 0.08)',
      transform: 'translateY(-1px)',
    },
  }}
>
  Text Link
</Button>
```

### **Typography Hierarchy**

```typescript
// Page Header
<Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
  Page Title
</Typography>

// Section Header
<Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
  Section Title
</Typography>

// Description Text
<Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
  Description text
</Typography>

// Content Header
<Typography variant="h6" sx={{ fontWeight: 600 }}>
  Content Title
</Typography>

// Body Text
<Typography variant="body2" color="text.secondary">
  Body text content
</Typography>
```

### **Form Reset Pattern**

```typescript
// Cancel Button with Reset Functionality
<Button
  variant="outlined"
  onClick={() => setFormData({
    field1: '',
    field2: '',
    field3: ''
  })}
  sx={{
    // ... secondary button styling
  }}
>
  Cancel
</Button>
```