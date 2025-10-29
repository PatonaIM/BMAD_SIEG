import { Box, Container, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../features/auth/store/authStore';
import { useLogout } from '../features/auth/hooks/useAuth';

const InterviewStartPage = () => {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useLogout();

  const handleBeginInterview = () => {
    // Generate a test session ID for now
    // In Story 1.7, this will come from the backend
    const sessionId = `session-${Date.now()}`;
    navigate(`/interview/${sessionId}`);
  };

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
          Ready to begin? Click the button below to start your AI-powered technical interview.
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            size="large"
            onClick={handleBeginInterview}
            sx={{ minWidth: 200 }}
          >
            Begin Interview
          </Button>
          <Button variant="outlined" onClick={logout}>
            Sign Out
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default InterviewStartPage;
