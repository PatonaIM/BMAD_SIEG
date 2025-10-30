# 8. Styling Guidelines

## 8.1 MUI Theme Configuration

\`\`\`typescript
// src/theme/theme.ts (from design system)
import { createTheme } from '@mui/material/styles';

export const teamifiedTheme = createTheme({
  palette: {
    primary: {
      main: '#A16AE8',
      light: '#E8E5F5',
      dark: '#7B3FD6',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#1DD1A1',
      light: '#D4F5EE',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#FFA502',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#EF4444',
      contrastText: '#FFFFFF',
    },
    grey: {
      900: '#2C3E50',
      700: '#7F8C8D',
      300: '#E0E4E8',
      100: '#F5F6F7',
      50: '#FAFBFC',
    },
    background: {
      default: '#FAFBFC',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", sans-serif',
    h1: { fontSize: '56px', fontWeight: 700 },
    h2: { fontSize: '44px', fontWeight: 700 },
    h3: { fontSize: '36px', fontWeight: 600 },
    h4: { fontSize: '30px', fontWeight: 600 },
    h5: { fontSize: '24px', fontWeight: 600 },
    h6: { fontSize: '20px', fontWeight: 600 },
    body1: { fontSize: '16px', fontWeight: 400 },
    body2: { fontSize: '14px', fontWeight: 400 },
  },
  spacing: 8,
  shape: {
    borderRadius: 8,
  },
});
\`\`\`

## 8.2 Styling Patterns

**Using sx Prop (Recommended for inline styling):**
\`\`\`typescript
<Box
  sx={{
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    p: 4,
    bgcolor: 'background.paper',
    borderRadius: 2,
    boxShadow: 1,
  }}
>
  <Typography variant="h5" sx={{ color: 'primary.main', mb: 2 }}>
    Title
  </Typography>
</Box>
\`\`\`

**Using Styled Components (For reusable styled elements):**
\`\`\`typescript
import { styled } from '@mui/material/styles';
import { Box } from '@mui/material';

const StyledCard = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[1],
  
  '&:hover': {
    boxShadow: theme.shadows[2],
  },
}));
\`\`\`

## 8.3 CSS Custom Properties

\`\`\`css
/* src/styles/variables.css */
:root {
  /* Colors from MUI theme */
  --color-primary: #A16AE8;
  --color-success: #1DD1A1;
  --color-error: #EF4444;
  --color-warning: #FFA502;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Border radius */
  --border-radius: 8px;
  
  /* Transitions */
  --transition-fast: 150ms;
  --transition-normal: 250ms;
  --transition-slow: 400ms;
  
  /* Z-index layers */
  --z-index-dropdown: 1000;
  --z-index-modal: 1300;
  --z-index-tooltip: 1500;
}
\`\`\`

---
