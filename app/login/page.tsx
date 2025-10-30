import { Box, Container, Paper } from "@mui/material"
import { LoginForm } from "@/components/auth/login-form"

export default function LoginPage() {
  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <LoginForm />
        </Paper>
      </Box>
    </Container>
  )
}
