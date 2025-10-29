import { createTheme, type ThemeOptions } from "@mui/material/styles"

// Extend MUI theme to include custom shadow types
declare module "@mui/material/styles" {
  interface Theme {
    shadows: {
      cardDefault: string
      cardHover: string
      level1: string
      level2: string
      level3: string
      dialog: string
    } & string[]
  }
  interface ThemeOptions {
    shadows?: Partial<{
      cardDefault: string
      cardHover: string
      level1: string
      level2: string
      level3: string
      dialog: string
    }> &
      Partial<string[]>
  }
}

const themeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: "#A16AE8",
      light: "#E8E5F5",
      dark: "#7B3FD6",
      contrastText: "#FFFFFF",
    },
    success: {
      main: "#1DD1A1",
      light: "#D4F5EE",
      contrastText: "#FFFFFF",
    },
    warning: {
      main: "#FFA502",
      contrastText: "#FFFFFF",
    },
    error: {
      main: "#EF4444",
      contrastText: "#FFFFFF",
    },
    info: {
      main: "#3B82F6",
      contrastText: "#FFFFFF",
    },
    grey: {
      900: "#2C3E50",
      700: "#7F8C8D",
      300: "#E0E4E8",
      100: "#F5F6F7",
      50: "#FAFBFC",
    },
    background: {
      default: "#FAFBFC",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#2C3E50",
      secondary: "#7F8C8D",
    },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: {
      fontSize: "56px",
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: "44px",
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h3: {
      fontSize: "36px",
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h4: {
      fontSize: "30px",
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h5: {
      fontSize: "24px",
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h6: {
      fontSize: "20px",
      fontWeight: 600,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: "16px",
      fontWeight: 400,
      lineHeight: 1.5,
    },
    body2: {
      fontSize: "14px",
      fontWeight: 400,
      lineHeight: 1.5,
    },
    caption: {
      fontSize: "12px",
      fontWeight: 400,
      lineHeight: 1.4,
    },
    button: {
      fontSize: "14px",
      fontWeight: 500,
      textTransform: "none",
    },
  },
  spacing: 8, // 8px baseline
  shape: {
    borderRadius: 8, // Default medium border radius
  },
  shadows: {
    cardDefault: "0 2px 8px rgba(0, 0, 0, 0.04)",
    cardHover: "0 4px 16px rgba(0, 0, 0, 0.08)",
    level1: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    level2: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    level3: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    dialog: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
  } as any,
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "8px",
          textTransform: "none",
          fontWeight: 500,
          fontSize: "14px",
          padding: "12px 24px",
          minHeight: "44px",
          transition: "all 150ms cubic-bezier(0.4, 0.0, 0.2, 1)",
          "&:active": {
            transform: "scale(0.95)",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: "12px",
          border: "1px solid #E0E4E8",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: "8px",
            "& fieldset": {
              borderColor: "#E0E4E8",
            },
            "&:hover fieldset": {
              borderColor: "#A16AE8",
            },
            "&.Mui-focused fieldset": {
              borderWidth: "2px",
              borderColor: "#A16AE8",
            },
            "&.Mui-error fieldset": {
              borderWidth: "2px",
              borderColor: "#EF4444",
            },
          },
        },
      },
    },
  },
}

export const teamifiedTheme = createTheme(themeOptions)
