/**
 * Teamified Design System Theme
 * Purple-based color palette with teal accents
 * WCAG AAA compliant for accessibility
 *
 * Theme is now implemented via Tailwind CSS design tokens in app/globals.css
 * This file is kept for reference but is no longer used.
 *
 * Color Palette:
 * - Primary (Purple): #A16AE8
 * - Success (Teal): #1DD1A1
 * - Error (Red): #EF4444
 * - Warning (Orange): #FFA502
 * - Text Primary: #2C3E50
 * - Text Secondary: #6B7280
 * - Background: #FAFAFA
 *
 * All colors are defined as CSS custom properties in globals.css
 * and can be used via Tailwind utility classes (e.g., bg-primary, text-foreground)
 */

export const themeColors = {
  primary: "#A16AE8",
  success: "#1DD1A1",
  error: "#EF4444",
  warning: "#FFA502",
  textPrimary: "#2C3E50",
  textSecondary: "#6B7280",
  background: "#FAFAFA",
} as const
