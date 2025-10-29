import { Box, Container, Typography, Button, CircularProgress } from '@mui/material';
import { useAuthStore } from '../features/auth/store/authStore';
import { useLogout } from '../features/auth/hooks/useAuth';
import { useStartInterview } from '../features/interview/hooks/useInterview';

const InterviewStartPage = () => {
  const user = useAuthStore((state) => state.user);
  const logout = useLogout();
  const { mutate: startInterview, isPending, isError, error } = useStartInterview();

  const handleBeginInterview = () => {
    // Call backend API to start interview
    startInterview({
      role_type: 'react', // TODO: Let user select role type
      resume_id: null,
    });
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
        
        {isError && (
          <Typography color="error" sx={{ mb: 2 }}>
            Failed to start interview: {error?.message || 'Unknown error'}
          </Typography>
        )}
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            size="large"
            onClick={handleBeginInterview}
            disabled={isPending}
            sx={{ minWidth: 200 }}
          >
            {isPending ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Starting...
              </>
            ) : (
              'Begin Interview'
            )}
          </Button>
          <Button variant="outlined" onClick={logout} disabled={isPending}>
            Sign Out
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default InterviewStartPage;
