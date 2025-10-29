import { Box, Container, Typography, Button } from '@mui/material';
import { useAuthStore } from '../features/auth/store/authStore';
import { useLogout } from '../features/auth/hooks/useAuth';

const InterviewStartPage = () => {
  const user = useAuthStore((state) => state.user);
  const logout = useLogout();

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
        }}
      >
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Your Interview
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
          Hello, {user?.email || 'Candidate'}!
        </Typography>
        <Typography variant="body1" sx={{ mb: 4 }}>
          You're all set to begin your interview. This page will be further developed in the next story.
        </Typography>
        <Button variant="outlined" onClick={logout}>
          Sign Out
        </Button>
      </Box>
    </Container>
  );
};

export default InterviewStartPage;
