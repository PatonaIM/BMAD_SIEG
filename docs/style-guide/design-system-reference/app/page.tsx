"use client"

import { ThemeProvider } from "@mui/material/styles"
import CssBaseline from "@mui/material/CssBaseline"
import { Box, Typography, Grid } from "@mui/material"
import { Send, CheckCircle, Warning, Error as ErrorIcon, ArrowForward } from "@mui/icons-material"
import { Button } from "@/components/teamified/Button"
import { Card } from "@/components/teamified/Card"
import { StatusBadge } from "@/components/teamified/StatusBadge"
import { Input } from "@/components/teamified/Input"
import { ProgressIndicator } from "@/components/teamified/ProgressIndicator"
import { teamifiedTheme } from "@/lib/theme"
import { useState } from "react"
import Link from "next/link"

export default function Home() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [bio, setBio] = useState("")

  return (
    <ThemeProvider theme={teamifiedTheme}>
      <CssBaseline />
      <Box sx={{ padding: 4, backgroundColor: "#FAFBFC", minHeight: "100vh" }}>
        {/* Navigation Section */}
        <Box
          sx={{
            marginBottom: 4,
            padding: 3,
            backgroundColor: "#FFFFFF",
            borderRadius: "12px",
            border: "2px solid #A16AE8",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 2,
          }}
        >
          <Box>
            <Typography variant="h6" sx={{ color: "#2C3E50", marginBottom: 0.5 }}>
              Ready to test your setup?
            </Typography>
            <Typography variant="body2" sx={{ color: "#7F8C8D" }}>
              Try the Pre-Interview System Check to test microphone and audio
            </Typography>
          </Box>
          <Link href="/pre-interview-check" style={{ textDecoration: "none" }}>
            <Button variant="primary" endIcon={<ArrowForward />}>
              Go to System Check
            </Button>
          </Link>
        </Box>

        <Typography variant="h3" sx={{ marginBottom: 4, color: "#2C3E50" }}>
          Teamified Design System
        </Typography>

        {/* Buttons Section */}
        <Card variant="default">
          <Typography variant="h5" sx={{ marginBottom: 3 }}>
            Buttons
          </Typography>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            <Button variant="primary">Primary Button</Button>
            <Button variant="secondary">Secondary Button</Button>
            <Button variant="danger">Danger Button</Button>
            <Button variant="ghost">Ghost Button</Button>
            <Button variant="primary" loading>
              Loading...
            </Button>
            <Button variant="primary" startIcon={<Send />}>
              With Icon
            </Button>
            <Button variant="primary" size="compact">
              Compact
            </Button>
          </Box>
        </Card>

        {/* Cards Section */}
        <Box sx={{ marginTop: 4 }}>
          <Typography variant="h5" sx={{ marginBottom: 3 }}>
            Cards
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card variant="default">
                <Typography variant="h6" sx={{ marginBottom: 1 }}>
                  Default Card
                </Typography>
                <Typography variant="body2" sx={{ color: "#7F8C8D" }}>
                  This is a standard card with subtle shadow.
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="interactive" onClick={() => alert("Card clicked!")}>
                <Typography variant="h6" sx={{ marginBottom: 1 }}>
                  Interactive Card
                </Typography>
                <Typography variant="body2" sx={{ color: "#7F8C8D" }}>
                  Click me! I have hover effects.
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="selected">
                <Typography variant="h6" sx={{ marginBottom: 1 }}>
                  Selected Card
                </Typography>
                <Typography variant="body2" sx={{ color: "#7F8C8D" }}>
                  This card is currently selected.
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Status Badges Section */}
        <Card variant="default" sx={{ marginTop: 4 }}>
          <Typography variant="h5" sx={{ marginBottom: 3 }}>
            Status Badges
          </Typography>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            <StatusBadge variant="success" icon={<CheckCircle />}>
              Completed
            </StatusBadge>
            <StatusBadge variant="warning" icon={<Warning />}>
              Pending
            </StatusBadge>
            <StatusBadge variant="error" icon={<ErrorIcon />}>
              Failed
            </StatusBadge>
            <StatusBadge variant="info">In Progress</StatusBadge>
          </Box>
        </Card>

        {/* Input Fields Section */}
        <Card variant="default" sx={{ marginTop: 4 }}>
          <Typography variant="h5" sx={{ marginBottom: 3 }}>
            Input Fields
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
            <Input
              variant="text"
              label="Email Address"
              placeholder="Enter your email"
              value={email}
              onChange={setEmail}
              required
              helpText="We'll never share your email"
            />
            <Input
              variant="password"
              label="Password"
              placeholder="Enter your password"
              value={password}
              onChange={setPassword}
              required
              error={password.length > 0 && password.length < 8 ? "Password must be at least 8 characters" : undefined}
            />
            <Input
              variant="textarea"
              label="Bio"
              placeholder="Tell us about yourself"
              value={bio}
              onChange={setBio}
              rows={4}
              helpText="Maximum 500 characters"
            />
          </Box>
        </Card>

        {/* Progress Indicators Section */}
        <Card variant="default" sx={{ marginTop: 4 }}>
          <Typography variant="h5" sx={{ marginBottom: 3 }}>
            Progress Indicators
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <Box>
              <Typography variant="body2" sx={{ marginBottom: 2, color: "#7F8C8D" }}>
                Linear Progress
              </Typography>
              <ProgressIndicator variant="linear" value={65} />
            </Box>
            <Box>
              <Typography variant="body2" sx={{ marginBottom: 2, color: "#7F8C8D" }}>
                Circular Progress
              </Typography>
              <Box sx={{ display: "flex", gap: 3, alignItems: "center" }}>
                <ProgressIndicator variant="circular" size="standard" />
                <ProgressIndicator variant="circular" size="small" />
              </Box>
            </Box>
            <Box>
              <Typography variant="body2" sx={{ marginBottom: 2, color: "#7F8C8D" }}>
                Stepper
              </Typography>
              <ProgressIndicator variant="stepper" steps={4} currentStep={2} />
            </Box>
          </Box>
        </Card>
      </Box>
    </ThemeProvider>
  )
}
