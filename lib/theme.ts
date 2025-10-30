import { createTheme } from "@mui/material/styles"

/**
 * Teamified Design System Theme
 * Migrated from frontend/src/theme/theme.ts
 */
export const teamifiedTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#A16AE8", // Brand Purple
      contrastText: "#FFFFFF",
    },
    success: {
      main: "#1DD1A1", // Teal
      contrastText: "#FFFFFF",
    },
    error: {
      main: "#EF4444", // Red
      contrastText: "#FFFFFF",
    },
    warning: {
      main: "#FFA502", // Orange
      contrastText: "#FFFFFF",
    },
    text: {
      primary: "#2C3E50", // Grey Dark
      secondary: "#6B7280",
    },
    background: {
      default: "#F5F6F7", // Background
      paper: "#FFFFFF",
    },
    grey: {
      100: "#F5F6F7",
      200: "#E0E4E8", // Grey Light
      300: "#CBD5E0",
      400: "#A0AEC0",
      500: "#718096",
      600: "#4A5568",
      700: "#2D3748",
      800: "#2C3E50", // Grey Dark
      900: "#1A202C",
    },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", "Segoe UI", "Roboto", sans-serif',
    fontSize: 16,
    h1: {
      fontSize: "3.5rem", // 56px
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: "2.75rem", // 44px
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h3: {
      fontSize: "2.25rem", // 36px
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h4: {
      fontSize: "1.875rem", // 30px
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h5: {
      fontSize: "1.5rem", // 24px
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h6: {
      fontSize: "1.25rem", // 20px
      fontWeight: 600,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: "1rem", // 16px
      lineHeight: 1.5,
    },
    body2: {
      fontSize: "0.875rem", // 14px
      lineHeight: 1.5,
    },
    caption: {
      fontSize: "0.75rem", // 12px
      lineHeight: 1.4,
    },
  },
  spacing: 8, // Base unit: 8px
  shape: {
    borderRadius: 8, // Default border radius
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: "none",
          fontWeight: 600,
          padding: "10px 20px",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 8,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
        },
      },
    },
  },
})
