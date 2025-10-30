import type React from "react"
import type { Metadata } from "next"
import { Plus_Jakarta_Sans } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { ThemeProvider } from "@/components/theme-provider"
import { Navigation } from "@/components/navigation"
import "./globals.css"

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
})

export const metadata: Metadata = {
  title: "Teamified - AI-Powered Recruitment Platform",
  description: "Transform your hiring with AI-driven technical interviews and smart job matching",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${plusJakartaSans.variable} font-sans antialiased`}>
        <ThemeProvider defaultTheme="system" storageKey="teamified-theme">
          <Navigation />
          {children}
          <Analytics />
        </ThemeProvider>
      </body>
    </html>
  )
}
