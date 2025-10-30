import { createTheme } from "@mui/material/styles"

export const teamifiedTheme = createTheme({
  palette: {
    primary: {
      main: "#A16AE8", // Brand Purple
      light: "#E8E5F5", // Light Purple
      dark: "#7B3FD6", // Dark Purple
      contrastText: "#FFFFFF",
    },
    success: {
      main: "#1DD1A1", // Success Teal
      light: "#D4F5EE", // Success Light
      contrastText: "#FFFFFF",
    },
    warning: {
      main: "#FFA502", // Warning Orange
      contrastText: "#FFFFFF",
    },
    error: {
      main: "#EF4444", // Error Red
      contrastText: "#FFFFFF",
    },
    info: {
      main: "#3B82F6", // Info Blue
      contrastText: "#FFFFFF",
    },
    grey: {
      900: "#2C3E50", // Dark Gray (text)
      700: "#7F8C8D", // Medium Gray (secondary text)
      300: "#E0E4E8", // Border Gray
      100: "#F5F6F7", // Light Gray (backgrounds)
      50: "#FAFBFC", // Background
    },
    background: {
      default: "#FAFBFC",
      paper: "#FFFFFF",
    },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: {
      fontSize: "56px",
      fontWeight: 700,
    },
    h2: {
      fontSize: "44px",
      fontWeight: 700,
    },
    h3: {
      fontSize: "36px",
      fontWeight: 600,
    },
    h4: {
      fontSize: "30px",
      fontWeight: 600,
    },
    h5: {
      fontSize: "24px",
      fontWeight: 600,
    },
    h6: {
      fontSize: "20px",
      fontWeight: 600,
    },
    body1: {
      fontSize: "16px",
      fontWeight: 400,
    },
    body2: {
      fontSize: "14px",
      fontWeight: 400,
    },
    caption: {
      fontSize: "12px",
      fontWeight: 400,
    },
  },
  spacing: 8,
  shape: {
    borderRadius: 8,
  },
  shadows: [
    "none",
    "0 2px 8px rgba(0, 0, 0, 0.04)", // cardDefault
    "0 4px 16px rgba(0, 0, 0, 0.08)", // cardHover
    "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)", // level1
    "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)", // level2
    "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)", // level3
    "0 25px 50px -12px rgba(0, 0, 0, 0.25)", // dialog
    ...Array(18).fill("none"),
  ] as any,
})
